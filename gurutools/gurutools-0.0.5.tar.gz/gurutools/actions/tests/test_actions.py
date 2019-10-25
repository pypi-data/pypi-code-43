from django.test import TestCase
from example_app.models import Todo
from datetime import date, datetime
from .testutils import (
    assert_in_registry,
    get_instance_action_url,
    get_bulk_action_url
)


class ReadActionsTestCase(TestCase):

    def setUp(self):
        pass

    def test_list_registry(self):
        bulk_actions = [
            'setstatuses'
        ]
        instance_actions = [
            'setstatus'
        ]
        assert_in_registry(self.client, 'todos', bulk_actions, instance_actions)

class MutateActionsTestCase(TestCase):

    def setUp(self):
        self.todo = Todo.objects.create(title='foo', due=date.today(), due_time=datetime.now())
        self.todo2 = Todo.objects.create(title='bar', due=date.today(), due_time=datetime.now())

    def test_perform_instance_action(self):
        url = get_instance_action_url('todos', self.todo.id, 'setstatus')
        data = {'status': 'C'}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)

    def test_perform_legacy_instance_action(self):
        url = get_instance_action_url('todos', self.todo.id, 'setstatus', context='legacy')
        data = {'status': 'C'}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)

    def test_perform_instance_action(self):
        url = get_bulk_action_url('todos', 'setstatuses')
        data = {
            'todos': '{},{}'.format(self.todo.id, self.todo2.id),
            'status': 'C'
        }
        res = self.client.post(url, data)

    def test_legacy_perform_instance_action(self):
        url = get_bulk_action_url('todos', 'setstatuses', context='legacy')
        data = {
            'todos': '{},{}'.format(self.todo.id, self.todo2.id),
            'status': 'C'
        }
        res = self.client.post(url, data)


