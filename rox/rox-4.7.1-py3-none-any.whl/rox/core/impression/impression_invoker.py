import os
from collections import namedtuple

from rox.core.consts import property_type
from rox.core.logging.logging import Logging
from rox.core.utils.time_utils import now_in_unix_milliseconds
from rox.core.utils.type_utils import is_string
from rox.core.impression.models.experiment import Experiment

ImpressionArgs = namedtuple('ImpressionArgs', ['reporting_value', 'experiment', 'context'])


class ImpressionInvoker:
    def __init__(self, internal_flags, custom_property_repository, device_properties, analytics_client, is_roxy):
        self.internal_flags = internal_flags
        self.custom_property_repository = custom_property_repository
        self.device_properties = device_properties
        self.analytics_client = analytics_client
        self.is_roxy = is_roxy

        self.impression_handlers = []

    def invoke(self, reporting_value, experiment, context):
        try:
            internal_experiment = self.internal_flags.is_enabled('rox.internal.analytics')
            if internal_experiment and experiment is not None and not self.is_roxy:
                prop = self.custom_property_repository.get_custom_property(experiment.stickinessProperty) or self.custom_property_repository.get_custom_property('rox.' + property_type.DISTINCT_ID.name)
                distinct_id = '(null_distinct_id'
                if prop is not None:
                    prop_value = prop.value(context)
                    if is_string(prop_value):
                        distinct_id = prop_value

                event_time = now_in_unix_milliseconds()
                try:
                    event_time = int(os.getenv('rox.analytics.ms'))
                except ValueError:
                    pass
                except TypeError:
                    pass

                self.analytics_client.track({
                    'flag': reporting_value.name,
                    'value': reporting_value.value,
                    'distinctId': distinct_id,
                    'experimentId': experiment.id,
                    'experimentVersion': '0',
                    'type': 'IMPRESSION',
                    'time': event_time,
                })
        except Exception as ex:
            Logging.get_logger().error('Failed to send analytics', ex)

        self.raise_impression_event(ImpressionArgs(reporting_value, None if not experiment else Experiment(experiment), context))

    def register_impression_handler(self, handler):
        self.impression_handlers.append(handler)

    def raise_impression_event(self, args):
        for handler in self.impression_handlers:
            try:
                handler(args)
            except Exception as ex:
                Logging.get_logger().error('Impresssion handler exception', ex)
