#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from pkg_resources import resource_exists, resource_filename
from shutil import copytree

from funity import UnityEditor, UnityProject
from funity.util import get_logger

rsc_data = ('funity', 'data/')


class FUnityEditor(UnityEditor):

    @staticmethod
    def __get_package(package: str, resource_name: str) -> str:
        if not resource_exists(package, resource_name):
            raise Exception('Package not found')

        return resource_filename(package, resource_name)

    @staticmethod
    def __import_package(project: UnityProject,
                         pkg_name: str,
                         pkg_dir: str) -> None:
        src_path = Path(pkg_dir)
        asset_path = project.get_assets_path()
        dst_path = asset_path / pkg_name
        if (asset_path / pkg_name).exists():
            raise Exception('Unable to import package')
        copytree(str(src_path), str(dst_path))

    @staticmethod
    def __log(line: str):
        if line.startswith(': >> '):
            get_logger().info(line[:-1])

    def __import_run(self,
                     *args: str,
                     project: UnityProject) -> int:
        pkg_name, pkg_data = rsc_data
        pkg_dir = FUnityEditor.__get_package(package=pkg_name, resource_name=pkg_data)
        FUnityEditor.__import_package(project, pkg_name=pkg_name, pkg_dir=pkg_dir)
        return_code = self.run(*args,
                               '-projectPath', str(project),
                               cli=True,
                               log_func=FUnityEditor.__log)
        project.delete_asset(pkg_name)

        return return_code

    def run_set_serialization_mode(self,
                                   *args: str,
                                   project: UnityProject,
                                   serialization_mode: str) -> int:
        class_name = 'funity.SetSerializationMode'
        if serialization_mode not in ['ForceBinary', 'ForceText', 'Mixed']:
            raise Exception('Invalid SerializationMode')
        return_code = self.__import_run(*args,
                                        '-executeMethod',
                                        f'{class_name}.{serialization_mode}',
                                        project=project)

        return return_code
