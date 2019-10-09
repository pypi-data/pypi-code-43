from __future__ import print_function
import os
import logging
import time
import click
from collections import defaultdict
from mcutk.apps import appfactory
from mcutk.exceptions import ProjectNotFound, ProjectParserError
from globster import Globster
from xml.etree import cElementTree as ET

TOOLCHAINS = [
    'iar',
    'mdk',
    'mcux',
    'armgcc',
    'lpcx',
    'xcc'
]


EXCLUDE_DIR_NAME = [
    'log/',
    'debug/',
    'obj/',
    'release/',
    '.debug/',
    '.release/',
    'RTE/',
    'settings/'
    '.git/',
    '__pycache__/',
    'flexspi_nor_debug/',
    'flexspi_nor_release/'
]

IDE_INS = [appfactory(toolname) for toolname in TOOLCHAINS]

def identify_project(path, toolname=None):
    """ Identify and return initiliazed project instance.

    Arguments:
        path {str} -- project path

    Keyword Arguments:
        toolname {str} -- if toolname is given, it will try to load
            the project with the tool. (default: None)

    Returns:
        Project object
    """
    if toolname:
        cls = appfactory(toolname)
        return cls.Project.frompath(path)

    prj = None
    for cls in IDE_INS:
        try:
            prj = cls.Project.frompath(path)
            break
        except ProjectParserError as e:
            logging.warning(str(e))
        except ET.ParseError as e:
            logging.error("Bad project: %s, Reason: %s", path, e)
        except ProjectNotFound:
            pass

    return prj


def find_projects(root_dir, recursive=True, include_tools=None, exclude_tools=None):
    """Find projects in specific directory.

    Arguments:
        root_dir {string} -- root directory
        recursive {bool} -- recursive mode
        include_tools {list} -- only include specifices tools
        exclude_tools {list} -- exlucde specifices tools
    Returns:
        {dict} -- key: toolchain name, value: a list of Project objects.

    Example:
        >> ps = find_projects("C:/code/mcu-sdk-2.0", True)
        >> ps
        {
            'iar': [<Project Object at 0x1123>, <Project Object at 0x1124>],
            'mdk': [<Project Object at 0x1123>, <Project Object at 0x1124>],
            ...
        }

    """

    projects = defaultdict(list)
    g = Globster(EXCLUDE_DIR_NAME)
    print('Process scanning')
    s_time = time.time()

    project = identify_project(root_dir)
    if project:
        projects[project.idename].append(project)

    if recursive:
        for root, folders, _ in os.walk(root_dir):
            for folder in folders:
                if g.match(folder):
                    continue

                path = os.path.join(root, folder)
                project = identify_project(path)
                if (project and project.idename != "mcux") or (hasattr(project, "is_enabled") and (project.is_enabled)):
                    projects[project.idename].append(project)

    if projects:
        if include_tools:
            projects = {k: v for k, v in projects.items()
                        if k in include_tools}

        elif exclude_tools:
            for toolname in exclude_tools:
                if toolname in projects:
                    projects.pop(toolname)

    e_time = time.time()

    count = 0
    for toolname, prjs in projects.items():
        length = len(prjs)
        count += length

    click.echo("Found projects total {0}, cover {1} toolchains. Used {2:.2f}(s)".format(
        count, len(projects), e_time-s_time))

    for toolname, prjs in projects.items():
        length = len(prjs)
        click.echo(" + {0:<10}  {1}".format(toolname, length))

    return projects, count
