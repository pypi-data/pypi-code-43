"""
the scheduler queries the database and docker to understand the state of the world
it is responsible for
    - keeping the database and docker in sync by starting containers as necessary
    - triggering work as it is required
"""

from blowpipe import App
import json
import time
import uuid
from blowpipe import constants
from blowpipe import docker_utils
from blowpipe.logger import Logger
from datetime import datetime


class Report(object):
    """
    The Report is the result of a single execute call by the scheduler
    """
    def __init__(self):
        self.workflows_running = []
        self.workflows_completed = []
        self.workflows_failed = []
        self.workflows_manually_triggered = []
        self.workflows_schedule_triggered = []
        self.event_triggered = []
        self.steps_completed = []
        self.steps_running = []
        self.steps_started = []


class Scheduler(object):
    def __init__(self, server):
        self.tick = 0
        self.name = "Scheduler"
        self._quit = False
        self.server = server
        self._is_running = False
        self.logger = Logger("Scheduler")
        self.SLEEP_SECONDS = 0.1

    def execute(self):
        """
        Runs the check() then sleeps for SLEEP_SECONDS
        repeats until quit == True
        :return:
        """

        self._is_running = True
        while not self._quit:
            try:
                report = self.check()
            except Exception as e:
                self.logger.error("execute()", e)
            time.sleep(self.SLEEP_SECONDS)
        self._is_running = False
        return report

    def is_running(self):
        return self._is_running

    def quit(self):
        self._quit = True

    def on_quit(self):
        """
        called by the threadpool when it has finished
        :return:
        """
        self.logger.debug("on_quit()")

    def check(self):
        """
        runs a single pass of the scheduler, syncing
        against docker, triggering any jobs that require it etc.
        :return:
        """
        self.tick += 1
        logger = self.logger
        logger.indent()
        db = self.server.get_db()
        report = Report()
        session = db.create_session()
        LOG_PREFIX = ".check(" + str(self.tick) + ") "
        try:
            workflow_instances = db.get_running_workflows(session, is_active_only=True)
            for workflow_instance in workflow_instances:
                workflow = workflow_instance.get_workflow()
                workflow_dirty = False

                if workflow_instance.state == constants.STATE_TRIGGER_MANUAL:
                    logger.debug(LOG_PREFIX+"manually triggered, running first steps.")
                    report.workflows_manually_triggered.append(workflow)
                    self.find_and_start_first_steps(workflow_instance, report, session)
                    workflow_instance.state = constants.STATE_IN_PROGRESS
                    workflow_dirty = True
                elif workflow_instance.state == constants.STATE_TRIGGER_SCHEDULE:
                    logger.debug(LOG_PREFIX+"schedule triggered, running first steps.")
                    report.workflows_schedule_triggered.append(workflow)
                    self.find_and_start_first_steps(workflow_instance, report, session)
                    workflow_instance.state = constants.STATE_IN_PROGRESS
                    workflow_dirty = True
                else:
                    running_steps = workflow.get_running_steps()
                    steps_updated = False
                    steps_started = False
                    for step in running_steps:
                        c_info = docker_utils.get_container_info(step)

                        if constants.DEBUG and constants.DEBUG_DOCKER_RESPONSE:
                            filename = "docker-response-" + str(uuid.uuid4()) + ".json"
                            logger.info(LOG_PREFIX+"(constants.DEBUG_DOCKER_RESPONSE=True) WRITING DOCKER RESPONSE as FILE " + filename)
                            f = open(filename, 'w')
                            f.write(json.dumps(c_info.data, indent=4))
                            f.close()

                        step.set_container_info(c_info)

                        if c_info.is_container_complete():
                            logger.debug(LOG_PREFIX+"step '" + step.get_name() + "' docker container is complete")
                            # then it has just finished from docker; mark it as finished here
                            step.set_state(constants.STATE_COMPLETE)
                            step.set_container_info(c_info)
                            report.steps_completed.append(step)
                            steps_updated = True
                            workflow_dirty = True
                        else:
                            logger.debug(LOG_PREFIX+"step '" + step.get_name() + "' docker container is not complete")
                            report.steps_running.append(step)

                    ready_to_run_steps = workflow.get_ready_to_run_steps()
                    for step in ready_to_run_steps:
                        logger.debug(LOG_PREFIX+"step '" + step.get_name() + "' is ready to run.")
                        self.start_step(step)
                        workflow_dirty = True
                        steps_started = True

                    # now work out if all steps are complete

                    all_steps = workflow.get_all_steps()
                    workflow_complete = True
                    for step in all_steps:
                        if not step.is_complete():
                            workflow_complete = False
                            workflow_dirty = True
                            break

                    if workflow_complete:
                        logger.debug(LOG_PREFIX+"- all steps completed, marking workflow as complete.")

                        # then this is complete
                        workflow.set_state(constants.STATE_COMPLETE)
                        workflow_instance.finished = datetime.today()
                        workflow_instance.is_active = False
                        workflow_instance.state = constants.STATE_COMPLETE
                        workflow_dirty = True
                        report.workflows_completed.append(workflow_instance)
                    else:
                        logger.debug(LOG_PREFIX+"- not all steps completed, workflow still running.")
                        report.workflows_running.append(workflow_instance)

                if workflow_dirty:
                    workflow_instance.save(session)

        except Exception as e:
            print(e)
            logger.error(LOG_PREFIX+"exception: ", e)

        finally:
            session.commit()
            session.close()

        self.logger.unindent()
        return report

    def find_and_start_first_steps(self, workflow_instance, report, session):
        workflow = workflow_instance.get_workflow()
        for step in workflow.get_all_steps():
            if step.is_root():
                self.logger.debug(".find_and_start_first_steps() step is '" + step.get_name() + "'")
                self.start_step(step)
                report.steps_started.append(step)

    def start_step(self, step):
        if step.is_enabled():
            self.logger.debug(".start_step(" + step.get_name() + ") enabled true, running.")
            container_name = step.get_image_name() + "-" + str(uuid.uuid4())
            container_name = container_name.replace(":", "_")
            container_name = container_name.replace("/", "-")
            container_name = container_name.replace("\\", "-")
            env_vars = step.environment()
            step.set_container_name(container_name)
            response = docker_utils.start_step(step, env_vars)
            step.set_started(datetime.today())
            step.set_state(constants.STATE_IN_PROGRESS)
            self.logger.debug(".start_step(" + step.get_name() + ") started, state set to " + constants.STATE_IN_PROGRESS)
        else:
            self.logger.debug(".start_step(" + step.get_name() + ") enabled false, not running.")
