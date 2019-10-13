from __future__ import print_function, unicode_literals

import json
import logging
import os
import platform
import sys
from copy import deepcopy
from typing import Any, Callable

import attr
from pathlib2 import Path
from pyhocon import ConfigFactory, HOCONConverter, ConfigTree

from trains_agent.backend_api.session import Session as _Session, Request
from trains_agent.backend_api.session.client import APIClient
from trains_agent.backend_config.defs import LOCAL_CONFIG_FILE_OVERRIDE_VAR, LOCAL_CONFIG_FILES
from trains_agent.definitions import ENVIRONMENT_CONFIG
from trains_agent.errors import APIError
from trains_agent.helper.base import HOCONEncoder
from trains_agent.helper.process import Argv
from .version import __version__

POETRY = "poetry"


@attr.s
class ConfigValue(object):

    """
    Manages a single config key
    """

    config = attr.ib(type=ConfigTree)
    key = attr.ib(type=str)

    def get(self, default=None):
        """
        Get value of key with default
        """
        return self.config.get(self.key, default=default)

    def set(self, value):
        """
        Change the value of key
        """
        self.config.put(self.key, value)

    def modify(self, fn):
        # type: (Callable[[Any], Any]) -> ()
        """
        Change the value of a key using a function
        """
        self.set(fn(self.get()))


def tree(*args):
    """
    Helper function for creating config trees
    """
    return ConfigTree(args)


