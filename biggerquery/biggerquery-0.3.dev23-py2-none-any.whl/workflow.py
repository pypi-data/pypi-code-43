import mock
from unittest import TestCase

DEFAULT_SCHEDULE_INTERVAL = '@daily'


class Workflow(object):
    def __init__(self,
                 definition,
                 schedule_interval=DEFAULT_SCHEDULE_INTERVAL,
                 dt_as_datetime=False):
        self.definition = definition
        self.schedule_interval = schedule_interval
        self.dt_as_datetime = dt_as_datetime

    def run(self, runtime):
        for job in self:
            job.run(runtime=runtime)

    def __iter__(self):
        for job in self.definition:
            yield job


class WorkflowTestCase(TestCase):
    def test_should_run_jobs(self):
        # given
        definition = [mock.Mock() for i in range(100)]
        workflow = Workflow(definition=definition)

        # when
        workflow.run('2019-01-01')

        # then
        for step in definition:
            step.assert_has_calls([mock.call.run(runtime='2019-01-01')])

    def test_should_have_id_and_schedule_interval(self):
        # given
        workflow = Workflow(
            definition=[],
            schedule_interval='@hourly',
            dt_as_datetime=True)

        # expected
        self.assertEqual(workflow.schedule_interval, '@hourly')
        self.assertEqual(workflow.dt_as_datetime, True)