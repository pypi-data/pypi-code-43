import os
import sys
from abc import abstractmethod
from collections import defaultdict
from importlib import import_module
import argparse
import inspect
import json

from pkgutil import iter_modules

from azureml.studio.package_info import __version__ as current_version
from azureml.studio.modulehost.attributes import ReleaseState
from azureml.studio.common.error import AlghostRuntimeError
from azureml.studio.common.json_encoder import EnhancedJsonEncoder
from azureml.studio.core.utils.fileutils import clear_folder
from azureml.studio.core.utils.strutils import join_stripped, parse_version_str
from azureml.studio.core.utils.yamlutils import dump_to_yaml
from azureml.studio.modulehost.module_reflector import ModuleEntry, BaseModule, is_valid_module_entry
from azureml.studio.tool.module_registry import ModuleRegistry, ServerConf
from azureml.studio.tool.module_spec import ModuleSpec
from azureml.studio.tool.checkers import assert_str_val_pass_rules


def sha1(input_str: str):
    """Given a string, return it's SHA1 digest.

    >>> sha1('hello alghost')
    '6844218275a7cbe6a18db0e84d2e2d7e1f2b314a'
    """
    if input_str is None:
        return None

    import hashlib
    sha_1 = hashlib.sha1()
    sha_1.update(input_str.encode())
    return sha_1.hexdigest()


class SpecHandler:
    @abstractmethod
    def handle_specs(self, specs: list):
        pass


class PrintStatisticsHandler(SpecHandler):
    def handle_specs(self, specs: list):
        print("\n--------------------------------------------------------------")
        self._print_module_category_tree(specs)
        print("\n--------------------------------------------------------------\n")
        self._print_module_statistics(specs)
        print("\n--------------------------------------------------------------\n")

    @staticmethod
    def _print_module_category_tree(specs):
        last_category = None
        for index, module in enumerate(specs, start=1):
            category = module.category
            if category != last_category:
                print(f"\n  {category}")
                last_category = category

            name = module.name
            release_state = module.release_state
            released = release_state == ReleaseState.Release

            marker = '*' if released else '-'
            badge = f"[{release_state.name.upper()}]" if not released else None
            print(f"    {join_stripped(marker, badge, name)}")

    @staticmethod
    def _print_module_statistics(specs):
        def count_by_state(state):
            return sum(m.release_state == state for m in specs)

        count_by_states = {s.name: count_by_state(s) for s in ReleaseState}
        formatted_counts = [f"{count} {name}" for name, count in count_by_states.items() if count > 0]
        print(f"  Total {len(specs)} ({join_stripped(*formatted_counts, sep=', ')}) Modules.")


class SaveToFileHandler(SpecHandler):
    def __init__(self, folder):
        os.makedirs(folder, exist_ok=True)
        self._folder = folder

    def handle_specs(self, specs: list):
        # Clear module path first, to detect module deletion
        clear_folder(self._folder)

        for s in specs:
            self._save_spec_to_file(s, self._folder)

    @staticmethod
    def _save_spec_to_file(spec, folder):
        spec_json = json.dumps(spec.ux_contract_dict, indent=4, cls=EnhancedJsonEncoder)
        module_name = _normalize_module_name(spec.name)
        file_name = f"{module_name}.json"
        with open(os.path.join(folder, file_name), 'w') as f:
            f.write(spec_json)


class SaveYamlSpecHandler(SpecHandler):
    def __init__(self, folder):
        os.makedirs(folder, exist_ok=True)
        self._folder = folder

    def handle_specs(self, specs: list):
        # Clear module path first, to detect module deletion
        clear_folder(self._folder)

        for s in specs:
            self._save_yaml_spec_to_file(s, self._folder)

    @staticmethod
    def _save_yaml_spec_to_file(spec, folder):
        module_name = _normalize_module_name(spec.name)
        file_name = f"{module_name}.yaml"
        with open(os.path.join(folder, file_name), 'w') as f:
            dump_to_yaml(spec.yaml_spec_dict, f)


class SaveDependenciesYamlHandler(SpecHandler):
    def __init__(self, folder):
        os.makedirs(folder, exist_ok=True)
        self._folder = folder

    def handle_specs(self, specs: list):
        # Clear module path first, to detect module deletion
        clear_folder(self._folder)

        index = defaultdict(list)
        for s in specs:
            module_name, file_name = self._save_dependencies_to_file(s, self._folder)
            index[file_name].append(module_name)

        with open(os.path.join(self._folder, 'index.yaml'), 'w') as f:
            dump_to_yaml(index, f)

    @staticmethod
    def _save_dependencies_to_file(spec, folder):
        module_name = spec.name
        yaml_str = spec.conda_dependencies.conda_dependency_yaml
        file_name = f"{sha1(yaml_str)}.yaml"
        with open(os.path.join(folder, file_name), 'w') as f:
            f.write(yaml_str)

        return module_name, file_name