class Session(_Session):
    version = __version__

    def __init__(self, *args, **kwargs):
        # make sure we set the environment variable so the parent session opens the correct file
        if kwargs.get('config_file'):
            config_file = Path(os.path.expandvars(kwargs.get('config_file'))).expanduser().absolute().as_posix()
            kwargs['config_file'] = config_file
            os.environ[LOCAL_CONFIG_FILE_OVERRIDE_VAR] = config_file
            if not Path(config_file).is_file():
                raise ValueError("Could not open configuration file: {}".format(config_file))
        super(Session, self).__init__(*args, **kwargs)
        self.log = self.get_logger(__name__)
        self.trace = kwargs.get('trace', False)
        self._config_file = kwargs.get('config_file') or \
                            os.environ.get(LOCAL_CONFIG_FILE_OVERRIDE_VAR) or LOCAL_CONFIG_FILES[0]
        self.api_client = APIClient(session=self, api_version="2.3")
        # HACK make sure we have python version to execute,
        # if nothing was specific, use the one that runs us
        def_python = ConfigValue(self.config, "agent.default_python")
        if not def_python.get():
            def_python.set("{version.major}.{version.minor}".format(version=sys.version_info))

        # HACK: backwards compatibility
        os.environ['ALG_CONFIG_FILE'] = self._config_file
        os.environ['SM_CONFIG_FILE'] = self._config_file
        if not self.config.get('api.host', None) and self.config.get('api.api_server', None):
            self.config['api']['host'] = self.config.get('api.api_server')

        # initialize nvidia visibility variable
        if os.environ.get('NVIDIA_VISIBLE_DEVICES') and not os.environ.get('CUDA_VISIBLE_DEVICES'):
            os.environ['CUDA_VISIBLE_DEVICES'] = os.environ.get('NVIDIA_VISIBLE_DEVICES')
        elif os.environ.get('CUDA_VISIBLE_DEVICES') and not os.environ.get('NVIDIA_VISIBLE_DEVICES'):
            os.environ['NVIDIA_VISIBLE_DEVICES'] = os.environ.get('CUDA_VISIBLE_DEVICES')

        # initialize cuda versions
        try:
            from trains_agent.helper.package.requirements import RequirementsManager
            agent = self.config['agent']
            agent['cuda_version'], agent['cudnn_version'] = \
                RequirementsManager.get_cuda_version(self.config)
        except Exception:
            pass

        # override with environment (includes cuda_version & cudnn_version)
        for config_key, env_config in ENVIRONMENT_CONFIG.items():
            value = env_config.get()
            if not value:
                continue
            env_key = ConfigValue(self.config, config_key)
            env_key.set(value)

        # initialize worker name
        worker_name = ConfigValue(self.config, "agent.worker_name")
        if not worker_name.get():
            worker_name.set(platform.node())

        # create target folders:
        folder_keys = ('agent.venvs_dir', 'agent.vcs_cache.path',
                       'agent.pip_download_cache.path',
                       'agent.docker_pip_cache', 'agent.docker_apt_cache')
        for key in folder_keys:
            folder_key = ConfigValue(self.config, key)
            if not folder_key.get():
                continue
            # update the configuration for full path
            folder = Path(os.path.expandvars(folder_key.get())).expanduser().absolute()
            folder_key.set(folder.as_posix())
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except:
                pass

    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        logger.propagate = True
        return TrainsAgentLogger(logger)

    @property
    def debug_mode(self):
        return self.config.get("agent.debug", False)

    @property
    def config_file(self):
        return self._config_file

    def print_configuration(self, remove_secret_keys=("secret", "pass", "token", "account_key")):
        # remove all the secrets from the print
        def recursive_remove_secrets(dictionary, secret_keys=()):
            for k in list(dictionary):
                for s in secret_keys:
                    if s in k:
                        dictionary.pop(k)
                        break
                if isinstance(dictionary.get(k, None), dict):
                    recursive_remove_secrets(dictionary[k], secret_keys=secret_keys)
                elif isinstance(dictionary.get(k, None), (list, tuple)):
                    for item in dictionary[k]:
                        if isinstance(item, dict):
                            recursive_remove_secrets(item, secret_keys=secret_keys)

        config = deepcopy(self.config.to_dict())
        # remove the env variable, it's not important
        config.pop('env', None)
        if remove_secret_keys:
            recursive_remove_secrets(config, secret_keys=remove_secret_keys)
        config = ConfigFactory.from_dict(config)
        self.log.debug("Run by interpreter: %s", sys.executable)
        print(
            "Current configuration (trains_agent v{}, location: {}):\n"
            "----------------------\n{}\n".format(
                self.version, self._config_file, HOCONConverter.convert(config, "properties")
            )
        )

    def send_api(self, request):
        # type: (Request) -> Any
        result = self.send(request)
        if not result.ok():
            raise APIError(result)
        if not result.response:
            raise APIError(result, extra_info="Invalid response")
        return result.response

    def get(self, service, action, version=None, headers=None,
            data=None, json=None, async_enable=False, **kwargs):
        return self._manual_request(service=service, action=action,
                                    version=version, method="get", headers=headers,
                                    data=data, async_enable=async_enable,
                                    json=json or kwargs)

    def post(self, service, action, version=None, headers=None,
             data=None, json=None, async_enable=False, **kwargs):
        return self._manual_request(service=service, action=action,
                                    version=version, method="post", headers=headers,
                                    data=data, async_enable=async_enable,
                                    json=json or kwargs)

    def _manual_request(self, service, action, version=None, method="get", headers=None,
            data=None, json=None, async_enable=False, **kwargs):

        res = self.send_request(service=service, action=action,
                                version=version, method=method, headers=headers,
                                data=data, async_enable=async_enable,
                                json=json or kwargs)

        try:
            res_json = res.json()
            return_code = res_json["meta"]["result_code"]
        except (ValueError, KeyError, TypeError):
            raise APIError(res)

        # check return code
        if return_code != 200:
            raise APIError(res)

        return res_json["data"]

    def to_json(self):
        return json.dumps(
            self.config.as_plain_ordered_dict(), cls=HOCONEncoder, indent=4
        )

    def command(self, *args):
        return Argv(*args, log=self.get_logger(Argv.__module__))

