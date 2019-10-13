#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from datetime import datetime
from json import dumps, loads
from os import chdir, getcwd, walk
from pathlib import Path
from platform import system
from shutil import copyfile, move, rmtree
from subprocess import PIPE, STDOUT, Popen
from typing import Callable, List


def __find_func_darwin(search_dir: str) -> List[str]:
    search_path = Path(search_dir)
    editor_dirs = []
    for root, dirs, _ in walk(search_path):
        root_path = Path(root)
        if not root_path.name == 'Unity.app':
            continue
        dirs[:] = []
        editor_dirs.append(str(root_path.parent))

    return editor_dirs


def __find_func_linux(search_dir: str) -> List[str]:
    search_path = Path(search_dir)
    editor_dirs = []
    for root, dirs, files in walk(search_path):
        root_path = Path(root)
        if 'Editor' != root_path.name:
            continue
        if 'Unity' not in files:
            continue
        dirs[:] = []
        editor_dirs.append(str(root_path.parent))

    return editor_dirs


def __find_func_windows(search_dir: str) -> List[str]:
    search_path = Path(search_dir)
    editor_dirs = []
    for root, dirs, files in walk(search_path):
        root_path = Path(root)
        if 'Editor' != root_path.name:
            continue
        if 'Unity.exe' not in files:
            continue
        dirs[:] = []
        editor_dirs.append(str(root_path.parent))

    return editor_dirs


unity_platform = {
    'Darwin': {
        'exec': 'Unity.app/Contents/MacOS/Unity',
        'data': 'Unity.app/Contents',
        'libcache': [
            'Unity.app/Contents/Managed/UnityEngine',
            'Unity.app/Contents/Resources/PackageManager/ProjectTemplates/libcache',
        ],
        'mono_bin': 'Unity.app/Contents/MonoBleedingEdge/bin',
        'mcs': 'Unity.app/Contents/MonoBleedingEdge/bin/mcs',
        'find': (
            __find_func_darwin, [
                '/Applications',
            ]
         ),
    },
    'Linux': {
        'exec': 'Editor/Unity',
        'data': 'Editor/Data',
        'libcache': [
            'Editor/Data/Managed/UnityEngine',
            'Editor/Data/Resources/PackageManager/ProjectTemplates/libcache',
        ],
        'mono_bin': 'Editor/Data/MonoBleedingEdge/bin',
        'mcs': 'Editor/Data/MonoBleedingEdge/bin/mcs',
        'find': (
            __find_func_linux, [
                '/opt',
            ]
         ),
    },
    'Windows': {
        'exec': 'Editor/Unity.exe',
        'data': 'Editor/Data',
        'libcache': [
            'Editor/Data/Managed/UnityEngine',
            'Editor/Data/Resources/PackageManager/ProjectTemplates/libcache',
        ],
        'mono_bin': 'Editor/Data/MonoBleedingEdge/bin',
        'mcs': 'Editor/Data/MonoBleedingEdge/bin/mcs.bat',
        'find': (
            __find_func_windows, [
                'C:/Program Files',
                'C:/Program Files (x86)',
            ]
         ),
    },
}


