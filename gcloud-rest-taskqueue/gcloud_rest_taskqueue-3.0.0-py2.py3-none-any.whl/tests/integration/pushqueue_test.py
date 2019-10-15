from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from datetime import datetime
from datetime import timedelta

import pytest
from future.utils import text_to_native_str

#@pytest.mark.asyncio
def test_task_lifecycle_in_push_queue(push_queue_context):
    tq = push_queue_context['queue']

    # Set to run in the future, giving us enough time to test all
    # functionalities before the task gets dispatched automatically.
    schedule_time = datetime.utcnow() + timedelta(days=1)

    task = {
        'scheduleTime': '{}Z'.format(
            schedule_time.isoformat(text_to_native_str('T'))),
        'appEngineHttpRequest': {
            'httpMethod': 'POST',
            # something that we know won't work,
            # so that 'run' task operation doesn't end up deleting the task.
            'relativeUri': '/some/test/uri',
        }
    }

    # CREATE
    created = tq.create(task)
    assert created

    # Add created task (and the queue to delete it from) to the tasks list
    # so the teardown will clean it up regardless of what happens.
    push_queue_context['tasks_to_cleanup'].append(created)

    # GET
    assert created == tq.get(created['name'], full=True)

    # LIST
    listed = tq.list(full=True)
    assert listed.get('tasks')
    assert created in listed['tasks']

    # RUN
    run = tq.run(created['name'], full=True)
    assert all(item in run.items() for item in created.items())

    # DELETE
    assert not tq.delete(created['name'])

    # Created task has been deleted successfully, so remove it from the list to
    # avoid unnecessary delete attempt in teardown.
    push_queue_context['tasks_to_cleanup'].remove(created)