class RegisterHandler(SpecHandler):
    def __init__(self, conf: ServerConf, cert_file=None, need_confirm=True):
        if not cert_file:
            raise ValueError(f"cert must be specified to register modules.")

        self._conf = conf
        self._registry = _get_registry_from_conf(conf, cert_file=cert_file)
        self._need_confirm = need_confirm
        self._allowed_release_states = conf.allowed_release_states

    def handle_specs(self, specs: list):
        batch_id = self._get_batch_id(current_version)

        self._confirm_conf_name_if_needed()
        self._confirm_batch_id_if_needed(expected_batch_id=batch_id)

        print(f"Registering to {self._conf.name} with batch id {batch_id} ...")
        specs_to_upload = [s for s in specs if self._should_upload(s)]
        self._registry.add_batch(batch_id, specs_to_upload)
        print(f"Registered {len(specs_to_upload)} modules.\n")

    @staticmethod
    def _get_batch_id(version):
        """
        Calculate "batch_id" (a incrementing integer, e.g. 834)
        using "alghost version" (a string looks like "0.0.50").

        A "batch id" is like a "version number" used on server-side (known as SMT),
        When an experiment is created, the batch ids for each module are recorded.

        For now, we bind alghost version and batch id one by one,
        using a simple algorithm, so that we can calculate one with another.

        Binding batch id with alghost version is helpful to share experiments
        across different deployments. Given a batch id, the corresponding version's
        module can be found and loaded correctly.

        :param version: alghost version string
        :return: the calculated batch id
        """
        segments = parse_version_str(version)
        if segments[0] != 0 or segments[1] != 0:
            raise ValueError(f"Only support '0.0.*' versions for now")

        # We simply add an offset to the last segment of the alghost version,
        # since the first two segments are 0 for now.
        # Choosing 784 as the offset is just because when we decided to use this strategy,
        # the alghost version was "0.0.50" and the batch id was 834,
        # so the offset should be 834-50=784.
        # TODO: calculate method to be updated when first two segments incremented.
        # TODO: offset to be updated (maybe 800 would a human friendly choice).
        batch_id = segments[2] + 784
        return batch_id

    def _confirm_conf_name_if_needed(self):
        if self._need_confirm:
            answer = input(f"Please enter the conf name to be registered: {ServerConf.AVAILABLE_NAMES}: ")
            if not answer == self._conf.name:
                raise ValueError(f"Conf name mismatch, module registration aborted.")

    def _confirm_batch_id_if_needed(self, expected_batch_id):
        if self._need_confirm:
            entered_batch_id = input(f"Please enter the batch id: ")
            if not str(expected_batch_id) == entered_batch_id:
                raise ValueError(f"Batch id mismatch, expected to be {expected_batch_id} but got {entered_batch_id}.")

    def _should_upload(self, spec: ModuleSpec):
        module_name = spec.name
        release_state = spec.release_state
        if release_state not in self._allowed_release_states:
            print(f"   '{module_name}'s release state is {release_state}, "
                  f"required to be {self._allowed_release_states}, cannot register.")
            return False

        return True


class ActivateHandler(RegisterHandler):
    def __init__(self, conf: ServerConf, cert_file=None, need_confirm=True, version_to_activate=None,
                 force_downgrade=False):
        super().__init__(conf=conf, cert_file=cert_file, need_confirm=need_confirm)
        self._version_to_activate = version_to_activate
        self._force_downgrade = force_downgrade

    def handle_specs(self, specs: list):
        batch_id = self._get_batch_id(self._version_to_activate)
        self._confirm_conf_name_if_needed()
        self._confirm_batch_id_if_needed(expected_batch_id=batch_id)
        self._confirm_latest_version_if_needed()

        print(f"Activating {self._version_to_activate} ({batch_id}) on {self._conf.name} ...")
        self._registry.activate_batch(batch_id, force=self._force_downgrade)
        print(f"Activated.")
        description = self._registry.get_batch_description()
        print(description)

    def _confirm_latest_version_if_needed(self):
        if self._need_confirm:
            if self._version_to_activate != current_version:
                answer = input(f"Latest version is {current_version}. "
                               f"Continue to activate older version {self._version_to_activate}? ")
                if not answer.lower() in ('y', 'yes'):
                    raise ValueError(f"Aborted to activate an older version.")