class UnityEditor(object):

    path: Path
    exec: Path
    mcs: Path

    def __init__(self, editor_dir: str):
        sys = system()
        self.path = Path(editor_dir)
        self.exec = self.path / unity_platform[sys]['exec']
        self.mcs = self.path / unity_platform[sys]['mcs']

        if not self.exec.exists():
            raise Exception('Executable not found')

    def __repr__(self):
        return str(self.path)

    @staticmethod
    def __run_process(command: List[str],
                      log_func: Callable[[str], None] = None) -> int:
        if log_func is not None:
            log_func(f': >> Running subprocess.. {" ".join(command)}\n')
        with Popen(command,
                   stderr=STDOUT,
                   stdout=PIPE,
                   universal_newlines=True) as process:
            if log_func is not None:
                for line in process.stdout:
                    log_func(f': {line}')
        return_code = process.returncode
        if log_func is not None:
            log_func(f': >> Subprocess finished with exit code {return_code}\n')

        return return_code

    @staticmethod
    def find_all(*args: str) -> List[UnityEditor]:
        sys = system()
        if sys not in unity_platform.keys():
            raise NotImplementedError
        func, dirs = unity_platform[sys]['find']
        search_dirs = []
        search_dirs.extend(dirs if len(args) == 0 else
                           list(filter(lambda p: Path(p).is_dir(), args)))
        editor_dirs = []
        for d in search_dirs:
            editor_dirs.extend(func(d))
        editors = [UnityEditor(e) for e in editor_dirs]

        return editors

    @staticmethod
    def find_in(*args: str,
                cache: str = None) -> List[UnityEditor]:
        if cache is not None:
            cache_path = Path(cache)
            if cache_path.exists():
                editor_dirs = loads(cache_path.read_text())
                return [UnityEditor(e) for e in editor_dirs]
            else:
                editors = UnityEditor.find_all(*args)
                editor_dirs = [str(e) for e in editors]
                cache_path.touch()
                cache_path.write_text(dumps(editor_dirs, indent=2))
                return editors
        else:
            return UnityEditor.find_all(*args)

    @staticmethod
    def find_libcache(editor: UnityEditor) -> List[str]:
        return [str(editor.path / d) for d in unity_platform[system()]['libcache']]

    @staticmethod
    def find_libs(editor: UnityEditor) -> List[str]:
        libs = {}
        for d in editor.get_libcache():
            libcache_path = Path(d)
            for root, _, files in walk(str(libcache_path)):
                root_path = Path(root)
                for f in files:
                    file_path = Path(f)
                    if not '.dll' == file_path.suffix:
                        continue
                    file_name = str(file_path.name)
                    if file_name in libs.keys():
                        continue
                    libs[file_name] = str(root_path / file_path)

        return list(libs.values())

    def compile(self, *args: str,
                defines: List[str] = None,
                debug: bool = False,
                doc: str = None,
                nostdlib: bool = False,
                nowarn: List[str] = None,
                optimize: bool = False,
                out: str = None,
                references: List[str] = None,
                stacktrace: bool = False,
                target: str = None,
                unsafe: bool = False,
                warnaserror: List[str] = None,
                log_func: Callable[[str], None] = None) -> int:
        cwd_path = Path(getcwd())
        tmp_path = cwd_path / f'tmp-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        tmp_path.mkdir()
        command = [str(self.mcs)]
        if defines is not None:
            command.append(f'-d:{";".join(defines)}')
        if debug:
            command.append('-debug')
        if doc is not None:
            command.append(f'-doc:{doc}')
        if nostdlib:
            command.append('-nostdlib')
        if nowarn is not None:
            command.append(f'-nowarn:{",".join(nowarn)}')
        if optimize:
            command.append('-optimize')
        if out is not None:
            command.append(f'-out:{out}')
        refs = []
        for r in references if references is not None else []:
            r_path = Path(r)
            if r_path.exists():
                r_name = r_path.name
                copyfile(str(r_path), str(tmp_path / r_name))
                refs.append(r_name)
        if len(refs) > 0:
            command.append(f'-r:{",".join(refs)}')
        if stacktrace:
            command.append('--stacktrace')
        if target is not None and target in ['exe', 'library', 'module', 'winexe']:
            command.append(f'-t:{target}')
        if unsafe:
            command.append('-unsafe')
        if warnaserror is not None:
            command.append(f'-warnaserror:{",".join(warnaserror)}')
        for f in args:
            f_path = Path(f)
            if f_path.exists():
                f_name = f_path.name
                copyfile(str(f_path), str(tmp_path / f_name))
        command.append('*.cs')
        try:
            chdir(str(tmp_path))
            return_code = UnityEditor.__run_process(command, log_func=log_func)
            if return_code == 0:
                out_path = tmp_path / out
                if out_path.exists():
                    move(str(out_path), str(cwd_path / out))
                doc_path = tmp_path / doc
                if doc_path.exists():
                    move(str(doc_path), str(cwd_path / doc))
        finally:
            chdir(str(cwd_path))
            rmtree(str(tmp_path), ignore_errors=True)

        return return_code

    def get_libcache(self) -> List[str]:
        return UnityEditor.find_libcache(self)

    def get_libs(self) -> List[str]:
        return UnityEditor.find_libs(self)

    def run(self, *args: str,
            cli: bool = True,
            log_func: Callable[[str], None] = None) -> int:
        command = [str(self.exec)]
        command.extend(args)
        if cli:
            for o in ['-batchmode', '-nographics', '-quit', '-silent-crashes']:
                if o not in command:
                    command.append(o)

        return UnityEditor.__run_process(command, log_func=log_func)
