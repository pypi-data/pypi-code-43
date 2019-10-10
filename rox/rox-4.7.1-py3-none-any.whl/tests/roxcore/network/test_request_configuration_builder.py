import unittest

from rox.core.consts.environment import Environment
from rox.core.network.request_configuration_builder import RequestConfigurationBuilder

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class RequestConfigurationBuilderTests(unittest.TestCase):
    def test_cdn_request_data_will_have_distinct_id(self):
        device_props = Mock()
        device_props.distinct_id = '123'
        device_props.get_all_properties.return_value = {
            'app_key': '123',
            'api_version': '4.0.0',
            'cache_miss_url': 'harta',
            'distinct_id': '123'
        }
        sdk_settings = Mock()
        sdk_settings.dev_mode_secret = '1'
        buid = Mock()
        buid.get_value.return_value = '123'

        request_configuration_builder = RequestConfigurationBuilder(sdk_settings, buid, device_props, None)
        result = request_configuration_builder.build_for_cdn()
        self.assertEqual('%s/123' % Environment.CDN_PATH, result.url)
        self.assertEqual('123', result.query_params['distinct_id'])

    def test_roxy_request_data_will_have_server_data(self):
        device_props = Mock()
        device_props.distinct_id = '123'
        device_props.get_all_properties.return_value = {
            'app_key': '123',
            'api_version': '4.0.0',
            'distinct_id': '123'
        }
        sdk_settings = Mock()
        sdk_settings.dev_mode_secret = '1'
        buid = Mock()
        buid.get_value.return_value = '123'
        buid.get_query_string_parts.return_value = {'buid': '123'}

        request_configuration_builder = RequestConfigurationBuilder(sdk_settings, buid, device_props, 'http://bimba.bobi.o.ponpon')
        result = request_configuration_builder.build_for_roxy()

        self.assertEqual('http://bimba.bobi.o.ponpon/device/request_configuration', result.url)
        self.assertEqual('123', result.query_params['app_key'])
        self.assertEqual('4.0.0', result.query_params['api_version'])
        self.assertEqual('123', result.query_params['distinct_id'])
        self.assertEqual('123', result.query_params['buid'])
        self.assertEqual('%s/123' % Environment.CDN_PATH, result.query_params['cache_miss_url'])
        self.assertEqual('1', result.query_params['devModeSecret'])
        self.assertEqual(6, len(result.query_params))

    def test_api_request_data_will_have_server_data(self):
        device_props = Mock()
        device_props.distinct_id = '123'
        device_props.get_all_properties.return_value = {
            'app_key': '123',
            'api_version': '4.0.0',
            'distinct_id': '123'
        }
        sdk_settings = Mock()
        sdk_settings.dev_mode_secret = '1'
        buid = Mock()
        buid.get_value.return_value = '123'
        buid.get_query_string_parts.return_value = {'buid': '123'}

        request_configuration_builder = RequestConfigurationBuilder(sdk_settings, buid, device_props, None)
        result = request_configuration_builder.build_for_api()

        self.assertEqual(Environment.API_PATH, result.url)
        self.assertEqual('123', result.query_params['app_key'])
        self.assertEqual('4.0.0', result.query_params['api_version'])
        self.assertEqual('123', result.query_params['distinct_id'])
        self.assertEqual('123', result.query_params['buid'])
        self.assertEqual('%s/123' % Environment.CDN_PATH, result.query_params['cache_miss_url'])
        self.assertEqual('1', result.query_params['devModeSecret'])
        self.assertEqual(6, len(result.query_params))
