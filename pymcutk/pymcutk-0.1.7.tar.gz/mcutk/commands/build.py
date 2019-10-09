from __future__ import print_function
import os
import csv
import sys
import click
import glob
import logging
import platform
from os.path import join

from mcutk.apps import appfactory
from mcutk.exceptions import ProjectNotFound
from mcutk.projects_scanner import find_projects, TOOLCHAINS

# from ._settings import TOOLCHAINS, EXCLUDE_DIR_NAME
from mcutk.managers.conf_mgr import ConfMgr


def _get_ides(ides):
    # apps conifguration from config file
    ide_apps = dict()
    os_name = platform.system()
    get_app = ConfMgr.load().get_app

    for tool_name in ides:
        info = get_app(tool_name)
        tool_class = appfactory(tool_name)

        app = None
        if info:
            app = tool_class(**info)
        elif os_name in tool_class.OSLIST:
            app = tool_class.get_latest()

        if app and app.is_ready:
            ide_apps[tool_name] = app
        else:
            ide_apps[tool_name] = None

    return ide_apps


def _project_operation(app, project, target, log, list, recursive):
    target = project.map_target(target)
    msg = '  => {}'.format(target)

    click.echo(msg)
    ret = app.build_project(project, target, log)
    color_table = { 0: "green", 1: "red", 2: "yellow" }
    color = color_table.get(ret.value)

    if log:
        click.echo('     - LOG: %s'%log)

    click.secho('     - BUILD %s'%ret.name, fg=color)
    if ret.value in (0, 2):
        click.echo('     - OUTPUT %s'%ret.output)

    return ret.name


def _dump_to_csv(data):
    keys = data[0].keys()
    csvfile = 'mcutk_build.csv'
    print ('dumped to file %s'%csvfile)
    with open(csvfile, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)





@click.command('build',
    short_help='find and build project',
    help="build projects with specific path",
    epilog="supported toolchains: %s"%TOOLCHAINS)
@click.argument('path', default=".", type=click.Path(exists=True))
@click.option('-t', '--target', help='set target name, if not specificed, the first known target is used')
@click.option('-l', '--log', type=click.Path(), help='specifies the output log file')
@click.option('-v', '--verbose', is_flag=True, help='show more console message')
@click.option('--no-build', 'no_build', is_flag=True, help='list project information only, not execute build!')
@click.option('-r', '--recursive', is_flag=True, default=False, help='recursive the directory and build all configuration')
@click.option('--include-tools', 'include_tools', nargs=1, help='specific toolchains, multiple value need to join with \",\", recursive mode only')
@click.option('--exclude-tools', 'exclude_tools', nargs=1, help='exlcude toolchains, multiple value need to join with \",\", recursive mode only')
@click.option('--results-csv', 'result2csv', is_flag=True, help='dump results to CSV format')
def cli(path, target, log, verbose, no_build, recursive, include_tools, exclude_tools, result2csv):
    """Find and build projects"""
    if recursive:
        print("recursive mode: true, log will be saved to project root directory.")

    if include_tools:
        include_tools = include_tools.split(',')
        print("include-tools: %s"%str(include_tools))

    if exclude_tools:
        exclude_tools = exclude_tools.split(',')
        print("exclude-tools: %s"%str(exclude_tools))

    project_root = path
    projects, count = find_projects(project_root, recursive, include_tools, exclude_tools)

    if not projects:
        click.secho('Error: not found projects', fg='red', err=True)
        return

    click.echo("Toolchains configuration: ")

    ide_apps = _get_ides(projects.keys())
    for name, ideapp in ide_apps.items():
        if ideapp:
            click.secho(' + {0:<10} | v={1:<20} | p=\"{2}\"'.format(ideapp.name, ideapp.version, ideapp.path), fg="green")
        else:
            click.echo(" - Warning: %s is unavaliable."% name)

    click.echo("\n============================= build session starts =============================")

    results = list()
    c = 1

    for toolname, plist in projects.items():
        for project in plist:
            click.echo('[{}/{}] Building {} - {}, project: {}'.format(c, count, project.idename, project.name, project.prjpath))
            c += 1
            if no_build:
                click.echo(' avaliable targets')
                for tname in project.targets:
                    click.echo('  - %s'% tname)
                continue

            if target:
                targets_to_build = [target]
            elif recursive and not target:
                targets_to_build = project.targets
            else:
                targets_to_build = [project.targets[0]]

            for target_name in targets_to_build:
                ideapp = ide_apps.get(project.idename)
                if not ideapp:
                    click.secho('Error: %s have no configuration, skip'%project.idename, fg='red')
                    continue

                if recursive:
                    log = os.path.join(project.prjdir, "build_" + target_name.replace(" ", "_") + ".log").replace('\\', '/')

                r = _project_operation(ideapp, project, target_name, log, list, recursive)
                ret = {
                    "name": project.name,
                    "toolchain": project.idename,
                    "target": target_name,
                    "result": r,
                    "log": log
                }

                results.append(ret)

    if result2csv:
        _dump_to_csv(results)

