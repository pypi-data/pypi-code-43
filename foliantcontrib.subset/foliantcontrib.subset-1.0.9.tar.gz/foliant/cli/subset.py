'''CLI extension for the ``subset`` command.'''

from uuid import uuid1
from pathlib import Path
from collections import OrderedDict
from logging import DEBUG, WARNING
from cliar import set_arg_map, set_metavars, set_help
from yaml import Loader

from foliant.config import Parser
from foliant.cli.base import BaseCli


class Cli(BaseCli):
    def _neutralize_special_characters(self, serialized_yaml: str) -> str:
        serialized_yaml = serialized_yaml.replace('!', f'EXCLAMATION_{self._neutralization_uuid}_')
        serialized_yaml = serialized_yaml.replace('&', f'AMPERSAND_{self._neutralization_uuid}_')
        serialized_yaml = serialized_yaml.replace('*', f'ASTERISK_{self._neutralization_uuid}_')

        return serialized_yaml

    def _restore_special_characters(self, serialized_yaml: str) -> str:
        serialized_yaml = serialized_yaml.replace(f'EXCLAMATION_{self._neutralization_uuid}_', '!')
        serialized_yaml = serialized_yaml.replace(f'AMPERSAND_{self._neutralization_uuid}_', '&')
        serialized_yaml = serialized_yaml.replace(f'ASTERISK_{self._neutralization_uuid}_', '*')

        return serialized_yaml

    def _get_whole_project_partial_config(self) -> OrderedDict:
        with open(
            self._project_dir_path / self._config_file_name, encoding='utf8'
        ) as whole_project_partial_config_file:
            whole_project_partial_config_str = whole_project_partial_config_file.read()

        whole_project_partial_config_str = self._neutralize_special_characters(whole_project_partial_config_str)

        from oyaml import load

        whole_project_partial_config = load(whole_project_partial_config_str, Loader)

        return whole_project_partial_config

    def _get_subset_partial_config(self) -> OrderedDict:
        with open(self._subset_dir_path / self._config_file_name, encoding='utf8') as subset_partial_config_file:
            subset_partial_config_str = subset_partial_config_file.read()

        subset_partial_config_str = self._neutralize_special_characters(subset_partial_config_str)

        from oyaml import load

        subset_partial_config = load(subset_partial_config_str, Loader)

        return subset_partial_config

    def _get_subset_dir_path(self, user_defined_path_str: str) -> Path:
        self.logger.debug(f'User-defined subset path: {user_defined_path_str}')

        subset_dir_path = Path(user_defined_path_str).expanduser()

        if (
            self._src_dir_path.resolve() in subset_dir_path.resolve().parents
            or
            self._src_dir_path.resolve() == subset_dir_path.resolve()
        ):
            self.logger.debug(
                f'The project source directory {self._src_dir_path} is included ' +
                f'into the user-defined subset path {user_defined_path_str}'
            )

        else:
            subset_dir_path = self._src_dir_path / subset_dir_path

            if (
                self._src_dir_path.resolve() in subset_dir_path.resolve().parents
                or
                self._src_dir_path.resolve() == subset_dir_path.resolve()
            ):
                self.logger.debug(
                    f'The project source directory {self._src_dir_path} is not included '
                    f'into the user-defined subset path {user_defined_path_str}'
                )

            else:
                error_message = f'Subset path {subset_dir_path} is outside the project source directory'

                self.logger.critical(error_message)

                raise RuntimeError(error_message)

        if subset_dir_path.is_dir():
            return subset_dir_path

        else:
            error_message = f'Subset path {subset_dir_path} is not an existing directory'

            self.logger.critical(error_message)

            raise RuntimeError(error_message)

    def _get_chapters_with_rewritten_paths(self, chapters: OrderedDict) -> OrderedDict:
        def _recursive_process_chapters(chapters_subset):
            if isinstance(chapters_subset, dict):
                new_chapters_subset = {}
                for key, value in chapters_subset.items():
                    new_chapters_subset[key] = _recursive_process_chapters(value)

            elif isinstance(chapters_subset, list):
                new_chapters_subset = []
                for item in chapters_subset:
                    new_chapters_subset.append(_recursive_process_chapters(item))

            elif isinstance(chapters_subset, str):
                chapter_file_path_str = chapters_subset

                rewritten_chapter_file_path = (
                    self._subset_dir_path / chapter_file_path_str
                ).relative_to(self._src_dir_path)

                self.logger.debug(
                    'Rewriting Markdown file path; ' +
                    f'source: {chapter_file_path_str}, target: {rewritten_chapter_file_path}'
                )

                new_chapters_subset = str(rewritten_chapter_file_path)

            else:
                new_chapters_subset = chapters_subset

            return new_chapters_subset

        new_chapters = _recursive_process_chapters(chapters)

        return new_chapters

    @set_arg_map(
        {
            'project_dir_path': 'path',
            'config_file_name': 'config',
            'no_rewrite_paths': 'norewrite'
        }
    )
    @set_metavars({'subpath': 'SUBPATH'})
    @set_help(
        {
            'subpath': "Path to the subset of the Foliant project",
            'project_dir_path': 'Path to the Foliant project',
            'config_file_name': "Name of config file of the Foliant project, default 'foliant.yml'",
            'no_rewrite_paths': "Do not rewrite the paths of Markdown files in the subset partial config",
            'debug': "Log all events during build. If not set, only warnings and errors are logged"
        }
    )
    def subset(
        self,
        subpath,
        project_dir_path=Path('.'),
        config_file_name='foliant.yml',
        no_rewrite_paths=False,
        debug=False
    ):
        '''Generate the config file to build the project subset from SUBPATH.'''

        self.logger.setLevel(DEBUG if debug else WARNING)

        self.logger.info('Processing started')

        self._project_dir_path = project_dir_path
        self._config_file_name = config_file_name

        self.logger.debug(
            f'Project directory path: {self._project_dir_path}, ' +
            f'config file name: {self._config_file_name}'
        )

        self._neutralization_uuid = str(uuid1()).replace('-', '')

        self.logger.debug(f'UUID to temporarily neutralize special characters: {self._neutralization_uuid}')

        whole_project_partial_config = self._get_whole_project_partial_config()

        self.logger.debug(f'Partial config of the whole project: {whole_project_partial_config}')

        self._src_dir_path = Path(
            {
                **Parser(self._project_dir_path, self._config_file_name, self.logger)._defaults,
                **whole_project_partial_config
            }['src_dir']
        ).expanduser()

        self.logger.debug(f'Project source directory: {self._src_dir_path}')

        self._subset_dir_path = self._get_subset_dir_path(subpath)

        self.logger.debug(f'Subset directory path: {self._subset_dir_path}')

        subset_partial_config = self._get_subset_partial_config()

        self.logger.debug(f'Subset partial config: {subset_partial_config}')

        if not no_rewrite_paths and 'chapters' in subset_partial_config:
            subset_partial_config['chapters'] = self._get_chapters_with_rewritten_paths(
                subset_partial_config['chapters']
            )

        def _recursive_merge_dicts(target_dict_subset, source_dict_subset):
            key = None

            if isinstance(target_dict_subset, dict):
                if isinstance(source_dict_subset, dict):
                    for key in source_dict_subset:
                        if key in target_dict_subset:
                            target_dict_subset[key] = _recursive_merge_dicts(
                                target_dict_subset[key],
                                source_dict_subset[key]
                            )

                        else:
                            target_dict_subset[key] = source_dict_subset[key]

                else:
                    error_message = f'Cannot merge non-dict {source_dict_subset} into dict {target_dict_subset}'

                    self.logger.critical(error_message)

                    raise TypeError(error_message)

            elif isinstance(target_dict_subset, list):
                if isinstance(source_dict_subset, list):
                    target_dict_subset.extend(source_dict_subset)

                else:
                    target_dict_subset.append(source_dict_subset)

            else:
                target_dict_subset = source_dict_subset

            return target_dict_subset

        project_subset_config = _recursive_merge_dicts(whole_project_partial_config, subset_partial_config)

        self.logger.debug(f'Project subset config: {project_subset_config}')

        from oyaml import dump

        project_subset_config_str = str(
            dump(
                project_subset_config,
                allow_unicode=True,
                encoding='utf-8',
                default_flow_style=False,
                indent=4,
                width=1024,
            ),
            encoding='utf-8'
        )

        project_subset_config_str = self._restore_special_characters(project_subset_config_str)

        with open(
            self._project_dir_path / (self._config_file_name + '.subset'), 'w', encoding='utf8'
        ) as project_subset_config_file:
            project_subset_config_file.write(project_subset_config_str)

        self.logger.info('Processing finished')