# class Session(object):
#     """
#     A TRAINS-AGENT invocation session.
#     Contains configuration information and an trains API session.
#     """
#
#     version = __version__
#     _token_refresh_threshold_sec = 60
#     _defaults = tree(
#         ("api", tree(("api_server", definitions.DEFAULT_HOST))),
#         (
#             "agent",
#             tree(
#                 ("venvs_dir", normalize_path(definitions.CONFIG_DIR, "venvs")),
#                 ("git_user", None),
#                 ("git_pass", None),
#                 ("hg_user", None),
#                 ("hg_pass", None),
#                 ("debug", False),
#                 ("worker_name", platform.node()),
#                 ("worker_id", None),
#                 (
#                     "package_manager",
#                     tree(
#                         ("type", "pip"),
#                         ("system_site_packages", False),
#                         ("force_upgrade", False),
#                     ),
#                 ),
#                 (
#                     "vcs_cache",
#                     tree(("enabled", True), ("path", definitions.DEFAULT_VCS_CACHE)),
#                 ),
#                 (
#                     "venv_update",
#                     tree(("enabled", False), ("url", DEFAULT_VENV_UPDATE_URL)),
#                 ),
#                 ("reload_config", False),
#                 (
#                     "pip_download_cache",
#                     tree(("enabled", True), ("path", DEFAULT_PIP_DOWNLOAD_CACHE)),
#                 ),
#                 ("log_files_buffering", FileBuffering.LINE_BUFFERING),
#                 ("translate_ssh", True),
#             ),
#         ),
#         (
#             "agent",
#             tree(("cuda_version", None), ("cudnn_version", None), ("cpu_only", False)),
#         ),
#     )
#     token_cache_path = Path(definitions.TOKEN_CACHE_FILE).expanduser()
#     _default_headers = {
#         definitions.HTTP_HEADERS[key]: value
#         for key, value in {
#             "worker": socket.gethostname(),
#             "client": "{}-{}".format(definitions.PROGRAM_NAME, __version__),
#         }.items()
#     }
#
#     def __init__(
#         self,
#         config_file=None,
#         config=None,
#         timeout=60,
#         use_cache=True,
#         verify_config_file=True,
#         debug=False,
#         connect_api=True,
#         trace=None,
#         **kwargs
#     ):
#         self._use_cache = use_cache
#         self._token = None
#         self._credentials = None
#         self._http_session = requests.Session()
#         self._http_session.headers.update(self._default_headers)
#         self._timeout = timeout
#         self.trace = trace
#         self._config_file = Path(
#             config_file or definitions.CONFIG_FILE_ENV.get() or definitions.CONFIG_FILE
#         ).expanduser()
#         self._extra_config_params = kwargs
#         self._verify_config_file = verify_config_file
#         self._config_modification_time = None
#
#         # merge all default keys to dictionary
#         # expand user/vars from os, and overrides in kwargs
#         self.config = config or self.load_config_file(
#             debug=debug,
#             verify_config_file=verify_config_file,
#             extra=self._extra_config_params,
#         )
#         self.main_logger_setup(PROGRAM_NAME)
#         self.log = self.get_logger(__name__)
#         self._config_mod_time = self._get_config_mod_time()
#
#         self._credentials = self.config.get("api.credentials", {})
#
#         self.api_session = None
#
#         if not connect_api:
#             return
#
#         try:
#             kwargs = dict(
#                 host=self.config.get("api.api_server", None) or self.config.get("api.host", None),
#                 api_key=self._credentials["access_key"],
#                 secret_key=self._credentials["secret_key"],
#                 worker=self._default_headers[definitions.HTTP_HEADERS["worker"]],
#                 initialize_logging=False,
#             )
#             self.api_session = APISession(config_file=self._config_file, **kwargs)
#             self.api_client = APIClient(self.api_session, api_version="2.3")
#         except ConfigurationError as e:
#             if verify_config_file:
#                 raise
#             error(e)
#         except Exception:
#             if verify_config_file:
#                 raise
#
#     @property
#     def config_file(self):
#         return self._config_file
#
#     def load_config_file(self, debug=False, verify_config_file=True, extra=None):
#         config = self._load_config_file(verify=verify_config_file)
#         self.get_kwargs_config(config, extra or {})
#         self.finalize_config(config, debug=debug, verify=verify_config_file)
#         return config
#
#     def reload(self):
#         # type: () -> bool
#         """
#         Reload configuration file and return whether necessary and successful.
#         Should suppress OS errors but raise parsing errors.
#         :return: True if could get modification time and it's greater than last modification time, else False
#         """
#         modification_time = self._get_config_mod_time()
#         if not modification_time or (
#             self._config_mod_time and modification_time <= self._config_mod_time
#         ):
#             return False
#
#         self.config = self.load_config_file(
#             debug=self.debug_mode,
#             verify_config_file=self._verify_config_file,
#             extra=self._extra_config_params,
#         )
#         self._config_mod_time = modification_time
#         return True
#
#     def get_config_value(self, key):
#         return ConfigValue(self.config, key)
#
#     def finalize_config(self, config, debug=False, verify=True):
#
#         credentials = config.get("api.credentials", {})
#         if verify:
#             missing = [
#                 key for key in ("access_key", "secret_key") if not credentials.get(key)
#             ]
#             if missing:
#                 raise CommandFailedError(
#                     "Missing required configuration key(s): {}".format(
#                         ", ".join(missing)
#                     )
#                 )
#         # set debug flag if global override set
#         if debug:
#             config["agent"]["debug"] = True
#
#         get_config_value = partial(ConfigValue, config)
#
#         config_value = get_config_value("agent.default_python")  # type: ConfigValue
#         if not config_value.get():
#             config_value.set(
#                 "{version.major}.{version.minor}".format(version=sys.version_info)
#             )
#
#         # support for older config files
#         try:
#             config["agent.venv_update.enabled"]
#         except (TypeError, pyhocon.ConfigException):
#             config.put(
#                 "agent.venv_update",
#                 ConfigFactory.from_dict(
#                     dict(
#                         enabled=bool(config.pop("agent.venv_update", False)),
#                         url=DEFAULT_VENV_UPDATE_URL,
#                     )
#                 ),
#             )
#
#         config_value = get_config_value("agent.package_manager")
#         try:
#             config_value.get().get("type")
#         except (AttributeError, TypeError, pyhocon.ConfigException):
#             config_value.set(
#                 ConfigFactory.from_dict(
#                     dict(self._defaults[config_value.key], type=config_value.get())
#                 )
#             )
#         config_value = get_config_value("agent.package_manager.type")
#         if config_value.get() == POETRY and not check_if_command_exists(POETRY):
#             raise CommandFailedError(
#                 "`{} = {}` configured in `{}` but command `{}` was not found in PATH".format(
#                     config_value.key, config_value.get(), self.config_file, POETRY
#                 )
#             )
#
#         config_value = get_config_value("agent.log_files_buffering")
#         buffering = config_value.get()
#         if isinstance(buffering, six.string_types):
#             try:
#                 buffering = FileBuffering[buffering]
#             except KeyError:
#                 raise CommandFailedError(
#                     "{} is not a valid file buffering: must be {} or integer".format(
#                         buffering, [entry.name for entry in FileBuffering]
#                     )
#                 )
#         config_value.set(int(buffering))
#
#         config_value = get_config_value("agent.cuda_version")
#         if config_value.get():
#             config_value.modify(normalize_cuda_version)
#
#     def _get_config_mod_time(self):
#         try:
#             return self.config_file.expanduser().stat().st_mtime
#         except OSError:
#             return None
#
#     def _load_config_file(self, verify=False):
#         if verify and not self.config_file.is_file():
#             raise ConfigFileNotFound()
#
#         config_file = self.config_file.expanduser()
#         user_friendly_path = reverse_home_folder_expansion(config_file)
#         config_base = deepcopy(self._defaults)
#         try:
#             try:
#                 conf = ConfigFactory.parse_file(str(config_file.resolve()))
#             except pyparsing.ParseSyntaxException as e:
#                 raise CommandFailedError(
#                     'Can not parse configuration file "{0}": '
#                     "Syntax error (at char {1.loc}), (line:{1.lineno}, col:{1.col})".format(
#                         user_friendly_path, e
#                     )
#                 )
#             except pyparsing.ParseBaseException as e:
#                 raise CommandFailedError(
#                     'Can not parse configuration file "{}": {}'.format(
#                         user_friendly_path, e
#                     )
#                 )
#             except Exception as e:
#                 raise CommandFailedError(
#                     'Can not read configuration file "{}": {}'.format(
#                         user_friendly_path, e
#                     )
#                 )
#             else:
#                 self._get_env_config(conf)
#                 ConfigTree.merge_configs(config_base, conf)
#                 return config_base
#         except Exception:
#             if verify:
#                 raise
#             return config_base
#
#     def get_kwargs_config(self, config, kwargs):
#         for key in set(config) | set(self._defaults):
#             section = config.get(key, ConfigTree())
#             def_section = self._defaults.get(key, ConfigTree())
#             for k in set(section) | set(def_section):
#                 if section.get(k, None) is None and k in def_section:
#                     section[k] = def_section[k]
#                 if kwargs.get(k):
#                     section[k] = kwargs[k]
#                 if section.get(k, None):
#                     try:
#                         section[k] = os_path.expanduser(os_path.expandvars(section[k]))
#                     except Exception:
#                         pass
#             config[key] = section
#
#     @contextmanager
#     def use_http_session(
#         self, http_session=None, timeout=None, use_default_headers=True
#     ):
#         """
#         Context manager for using a different HTTP session and/or timeout than instance's one.
#         The original session is restored when exiting the context.
#         :param http_session: session to use
#         :type http_session: requests.Session()
#         :param timeout: new timeout to use in seconds
#         :type timeout: int
#         :param use_default_headers: whether to update the session's headers with the default ones
#         :type use_default_headers: bool
#         """
#         old_session = self._http_session
#         old_timeout = self._timeout
#         if http_session:
#             self._http_session = http_session
#         if timeout is not None:
#             self._timeout = timeout
#         if use_default_headers:
#             self._http_session.headers.update(self._default_headers)
#         try:
#             yield
#         finally:
#             if http_session:
#                 self._http_session.close()
#                 self._http_session = old_session
#             if timeout is not None:
#                 self._timeout = old_timeout
#
#     @staticmethod
#     def _report_env_config_value(key, value, config=None, config_key=None):
#         if value is None:
#             return None
#         message = "Using environment value {}={}".format(key, value)
#         if config and config_key:
#             try:
#                 dpath.get(config, config_key, separator=".")
#             except KeyError:
#                 pass
#             else:
#                 message += " (override configured value)"
#         print(message)
#
#     @classmethod
#     def _get_env_config(cls, config):
#         for config_key, env_config in definitions.ENVIRONMENT_CONFIG.items():
#             result = env_config.get(key=True)
#             if not result:
#                 continue
#             env_name, value = result
#             cls._report_env_config_value(env_name, value, config, config_key)
#             dpath.new(config, config_key, value, separator=".")
#
#     @property
#     def host(self):
#         return self.config.get("api.api_server", None) or self.config.get("api.host", None)
#
#     def to_hocon(self):
#         return HOCONConverter.to_hocon(self.config)
#
#     def to_json(self):
#         return json.dumps(
#             self.config.as_plain_ordered_dict(), cls=HOCONEncoder, indent=4
#         )
#
#     def print_configuration(self, remove_secret_keys=("secret", "pass", "token", "account_key")):
#         # remove all the secrets from the print
#         def recursive_remove_secrets(dictionary, secret_keys=()):
#             for k in list(dictionary):
#                 for s in secret_keys:
#                     if s in k:
#                         dictionary.pop(k)
#                         break
#                 if isinstance(dictionary.get(k, None), dict):
#                     recursive_remove_secrets(dictionary[k], secret_keys=secret_keys)
#                 elif isinstance(dictionary.get(k, None), (list, tuple)):
#                     for item in dictionary[k]:
#                         if isinstance(item, dict):
#                             recursive_remove_secrets(item, secret_keys=secret_keys)
#
#         config = deepcopy(self.config)
#         if remove_secret_keys:
#             recursive_remove_secrets(config, secret_keys=remove_secret_keys)
#         config = ConfigFactory.from_dict(config)
#         self.log.debug("Run by interpreter: %s", sys.executable)
#         print(
#             "Current configuration (trains_agent v{}, location: {}):\n"
#             "----------------------\n{}\n".format(
#                 self.version, self._config_file, HOCONConverter.convert(config, "properties")
#             )
#         )
#
#     def _valid_token(self, token=None):
#         token = token or self._token
#         if not token:
#             return False
#         try:
#             payload = jwt.decode(token, verify=False)
#         except jwt.exceptions.InvalidTokenError:
#             return False
#         exp = payload["exp"]
#         # token will not expire in the next 60 seconds
#         return (time.time() + self._token_refresh_threshold_sec) <= exp
#
#     @property
#     def current_user(self):
#         token = self.get_token()
#         return jwt.decode(token, verify=False)["identity"]["user"]
#
#     def get_token(self):
#         if self._valid_token():
#             return self._token
#
#         access_key = self._credentials["access_key"]
#         secret_key = self._credentials["secret_key"]
#
#         tokens = pyhocon.ConfigTree()
#         if self._use_cache and self.token_cache_path.is_file():
#             tokens = pyhocon.ConfigFactory.parse_file(str(self.token_cache_path))
#             value = tokens.get(access_key, None)
#             if value:
#                 if len(value) != 2:
#                     self.token_cache_path.unlink()  # unlink is remove
#                 else:
#                     token, hashed = value
#                     if bcrypt.checkpw(
#                         secret_key.encode("ascii"), hashed.encode("ascii")
#                     ) and self._valid_token(token):
#                         return token
#
#         res = self._http_request(
#             method="get",
#             host=self.host,
#             version=definitions.API_VERSION,
#             service="auth",
#             action="login",
#             auth=requests.auth.HTTPBasicAuth(access_key, secret_key),
#             json={"expiration_sec": definitions.TOKEN_EXPIRATION_SECONDS},
#         )
#
#         if res.status_code != 200:
#             raise CommandFailedError("Failed obtaining token from {}".format(self.host))
#
#         try:
#             response_data = res.json()
#             self._token = response_data["data"]["token"]
#         except KeyError:
#             raise APIError(res, extra_info="could not find response.data.token")
#         except ValueError:
#             raise APIError(res)
#
#         if self._use_cache:
#             hashed = bcrypt.hashpw(secret_key.encode("ascii"), bcrypt.gensalt())
#             tokens[access_key] = [str(self._token), hashed.decode("ascii")]
#             self.token_cache_path.write_text(
#                 six.text_type(pyhocon.HOCONConverter.to_hocon(tokens))
#             )
#
#         return self._token
#
#     def _http_request(
#         self,
#         method,
#         host,
#         version,
#         service,
#         action,
#         json=None,
#         headers=None,
#         auth=None,
#         **kwargs
#     ):
#         return self._http_session.request(
#             url="{host}/{version}/{service}.{action}".format(**locals()),
#             method=method,
#             headers=headers,
#             auth=auth,
#             verify=True,
#             json=json,
#             timeout=self._timeout,
#             **kwargs
#         )
#
#     def _manual_api_request(
#         self, method, service, action, data=None, params=None, headers=None, **kwargs
#     ):
#         token = self.get_token()
#         _headers = {"Authorization": "Bearer %s" % token}
#         _headers.update(headers or {})
#
#         tic = time.time()
#         res = self._http_request(
#             method=method,
#             host=self.host,
#             version=definitions.API_VERSION,
#             service=service,
#             action=action,
#             json=kwargs,
#             headers=_headers,
#             data=data,
#             params=params,
#         )
#
#         if self.debug_mode:
#             print(
#                 "{} request: {}/{} took {:.3f} sec".format(
#                     method, service, action, time.time() - tic
#                 )
#             )
#         try:
#             res_json = res.json()
#             return_code = res_json["meta"]["result_code"]
#         except (ValueError, KeyError, TypeError):
#             raise APIError(res)
#
#         # check return code
#         if return_code != 200:
#             raise APIError(res)
#
#         return res_json["data"]
#
#     def get(self, *args, **kwargs):
#         return self._manual_api_request("get", *args, **kwargs)
#
#     def post(self, *args, **kwargs):
#         return self._manual_api_request("post", *args, **kwargs)
#
#     def get_with_act_as(
#         self, impersonation_user_id=None, headers=None, *args, **kwargs
#     ):
#         headers = chain_map(
#             {definitions.HTTP_HEADERS["act-as"]: impersonation_user_id}, headers or {}
#         )
#         return self.get(headers=headers, *args, **kwargs)
#
#     def send_api(self, request):
#         # type: (Request) -> Any
#         result = self.api_session.send(request, headers=self._default_headers)
#         if not result.ok():
#             raise APIError(result)
#         if not result.response:
#             raise APIError(result, extra_info="Invalid response")
#         return result.response
#
#     @property
#     def debug_mode(self):
#         return self.config["agent.debug"]
#
#     def main_logger_setup(self, name):
#         logger = logging.getLogger(name)
#         if logger.handlers:
#             return
#         handler = logging.StreamHandler()
#         if self.debug_mode:
#             level = logging.DEBUG
#             formatter = logging.Formatter(
#                 "{} - %(asctime)s - %(name)-30s - %(levelname)-8s - %(message)s".format(
#                     PROGRAM_NAME
#                 )
#             )
#         else:
#             level = logging.INFO
#             formatter = LowercaseFormatter(
#                 "{}: %(levelname)s: %(message)s".format(PROGRAM_NAME)
#             )
#         logger.setLevel(level)
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)
#         return TrainsAgentLogger(logger)
#
#     @staticmethod
#     def get_logger(name):
#         logger = logging.getLogger(name)
#         logger.propagate = True
#         return TrainsAgentLogger(logger)
#
#     @contextmanager
#     def temp_file(self, prefix, contents):
#         # type: (Union[Text, Iterable[Text]], Iterable[Text]) -> Text
#         """
#         Write contents to a temporary file, yielding its path. Finally, delete it.
#         :param prefix: file name prefix
#         :param contents: text lines to write
#         """
#         f, temp_path = mkstemp(suffix=".txt", prefix=prefix)
#         with f:
#             f.write(
#                 contents
#                 if isinstance(contents, six.text_type)
#                 else join_lines(contents)
#             )
#         try:
#             yield temp_path
#         finally:
#             if not self.debug_mode:
#                 safe_remove_file(temp_path)
#
#     def command(self, *args):
#         return Argv(*args, log=self.get_logger(Argv.__module__))
#