class DownloadAndSaveHandler(SpecHandler):
    def __init__(self, conf: ServerConf, cert_file: str, folder: str):
        if not cert_file:
            raise ValueError(f"cert must be specified to register modules.")

        self._registry = _get_registry_from_conf(conf, cert_file=cert_file)
        self._folder = folder
        os.makedirs(folder, exist_ok=True)

    def handle_specs(self, _: list):
        print(f"Downloading modules from module registry ...")
        smt_specs = self._registry.list_modules()
        print(f"Downloaded {len(smt_specs)} modules.")

        # Clear module path first, to detect module deletion
        clear_folder(self._folder)
        for s in smt_specs:
            self._save_smt_spec_to_file(s, self._folder)

    @staticmethod
    def _save_smt_spec_to_file(smt_spec, folder):
        spec_json = json.dumps(smt_spec, indent=4, cls=EnhancedJsonEncoder)
        module_name = _normalize_module_name(smt_spec['Name'])
        file_name = f"{module_name}.json"
        with open(os.path.join(folder, file_name), 'w') as f:
            f.write(spec_json)


def _normalize_module_name(module_name):
    return module_name.replace(' ', '_').lower()


def _class_type_looks_like_a_module(cls):
    return issubclass(cls, BaseModule) and cls is not BaseModule


def _class_name_looks_like_a_module(cls):
    return cls.__name__.endswith('Module') and not cls.__name__ == 'BaseModule'


def _class_looks_like_a_module(cls):
    return _class_type_looks_like_a_module(cls) or _class_name_looks_like_a_module(cls)


def _validate_module_class(cls):
    if not _class_type_looks_like_a_module(cls):
        raise TypeError(f"{cls} must inherit from BaseModule.")

    if not _class_name_looks_like_a_module(cls):
        raise ValueError(f"{cls}: class name must end with 'Module'.")


def _enumerate_simple_modules(module_name, exclude=()):
    module = import_module(module_name)

    # Use __path__ attr to determine whether a module is a 'simple module' or a 'package module'.
    # A 'simple module' refers to a python file, and a 'package module' refers to a folder.
    # Detailed documentation: https://docs.python.org/3/reference/import.html#module-path
    path = getattr(module, '__path__', None)
    is_simple_module = path is None

    for module_name_suffix in exclude:
        if module.__name__.endswith(module_name_suffix):
            return

    if is_simple_module:
        # For 'simple module's, simply yield.
        yield module
    else:
        # For 'package module's, find simple modules recursively to yield.
        for module_spec in iter_modules(path=path, prefix=f"{module_name}."):
            sub_module_name = module_spec.name
            yield from _enumerate_simple_modules(sub_module_name, exclude=exclude)


def _enumerate_classes_in_module(module):
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            # Filter the classes roughly, and then check strictly.
            # The purpose for taking this strategy is that we want to detect human mistakes
            # (say, forgot to inherit from BaseModule) as much as we can.
            if _class_looks_like_a_module(obj):
                _validate_module_class(obj)
                yield obj


def _enumerate_functions_in_class(cls):
    for name, obj in inspect.getmembers(cls):
        if inspect.isfunction(obj):
            yield obj


def _enumerate_module_entry_in_class(cls):
    for f in _enumerate_functions_in_class(cls):
        try:
            if is_valid_module_entry(f):
                entry = ModuleEntry.from_func(f)
                yield entry
        except (ValueError, TypeError) as e:
            raise AlghostRuntimeError(f"Failed to create spec for {cls}") from e


def enumerate_module_entry(base_module_name, exclude=()):
    for module in _enumerate_simple_modules(base_module_name, exclude=exclude):
        for cls in _enumerate_classes_in_module(module):
            entries_detected = 0
            for entry in _enumerate_module_entry_in_class(cls):
                try:
                    entries_detected += 1
                    yield entry
                except GeneratorExit:
                    return
                except BaseException as e:
                    raise AlghostRuntimeError("Failed to generate module entry") from e
            if entries_detected <= 0:
                raise AlghostRuntimeError(f"{cls}: No module entry detected.")
            elif entries_detected > 1:
                raise AlghostRuntimeError(f"{cls}: Detected {entries_detected} module entries."
                                          f" Supposed to be only one.")


def _enumerate_module_specs(base_module_name, exclude=()):
    for entry in enumerate_module_entry(base_module_name, exclude):
        yield ModuleSpec(entry)


