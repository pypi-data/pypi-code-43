"""
Main entrypoint for ocupgrader.
"""

import argparse
import logging
import os
from sh import ErrorReturnCode
import re
import sys

from ocdeployer.utils import oc, load_cfg_file
import yaml

from .schema import validate_schema

ocdeployer_log_level = os.getenv("OCDEPLOYER_LOG_LEVEL", "WARN")
logging.basicConfig(level=getattr(logging, ocdeployer_log_level))

log = logging.getLogger("ocupgrader")
log.level = logging.INFO


def set_oc_project(args):
    try:
        oc("project", args.project, _reraise=True)
    except ErrorReturnCode:
        log.error("You should log in to your cluster before upgrading and make sure you can access specified project:")
        log.error("  $ oc login https://api.myopenshift --token=*************")
        log.error("  $ oc project %s", args.project)
        sys.exit(2)


def get_project_spec(args):
    try:
        return load_cfg_file(args.file)
    except ValueError as e:
        log.error(e)
        sys.exit(3)


def list_tasks(args, project_spec):
    log.info("Available tasks:")
    for task_name in project_spec["tasks"]:
        log.info("  %s (%s)", task_name, project_spec["tasks"][task_name]["description"])


def replace_params(arg, params):
    def matchrepl(matchobj):
        return params.get(matchobj.group(1), "{{ %s }}" % matchobj.group(1))
    return re.sub(r'{{ (.+) }}', matchrepl, arg)


def run_task(args, project_spec):
    task_name = args.task
    if task_name in project_spec["tasks"]:
        required_params = project_spec["tasks"][task_name].get("parameters")
        parsed_params = {}
        if required_params:
            if args.parameters:
                for param in args.parameters.split(","):
                    param_parts = param.split("=")
                    parsed_params[param_parts[0]] = param_parts[1]
                for required_param in required_params:
                    if required_param not in parsed_params:
                        log.error("Required parameters: %s", required_params)
                        sys.exit(6)
            else:
                log.error("Required parameters: %s", required_params)
                sys.exit(6)
        log.info("Executing task: %s", task_name)
        for command in project_spec["tasks"][task_name]["commands"]:
            if command.get("description"):
                log.info(command["description"])
            args = command["args"]
            args = [replace_params(arg, parsed_params) for arg in args]
            output = oc(*args)
            if output:
                log.info("\n%s" % output)
        log.info("Task executed successfuly.")
    else:
        log.error("Task doesn't exist in project spec: '%s'", task_name)
        sys.exit(5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", action="store", help="target OpenShift project")
    parser.add_argument("-f", "--file", action="store", default="ocupgrader.yml",
                        help="project file with upgrade tasks specification (default: '%(default)s')")
    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.add_parser("list-tasks", help="list available tasks")
    run_parser = subparsers.add_parser("run", help="run given task")
    run_parser.add_argument("task", help="task name")
    run_parser.add_argument("-p", "--parameters", action="store", help="task parameters")
    args = parser.parse_args()
    
    set_oc_project(args)
    project_spec = get_project_spec(args)
    if not validate_schema(project_spec):
        log.error("Error validating project spec.")
        sys.exit(4)

    if args.subcommand == "run":
        run_task(args, project_spec)
    elif args.subcommand == "list-tasks":
        list_tasks(args, project_spec)
    else:
        log.error("No subcommand specified. Nothing to do.")
        sys.exit(1)

if __name__ == "__main__":
    main()
