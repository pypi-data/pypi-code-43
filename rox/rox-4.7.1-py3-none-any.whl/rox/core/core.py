from concurrent.futures import ThreadPoolExecutor
from threading import Event
from datetime import datetime, timedelta
import threading
import re

from rox.core.analytics.client_proxy import ClientProxy
from rox.core.client.buid import BUID
from rox.core.client.dynamic_api import DynamicApi
from rox.core.client.internal_flags import InternalFlags
from rox.core.configuration.configuration_fetched_invoker import ConfigurationFetchedInvoker, FetcherStatus
from rox.core.configuration.configuration_parser import ConfigurationParser
from rox.core.consts.environment import Environment
from rox.core.entities.flag_setter import FlagSetter
from rox.core.impression.impression_invoker import ImpressionInvoker
from rox.core.network.state_sender import StateSender
from rox.core.network.configuration_fetcher import ConfigurationFetcher
from rox.core.network.configuration_fetcher_roxy import ConfigurationFetcherRoxy
from rox.core.network.request import Request
from rox.core.notifications.notification_listener import NotificationListener
from rox.core.register.registerer import Registerer
from rox.core.reporting.error_reporter import ErrorReporter
from rox.core.repositories.custom_property_repository import CustomPropertyRepository
from rox.core.repositories.experiment_repository import ExperimentRepository
from rox.core.repositories.flag_repository import FlagRepository
from rox.core.repositories.roxx.experiments_extensions import ExperimentsExtensions
from rox.core.repositories.roxx.properties_extensions import PropertiesExtensions
from rox.core.repositories.target_group_repository import TargetGroupRepository
from rox.core.roxx.parser import Parser
from rox.core.security.signature_verifier import SignatureVerifier
from rox.core.utils import periodic_task
from rox.core.utils.aggregate_event import AggregateEvent
from rox.core.logging.logging import Logging

