# coding=utf-8
import argparse
import os
import random
import shutil
import subprocess
import sys

import termcolor
import yaml

from dt_shell import UserError
from dt_shell.env_checks import check_docker_environment
from duckietown_challenges import CHALLENGE_PREVIOUS_STEPS_DIR, ChallengeResults
from duckietown_challenges.rest_methods import (
    get_challenge_description,
    dtserver_get_compatible_challenges,
)
from duckietown_challenges.submission_read import read_submission_info
from duckietown_challenges.utils import indent
from .runner import run_single, get_token_from_shell_config
from .submission_build import build_image

usage = """




"""
import logging

logger = logging.getLogger("runner-local")
logger.setLevel(logging.DEBUG)
import traceback


# noinspection PyBroadException
def runner_local_main():
    try:
        runner_local_main_()
    except UserError as e:
        sys.stdout.flush()
        sys.stderr.flush()
        print(termcolor.colored(str(e), "red"))
        sys.exit(1)
    except BaseException:
        sys.stdout.flush()
        sys.stderr.flush()
        s = traceback.format_exc()
        print(termcolor.colored(s, "red"))
        sys.exit(2)


def runner_local_main_():
    from duckietown_challenges.col_logging import setup_logging_color

    setup_logging_color()
    prog = "dts challenges evaluate"
    parser = argparse.ArgumentParser(prog=prog, usage=usage)

    group = parser.add_argument_group("Basic")

    group.add_argument("--no-cache", action="store_true", default=False, help="")

    group.add_argument("--no-build", action="store_true", default=False, help="")
    group.add_argument("--output", default="output-local-evaluation")
    group.add_argument("--impersonate", default=None)

    group.add_argument("--challenge", default=None, help="override challenge")
    parser.add_argument("--debug-volumes", default=None)
    group.add_argument("-C", dest="change", default=None)

    parsed = parser.parse_args()

    logger.debug("Running in directory %s" % os.getcwd())

    if parsed.change:
        os.chdir(parsed.change)
        logger.debug("Changing to directory %s" % os.getcwd())

    token = get_token_from_shell_config()
    path = "."

    sub_info = read_submission_info(path)

    compat = dtserver_get_compatible_challenges(
        token=token,
        impersonate=parsed.impersonate,
        submission_protocols=sub_info.protocols,
    )
    if not compat.compatible:
        msg = (
            "There are no compatible challenges with protocols %s." % sub_info.protocols
        )
        raise UserError(msg)

    dockerfile = os.path.join(path, "Dockerfile")
    if not os.path.exists(dockerfile):
        msg = 'I expected to find the file "%s".' % dockerfile
        raise Exception(msg)

    client = check_docker_environment()

    no_cache = parsed.no_cache
    no_build = parsed.no_build
    do_pull = False

    if parsed.challenge is not None:
        sub_info.challenge_names = parsed.challenge.split(",")

    if sub_info.challenge_names is not None:

        for c in sub_info.challenge_names:
            if c not in compat.available_submit:
                msg = 'The challenge "%s" is not available.' % c
                # msg += '\n available %s' % list(compat.available_submit)
                raise UserError(msg)

            if c not in compat.compatible:
                msg = 'The challenge "%s" is not compatible with the protocol %s.' % (
                    c,
                    sub_info.protocols,
                )
                raise UserError(msg)

    if not sub_info.challenge_names:
        sub_info.challenge_names = compat.compatible

    if len(sub_info.challenge_names) > 1:
        sep = "\n   "
        msg = f"""
This submission can be sent to multiple challenges ({sub_info.challenge_names}).

Therefore, I need you to tell me which challenge to you want to test locally
using the --challenge option.

The options are:  
{sep + sep.join(sub_info.challenge_names)}


For example, you could try:

{prog} --challenge {sub_info.challenge_names[0]}

"""
        raise UserError(msg)

    assert (
        sub_info.challenge_names and len(sub_info.challenge_names) == 1
    ), sub_info.challenge_names

    one = sub_info.challenge_names[0]

    logger.info("I will evaluate challenge %s" % one)
    cd = get_challenge_description(token, one, impersonate=parsed.impersonate)

    tag = "dummy-org/dummy-repo"
    image = build_image(
        client,
        tag=tag,
        path=path,
        dockerfile=dockerfile,
        no_cache=no_cache,
        no_build=no_build,
    )

    caching = False
    solution_container = tag
    SUCCESS = "success"
    steps_ordered = list(sorted(cd.steps))
    logger.info("steps: %s" % steps_ordered)
    for i, challenge_step_name in enumerate(steps_ordered):
        logger.info('Now considering step "%s"' % challenge_step_name)
        step = cd.steps[challenge_step_name]
        evaluation_parameters_str = (
            yaml.safe_dump(step.evaluation_parameters.as_dict())
            + "\ns: %s" % solution_container
        )

        wd_final = os.path.join(parsed.output, challenge_step_name)
        if caching:
            params = os.path.join(wd_final, "parameters.json")
            if os.path.exists(wd_final) and os.path.exists(params):
                if open(params).read() == evaluation_parameters_str:
                    cr_yaml = open(os.path.join(wd_final, "results.yaml"))
                    cr = ChallengeResults.from_yaml(yaml.load(cr_yaml))
                    if cr.status == SUCCESS:
                        logger.info(
                            'Not redoing step "%s" because it is already completed.'
                            % challenge_step_name
                        )
                        logger.info(
                            "If you want to re-do it, erase the directory %s."
                            % wd_final
                        )
                        continue
                    else:
                        msg = (
                            'Breaking because step "%s" was already evaluated with result "%s".'
                            % (challenge_step_name, cr.status)
                        )
                        msg += (
                            "\n"
                            + "If you want to re-do it, erase the directory %s."
                            % wd_final
                        )
                        logger.error(msg)
                        break
                else:
                    logger.info("I will redo the step because the parameters changed.")
                    if os.path.exists(wd_final):
                        shutil.rmtree(wd_final)
        else:
            if os.path.exists(wd_final):
                shutil.rmtree(wd_final)

        wd = wd_final + ".tmp"

        if os.path.exists(wd):
            shutil.rmtree(wd)
        logger.info(f"Using working dir {wd}")
        params_tmp = os.path.join(wd, "parameters.json")
        if not os.path.exists(wd):
            os.makedirs(wd)
        with open(params_tmp, "w") as f:
            f.write(evaluation_parameters_str)

        previous = steps_ordered[:i]
        for previous_step in previous:
            pd = os.path.join(wd, CHALLENGE_PREVIOUS_STEPS_DIR)
            if not os.path.exists(pd):
                os.makedirs(pd)

            d = os.path.join(pd, previous_step)
            # os.symlink('../../%s' % previous_step, d)
            p = os.path.join(parsed.output, previous_step)
            shutil.copytree(p, d)

            mk = os.path.join(d, "docker-compose.yaml")
            if not os.path.exists(mk):
                subprocess.check_call(["find", wd])
                raise Exception()
        aws_config = None
        steps2artefacts = {}
        evaluation_parameters = step.evaluation_parameters
        server_host = None
        project = "project%s" % random.randint(1, 100000)
        cr = run_single(
            wd=wd,
            aws_config=aws_config,
            steps2artefacts=steps2artefacts,
            challenge_parameters=evaluation_parameters,
            solution_container=solution_container,
            challenge_name=one,
            challenge_step_name=challenge_step_name,
            project=project,
            do_pull=do_pull,
            debug_volumes=parsed.debug_volumes,
            submission_id=0,
            timeout_sec=step.timeout,
            server_host=server_host,
        )

        fn = os.path.join(wd, "results.yaml")
        with open(fn, "w") as f:
            res = yaml.dump(cr.to_yaml())
            f.write(res)

        s = ""
        s += "\nStatus: %s" % cr.status
        s += "\nScores:\n\n%s" % yaml.safe_dump(cr.scores, default_flow_style=False)
        s += "\n\n%s" % cr.msg
        logger.info(indent(s, dark("step %s : " % challenge_step_name)))

        os.rename(wd, wd_final)

        if cr.status != SUCCESS:
            logger.error(
                'Breaking because step "%s" has result %s.'
                % (challenge_step_name, cr.status)
            )
            break

    logger.info("Find your output here: %s" % parsed.output)


def dark(x):
    return termcolor.colored(x, attrs=["dark"])


if __name__ == "__main__":
    runner_local_main()
