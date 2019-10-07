from deployv.helpers import utils
from deployv.base.errors import BuildError, NoSuchImage
from deployv.helpers.clone_oca_dependencies import run as clone_oca_deps
from deployv.instance import SAAS_VERSIONS
from spur.results import RunProcessError
from stat import S_IREAD, S_IWRITE
from logging import getLogger
from os import path, chmod
from base64 import b64decode
from branchesv.branches import load as load_branches
import simplejson as json

_logger = getLogger(__name__)


class CloneV(object):

    def __init__(self, config, instance):
        self.config = config
        self.instance_manager = instance

    def clone_repositories(self):
        """Create the folder where the repositories will clone,
        then it the ssh key to clone the private repositories and for last
        it clone the repositories and get the variables from the main repository.
        """
        try:
            res_paths = self._create_working_folder()
            self._deploy_key()
            self._clone_dependencies(res_paths)
        except (RunProcessError, BuildError, IOError, NoSuchImage) as error:
            msg_error = utils.get_error_message(error)
            _logger.exception('Could not clone the repos: %s', msg_error)
            return {"error": msg_error}
        return {'result': 'Repositories cloned'}

    def _create_working_folder(self):
        """Creates the working directory where store the repositories cloned.
        """
        instance_path = path.join(self.config.temp_working_folder, 'instance')
        addons_path = path.join(instance_path, 'extra_addons')
        utils.makedir(addons_path)
        return {'instance_path': instance_path, 'addons_path': addons_path}

    def _clone_dependencies(self, paths):
        """Clones the repositories specified in the config and
        search the variables.sh file to set the data in `variables`.

        :param paths: Content the instance folder path where the odoo repository is cloned,
        and the `extra_addons` folder where content all the other repositories cloned.
        :return: True if no error is raised.
        """
        repos = self.config.instance_config.get('repositories')
        res = load_branches(repos, paths['instance_path'], self.config.temp_working_folder,
                            self.config.key_ssh_path)
        cloned = repos
        if res:
            raise BuildError(res.get('msg'))
        variables = utils.find_file(paths['instance_path'], 'variables.sh')
        self.config.variables.update(utils.parse_variables_to_json(variables))
        if not self.instance_manager.config_variables.get('version'):
            raise BuildError('You need to specify a version in '
                             ' your "variables.sh" file in the repository')
        odoo_url = 'https://github.com/%s.git' % (
            self.instance_manager.config_variables.get('odoo_repo'))
        extra_repos = [('odoo', odoo_url, 'odoo',
                        self.instance_manager.config_variables.get('odoo_branch'))]
        version = self.instance_manager.config_variables.get('version')
        if self.config.instance_config.get('instance_type') != 'production':
            branch = SAAS_VERSIONS.get(version) or version
            extra_repos.append((
                'isolated_addons', 'https://git.vauxoo.com/vauxoo/isolated_addons.git',
                'extra_addons/isolated_addons', branch))
            if self.config.container_config.get('full_stack'):
                # odoo-profile is clone alone, because
                # it doesn't matter if the repository can't be cloned
                profiler_repo = utils.add_repo(
                    branch, 'odoo-profiler', 'extra_addons/odoo-profiler',
                    'https://github.com/Vauxoo/odoo-profiler.git')
                load_branches([profiler_repo], paths['instance_path'],
                              self.config.temp_working_folder, self.config.key_ssh_path)
                cloned.append(profiler_repo)
        repo_names = [rep.get('name') for rep in repos]
        extra_clone = []
        for name, url, r_path, r_branch in extra_repos:
            if name in repo_names:
                _logger.debug('%s repository is already in the json, skipping', name)
                continue
            extra_clone.append(utils.add_repo(r_branch, name, r_path, url))
        # Clones oca dependencies.
        res_oca = clone_oca_deps(paths['addons_path'], paths['addons_path'], version)
        if not res_oca[0]:
            raise BuildError(res_oca[1])
        res = load_branches(repos + extra_clone, paths['instance_path'],
                            self.config.temp_working_folder, self.config.key_ssh_path)
        with open(path.join(self.config.temp_working_folder, 'repos_cloned.json'), 'w') as wfile:
            json.dump(cloned + extra_clone, wfile, indent=4, ensure_ascii=False,
                      separators=(',', ':'))
        if res:
            raise BuildError(res.get('msg'))
        return True

    def _deploy_key(self):
        """Deploy a SSH private key into the temporal working folder.
        """
        if not utils.is_base64_encode(self.config.instance_config.get('ssh_key')):
            _logger.error("Can not use the specified ssh key. It is not encoded in base64")
            return False
        _logger.info('Deploying keys')
        ssh_key = utils.decode(b64decode(self.config.instance_config.get('ssh_key')))
        filename = path.join(self.config.temp_working_folder, 'id_rsa')
        with open(filename, 'w') as key_file:
            key_file.write(ssh_key)
        chmod(filename, S_IREAD + S_IWRITE)
        self.config.key_ssh_path = filename