def get_module_spec_list(base_module_name, exclude=(), release_state_filter=None):
    result = []
    seen = {}

    for spec in _enumerate_module_specs(base_module_name, exclude=exclude):
        family_id = spec.family_id
        if family_id in seen:
            if seen[family_id] == spec:
                # Say, `EnterData.run` method is defined in modules.dataio.enter_data.enter_data,
                # and imported in the test source in modules.dataio.enter_data.tests.test_enter_data,
                # the method will be detected in both modules, with the same python object id.
                # We just simply skip the duplicate case here since it is not a family-id-duplicate error.
                print(f"    already seen, skip")
                continue

            raise ValueError(f"'{spec.name}': Duplicate family id with '{seen[family_id].name}'")

        seen.update({family_id: spec})
        if release_state_filter is None or spec.release_state in release_state_filter:
            result.append(spec)

    return result


def _output_path(name):
    script_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_path, 'output', name)


def _get_registry_from_conf(conf: ServerConf, cert_file=None):
    if not cert_file:
        raise ValueError("Cert must be specified")

    return ModuleRegistry(
        base_url=conf.url,
        workspace_id=conf.workspace_id,
        cert_file=cert_file
    )


def _assert_module_meta_is_valid(spec):
    str_attrs = ['name', 'description']
    for attr in str_attrs:
        assert_str_val_pass_rules(getattr(spec.meta, attr))


def main(args):
    parser = argparse.ArgumentParser(
        "Module Collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""A CLI tool to collect modules, generate module spec JSON files, and register to SMT.

Example Usage:

python module_collector.py --base-module=azureml.studio.modules.dataio.enter_data'
    Generates JSON spec file for modules under 'azureml.studio.modules.dataio.enter_data'.

python module_collector.py
    Generates JSON spec file for modules under 'azureml.studio.modules',
    which is the default base module start point if not specified.

python module_collector.py --register
    Generates JSON spec file for modules under 'azureml.studio.modules', and register them to SMT.

"""
    )

    parser.add_argument(
        '--base-module', type=str, default='azureml.studio.modules',
        help="Base module (along with all child modules) to be extracted."
    )
    parser.add_argument(
        '--exclude', action='append', default=['.simple', '.tests', '.test'],
        help="Package ends with these patterns will be excluded."
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help="Will do nothing if specified."
    )
    parser.add_argument(
        '--register', action='store_true',
        help="Will perform registration to SMT if specified."
    )
    parser.add_argument(
        '--activate', type=str, nargs='?', const=current_version,
        help="Activate given version of modules."
    )
    parser.add_argument(
        '--force-downgrade', action='store_true',
        help="Use with --activate. By default, module version can downgrade by up to 2 versions "
             "(e.g. One can downgrade from 0.0.10 to 0.0.8, but cannot to 0.0.7.) "
             "Specify this flag to bypass the check."
    )
    parser.add_argument(
        '--conf', default='int',
        help="To which server will be registered."
    )
    parser.add_argument(
        '--verify-upload', action='store_true',
        help="Will download registered modules if specified."
    )
    parser.add_argument(
        '--cert', type=str,
        help="Certificate file to communicate with registry server."
    )
    parser.add_argument(
        '--skip-confirm', action='store_true',
        help='By default, confirm of registration server is needed, '
             'let user to type in server name to avoid human mistake. '
             'Specify this option to skip this action.'
    )

    args = parser.parse_args(args)
    base_module_name = args.base_module
    exclude = args.exclude

    conf = ServerConf(args.conf)

    handlers = [
        PrintStatisticsHandler(),
        SaveToFileHandler(_output_path('modules')),
        SaveYamlSpecHandler(_output_path('yaml_spec')),
        SaveDependenciesYamlHandler(_output_path('conda_yamls')),
    ]

    if args.register:
        handlers.append(RegisterHandler(conf, cert_file=args.cert, need_confirm=not args.skip_confirm))

    if args.verify_upload:
        handlers.append(DownloadAndSaveHandler(conf, cert_file=args.cert, folder=_output_path('smt_module')))

    if args.activate:
        handlers.append(ActivateHandler(conf, cert_file=args.cert, need_confirm=not args.skip_confirm,
                                        version_to_activate=args.activate, force_downgrade=args.force_downgrade))

    module_specs = get_module_spec_list(
        base_module_name=base_module_name,
        exclude=exclude,
        release_state_filter=conf.allowed_release_states
    )

    for spec in module_specs:
        _assert_module_meta_is_valid(spec)

    if not args.dry_run:
        for handler in handlers:
            handler.handle_specs(module_specs)


if __name__ == '__main__':
    main(sys.argv[1:])