@attr.s
class TrainsAgentLogger(object):
    """
    Proxy around logging.Logger because inheriting from it is difficult.
    """

    logger = attr.ib(type=logging.Logger)

    def _log_with_error(self, level, *args, **kwargs):
        """
        Include error information when in debug mode
        """
        kwargs.setdefault("exc_info", self.logger.isEnabledFor(logging.DEBUG))
        return self.logger.log(level, *args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._log_with_error(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        return self._log_with_error(logging.ERROR, *args, **kwargs)

    def __getattr__(self, item):
        return getattr(self.logger, item)

    def __call__(self, *args, **kwargs):
        """
        Compatibility with old ``Command.log()`` method
        """
        return self.logger.info(*args, **kwargs)


def normalize_cuda_version(value):
    # type: (Any) -> str
    """
    Take variably formatted cuda version string/number and return it in the same format:
    string decimal representation of 10 * major + minor.

    >>> normalize_cuda_version(100)
    '100'
    >>> normalize_cuda_version("100")
    '100'
    >>> normalize_cuda_version(10)
    '10'
    >>> normalize_cuda_version(10.0)
    '100'
    >>> normalize_cuda_version("10.0")
    '100'
    >>> normalize_cuda_version("10.0.130")
    '100'
    """
    value = str(value)
    if "." in value:
        try:
            value = str(int(float(".".join(value.split(".")[:2])) * 10))
        except (ValueError, TypeError):
            pass
    return value
