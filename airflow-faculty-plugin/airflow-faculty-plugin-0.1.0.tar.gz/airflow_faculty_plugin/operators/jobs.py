import os
import time

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator

import faculty
from faculty.clients.job import RunState

COMPLETED_RUN_STATES = {
    RunState.COMPLETED,
    RunState.FAILED,
    RunState.CANCELLED,
    RunState.ERROR,
}


class FacultyJobRunNowOperator(BaseOperator):
    """
    :param job_id                       The Faculty job id
    :type job_id                        string
    :param job_parameter_values         The parameters to be passed into the job run
    :type job_parameter_values          dict
    :param polling_period_seconds       The time to wait between polling to get the job run status
    :type polling_period_seconds        int
    :param project_id                   The project id for the job.
    :type project_id                    string
    """

    ui_color = "#00aef9"
    ui_fgcolor = "#fff"

    def __init__(
        self,
        job_id,
        job_parameter_values=None,
        polling_period_seconds=30,
        project_id=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.job_id = job_id

        if job_parameter_values is not None:
            self.job_parameter_values = job_parameter_values
        else:
            self.job_parameter_values = {}

        self.polling_period_seconds = polling_period_seconds

        if project_id is not None:
            self.project_id = project_id
        else:
            self.project_id = os.environ["FACULTY_PROJECT_ID"]

    def execute(self, context):
        """
        Triggers a run of a Faculty job based on the job id and parameters
        passed in
        """
        log = self.log
        project_id = self.project_id
        job_id = self.job_id
        job_parameter_values = self.job_parameter_values

        # Trigger job run parameters
        job_client = faculty.client("job")
        log.info(
            f"Creating a job run for job {job_id} parameters {job_parameter_values}."
        )
        run_id = job_client.create_run(
            project_id, job_id, [job_parameter_values]
        )
        log.info(
            f"Triggered job {job_id} with run id {run_id} and parameters {job_parameter_values}."
        )

        while True:
            run_info = job_client.get_run(project_id, job_id, run_id)
            run_state = run_info.state
            if run_state in COMPLETED_RUN_STATES:
                if run_state == RunState.COMPLETED:
                    log.info(
                        f"Job {job_id} and run {run_id} completed successfully."
                    )
                    break

                else:
                    raise AirflowException(
                        f"Job {job_id} and run {run_id} failed with terminal state: {run_state}"
                    )
            else:
                log.info(
                    f"Job {job_id} and run {run_id} in run state: {run_state}"
                )
                log.info(
                    f"Sleeping for {self.polling_period_seconds} seconds."
                )
                time.sleep(self.polling_period_seconds)

    def on_kill(self):
        """
        Cancels the job run on Faculty
        """
        # TODO: Use the Faculty job client to cancel the run.
        raise NotImplementedError
