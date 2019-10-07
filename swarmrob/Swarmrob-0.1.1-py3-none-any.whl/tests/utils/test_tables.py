import jsonpickle
from unittest import TestCase
from swarmrob.swarmengine import swarm_engine_worker, swarmrob_d, swarm_engine_master, swarm_engine, swarm
from swarmrob.services import service, service_composition
from swarmrob.utils import table_builder


class TestTables(TestCase):
    """
        These test are just for checking if every parameter is defined and if all the tables can be created.
        They don't test the content of the tables.
    """
    def test_table_builder_worker_daemon_status_to_table(self):
        daemon = swarmrob_d.SwarmRobDaemon("lo", None)
        worker = swarm_engine_worker.Worker("foo", "lo")
        daemon.register_worker_at_local_daemon(worker)
        table_builder.worker_daemon_status_to_table(jsonpickle.decode(daemon.get_worker_status_as_json()))

    def test_table_builder_worker_status_to_table(self):
        worker = swarm_engine_worker.Worker("foo", "lo")
        table_builder.worker_status_to_table(jsonpickle.decode(worker.get_info_as_json()))

    def test_table_builder_swarm_status_to_worker_list(self):
        master = swarm_engine_master.Master("lo", "127.0.0.1")
        worker = swarm_engine_worker.Worker("foo", "lo")
        swarm_engine.SwarmEngine().swarm = swarm.Swarm("foo", master)
        master.register_worker_at_master(jsonpickle.encode(master.uuid), jsonpickle.encode(worker))
        table_builder.swarm_status_to_worker_list(jsonpickle.decode(master.get_swarm_status_as_json()))

    def test_table_builder_swarm_status_to_table(self):
        master = swarm_engine_master.Master("lo", "127.0.0.1")
        worker = swarm_engine_worker.Worker("foo", "lo")
        swarm_engine.SwarmEngine().swarm = swarm.Swarm("foo", master)
        master.register_worker_at_master(jsonpickle.encode(master.uuid), jsonpickle.encode(worker))
        table_builder.swarm_status_to_table(jsonpickle.decode(master.get_swarm_status_as_json()))

    def test_table_builder_service_list_to_table(self):
        worker_info = swarm_engine_worker.WorkerInfo("bar", "lo", advertise_address="127.0.0.1", swarm_uuid="foo")
        worker_info.services = [swarm_engine_worker.ServiceInfo("bar", image="hello-world", name="foobar",
                                                                status="exited")]
        table_builder.service_list_to_table(worker_info)

    def test_service_format_service_definition_as_table(self):
        srv = service.Service()
        srv.add_env("KEY", "VALUE")
        srv.add_dependency("MASTER")
        srv.add_deployment("KEY", "VALUE")
        srv.add_volume("SRC", "DST")
        srv.add_device("SRC", "DST")
        srv.format_service_definition_as_table()

    def test_service_composition_format_service_composition_as_table(self):
        srv = service.Service()
        composition = service_composition.ServiceComposition()
        composition.add_service("KEY", srv)
        composition.add_service("KEY2", srv)
        composition.format_service_composition_as_table()