class Core:
    def __init__(self):
        self.flag_repository = FlagRepository()
        self.custom_property_repository = CustomPropertyRepository()
        self.target_group_repository = TargetGroupRepository()
        self.experiment_repository = ExperimentRepository()
        self.parser = Parser()

        experiments_extensions = ExperimentsExtensions(self.parser, self.target_group_repository, self.flag_repository, self.experiment_repository)
        properties_extensions = PropertiesExtensions(self.parser, self.custom_property_repository)
        experiments_extensions.extend()
        properties_extensions.extend()

        self.configuration_fetched_invoker = ConfigurationFetchedInvoker()
        self.registerer = Registerer(self.flag_repository)

        self.sdk_settings = None
        self.internal_flags = None
        self.impression_invoker = None
        self.flag_setter = None
        self.error_reporter = None
        self.configuration_fetcher = None
        self.state_sender = None
        self.last_configurations = None
        self.push_updates_listener = None
        self.cancel_event = Event()
        self.analytics_client = None
        self.last_fetch_time = None

    def setup(self, sdk_settings, device_properties, rox_options):
        self.sdk_settings = sdk_settings
        roxy_path = rox_options.roxy_url if rox_options is not None and rox_options.roxy_url is not None else None

        if roxy_path is None:
            if sdk_settings.api_key is None or sdk_settings.api_key == '':
                raise ValueError('Invalid rollout apikey - must be specified')

            valid_api_key_pattern = '^[a-fA-F\\d]{24}$'
            is_api_key_valid = re.search(valid_api_key_pattern, sdk_settings.api_key)

            if is_api_key_valid is None:
                raise ValueError('Illegal rollout apikey')

        self.internal_flags = InternalFlags(self.experiment_repository, self.parser)
        self.analytics_client = ClientProxy(device_properties, device_properties.rollout_key)
        self.impression_invoker = ImpressionInvoker(self.internal_flags, self.custom_property_repository, device_properties, self.analytics_client, roxy_path is not None)
        self.flag_setter = FlagSetter(self.flag_repository, self.parser, self.experiment_repository, self.impression_invoker)
        buid = BUID(sdk_settings, device_properties)

        #TODO: wrap with CacheControl
        client_request = Request()
        client_request_for_state = Request()
        err_reporter_request = Request()

        self.error_reporter = ErrorReporter(err_reporter_request, device_properties, buid)

        if roxy_path is not None:
            self.configuration_fetcher = ConfigurationFetcherRoxy(device_properties, client_request, self.configuration_fetched_invoker, self.error_reporter, roxy_path)
        else:
            self.configuration_fetcher = ConfigurationFetcher(device_properties, client_request, self.configuration_fetched_invoker, self.error_reporter, buid)
            self.state_sender = StateSender(device_properties, client_request_for_state, self.flag_repository, self.custom_property_repository, self.error_reporter)

        self.configuration_fetched_invoker.register_configuration_fetched_handler(
            self.wrap_configuration_fetched_handler(rox_options.configuration_fetched_handler if rox_options else None))

        def fetch():
            self.fetch()

            if rox_options is not None and rox_options.impression_handler is not None:
                self.impression_invoker.register_impression_handler(rox_options.impression_handler)

            cancel_periodic_task_event = None
            if rox_options is not None and rox_options.fetch_interval is not None:
                cancel_periodic_task_event = periodic_task.run(self.fetch, rox_options.fetch_interval)

            return AggregateEvent([cancel_periodic_task_event, self.cancel_event])

        executor = ThreadPoolExecutor(3)
        executor.submit(self.stop_background_activity_on_cancel)

        if self.state_sender is not None:
            executor.submit(self.state_sender.send)
        
        return executor.submit(fetch)

    def fetch(self, is_source_pushing = False):
        if self.configuration_fetcher is None:
            return

        fetch_throttle_interval = self.internal_flags.get_number_value("rox.internal.throttleFetchInSeconds")
        if (fetch_throttle_interval is not None and fetch_throttle_interval > 0 and
            (not is_source_pushing or self.internal_flags.is_enabled('rox.internal.considerThrottleInPush'))):
            current_time = datetime.now()
            if self.last_fetch_time is not None and current_time < self.last_fetch_time + timedelta(seconds = fetch_throttle_interval):
                Logging.get_logger().warn('Skipping fetch - kill switch')
                return

            self.last_fetch_time = current_time

        result = self.configuration_fetcher.fetch()
        if result is None or result.json_data is None:
            return

        configuration_parser = ConfigurationParser(SignatureVerifier(), self.error_reporter, self.configuration_fetched_invoker)

        configuration = configuration_parser.parse(result, self.sdk_settings)
        if configuration is None:
            return

        self.experiment_repository.set_experiments(configuration.experiments)
        self.target_group_repository.set_target_groups(configuration.target_groups)
        self.flag_setter.set_experiments()

        has_changes = self.last_configurations is None or self.last_configurations.json_data != result.json_data
        self.last_configurations = result
        self.configuration_fetched_invoker.invoke(FetcherStatus.APPLIED_FROM_NETWORK, configuration.signature_date, has_changes)

    def register(self, ns, rox_container):
        self.registerer.register_instance(rox_container, ns)

    def set_context(self, context):
        for flag in self.flag_repository.get_all_flags().values():
            flag.set_context(context)

    def add_custom_property(self, property):
        self.custom_property_repository.add_custom_property(property)

    def add_custom_property_if_not_exists(self, property):
        self.custom_property_repository.add_custom_property_if_not_exists(property)

    def wrap_configuration_fetched_handler(self, handler):
        def configuration_fetched_handler(args):
            if args.fetcher_status != FetcherStatus.ERROR_FETCHED_FAILED:
                self.start_or_stop_push_updated_listener()

            if handler is not None:
                try:
                    handler(args)
                except Exception as ex:
                    Logging.get_logger().error('Configuration fetcher handler exception', ex)

        return configuration_fetched_handler

    def start_or_stop_push_updated_listener(self):
        if self.internal_flags.is_enabled('rox.internal.pushUpdates'):
            if not self.push_updates_listener and not self.cancel_event.is_set():
                self.push_updates_listener = NotificationListener(Environment.NOTIFICATIONS_PATH, self.sdk_settings.api_key)
                self.push_updates_listener.on('changed', lambda event: self.fetch(True))
                self.push_updates_listener.start()
        else:
            if self.push_updates_listener:
                self.push_updates_listener.stop()
                self.push_updates_listener = None

    def stop_background_activity_on_cancel(self):
        self.cancel_event.wait()

        if self.push_updates_listener:
            self.push_updates_listener.stop()
            self.push_updates_listener = None

        self.analytics_client.shutdown()

    def dynamic_api(self, entities_provider):
        return DynamicApi(self.flag_repository, entities_provider)
