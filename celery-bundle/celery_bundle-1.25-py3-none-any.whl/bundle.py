from applauncher.kernel import KernelReadyEvent, KernelShutdownEvent, Configuration
from applauncher.kernel import Kernel
from celery import Celery, signals
from celery.signals import celeryd_after_setup
import socket
import inject
import logging


@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    # Do not let celery configure loggers
    return True


class CeleryBundle(object):
    def __init__(self):
        self.logger = logging.getLogger("celery_bundle")
        self.worker = None
        self.config_mapping = {
            "celery": {
                "broker": 'pyamqp://guest@localhost//',
                "name": "",
                "result_backend": "",
                "worker": True,
                "queues":  ["celery"],
                "task_routes": [{
                    "pattern": None,
                    "queue": None
                }],
                "task_serializer": "json",
                "accept_content": ["json"],
                "result_serializer": 'json',
                "result_expires": 3600, # 1 hour
                "timezone": 'Europe/Madrid',
                "concurrency": 0,
                "worker_max_tasks_per_child": -1,
                "broker_pool_limit": 1,
                "broker_heartbeat": 0, # Disabled, put some greater value if you network is not good
                "broker_connection_timeout": 30,
                "event_queue_expires": 60,
                "worker_prefetch_multiplier": 1,
                "quiet": True,
                "without_gossip": True,
                "without_mingle": True
            }
        }

        self.event_listeners = [
            (KernelReadyEvent, self.kernel_ready),
            (KernelShutdownEvent, self.kernel_shutdown)
        ]
        
        self.app = Celery()
        self.injection_bindings = {
             Celery: self.app
        }

    @inject.params(config=Configuration)
    def start_sever(self, config):
        # Register mappings
        kernel = inject.instance(Kernel)
        for bundle in kernel.bundles:
            if hasattr(bundle, "register_tasks"):
                getattr(bundle, "register_tasks")()
        tasks_per_child = config.celery.worker_max_tasks_per_child
        if tasks_per_child == -1:
            tasks_per_child = None

        if config.celery.broker_heartbeat <= 0:
            broker_hearthbeat = None
        else:
            broker_hearthbeat = config.celery.broker_heartbeat

        self.app.conf.update(
            broker_url=config.celery.broker,
            result_backend=config.celery.result_backend,
            task_track_started=True,
            result_expires=config.celery.result_expires,
            task_serializer=config.celery.task_serializer,
            accept_content=config.celery.accept_content,  # Ignore other content
            result_serializer=config.celery.task_serializer,
            timezone=config.celery.timezone,
            enable_utc=True,
            task_acks_late=True,
            worker_max_tasks_per_child=tasks_per_child,
            broker_pool_limit=config.celery.broker_pool_limit,
            broker_heartbeat=broker_hearthbeat,
            broker_connection_timeout=config.celery.broker_connection_timeout,
            event_queue_expires=config.celery.event_queue_expires,
            worker_prefetch_multiplier=config.celery.worker_prefetch_multiplier
        )

        if len(config.celery.task_routes) > 0:
            task_routes = {}
            for route in config.celery.task_routes:
                task_routes[route.pattern] = route.queue
            self.app.conf.update({"task_routes": task_routes})

        if config.celery.worker:
            self.logger.info("Starting worker")
            params = {
                'pool_cls': 'prefork', 
                'quiet': True,
                'detach': False, 
                'optimization': None, 
                'prefetch_multiplier': 1, 
                'concurrency': config.celery.concurrency,
                'pool': 'prefork', 
                'task_events': True, 
                'max_tasks_per_child': 50, 
                'max_memory_per_child': None, 
                'purge': False, 
                'queues': ",".join(config.celery.queues),
                'exclude_queues': [], 'include': [], 
                'without_gossip': config.celery.without_gossip,
                'without_mingle': config.celery.without_mingle,
                'without_heartbeat': broker_hearthbeat is None,
                'heartbeat_interval': broker_hearthbeat,
                'autoscale': None, 
                'umask': None, 
                'executable': None, 
                'beat': False, 
                'schedule_filename': 'celerybeat-schedule', 
                'scheduler': None
            }
            if len(config.celery.name) == 0:
                config.celery.name = socket.gethostname()

            self.worker = self.app.Worker(hostname=f"{config.celery.name}@{socket.gethostname()}", **params)
            self.logger.info("Worker started")
            self.worker.start()
        else:
            self.logger.info("Running as client only")

    @inject.params(kernel=Kernel)
    def kernel_ready(self, event, kernel):
        config = inject.instance(Configuration).celery
        if config.worker:
            kernel.run_service(self.start_sever)
        else:
            self.start_sever()

    def kernel_shutdown(self, event):
        if self.worker:
            self.logger.info("Stopping worker")
            self.worker.stop()
            self.logger.info("Worker has been stoped") 
