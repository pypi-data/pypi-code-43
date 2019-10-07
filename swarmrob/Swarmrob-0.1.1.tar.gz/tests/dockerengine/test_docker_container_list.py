from unittest import TestCase
from swarmrob.dockerengine import docker_container_list


class DummyContainer:

    def __init__(self, status="exited"):
        self.status = status
        self.reload_count = 0
        self.killed = status == "exited"

    def reload(self):
        self.reload_count += 1
        if self.killed:
            self.status = "exited"

    def kill(self):
        self.killed = True


class TestDockerContainerListInit(TestCase):
    def setUp(self):
        self.container_list = default_setup()

    def test_init(self):
        container_list = docker_container_list.DockerContainerList()
        self.assertEqual(0, len(container_list))


class TestDockerContainerListReloadContainers(TestCase):
    def setUp(self):
        self.container_list = default_setup()

    def test_reload_containers(self):
        self.container_list.reload_containers()
        self.assertEqual(1, self.container_list[0].reload_count)
        self.assertEqual(1, self.container_list[1].reload_count)

    def test_multiple_reloads(self):
        self.container_list.reload_containers()
        self.container_list.reload_containers()
        self.assertEqual(2, self.container_list[0].reload_count)
        self.assertEqual(2, self.container_list[1].reload_count)


class TestDockerContainerListStopAllContainers(TestCase):
    def setUp(self):
        self.container_list = default_setup()

    def test_kill_container(self):
        kill_count = self.container_list.stop_all_containers()
        self.assertTrue(self.container_list[0].killed)
        self.assertTrue(self.container_list[1].killed)
        self.assertEqual(1, kill_count)

    def test_multiple_kills(self):
        kill_count = self.container_list.stop_all_containers()
        self.assertEqual(1, kill_count)
        kill_count = self.container_list.stop_all_containers()
        self.assertEqual(0, kill_count)


class TestDockerContainerListGetRunningContainers(TestCase):
    def setUp(self):
        self.container_list = default_setup()

    def test_get_running_containers(self):
        containers = self.container_list.get_running_containers()
        self.assertEqual(1, len(containers))
        self.assertEqual("running", containers[0].status)
        self.assertFalse(containers[0].killed)


def default_setup():
    container_list = docker_container_list.DockerContainerList()
    container_list.append(DummyContainer())
    container_list.append(DummyContainer("running"))
    return container_list
