from requests.compat import urljoin

from rox.core.consts.environment import Environment
from rox.core.consts.property_type import CACHE_MISS_URL, DISTINCT_ID
from rox.core.network.request import RequestData


class RequestConfigurationBuilder:
    def __init__(self, sdk_settings, buid, device_properties, roxy_url):
        self.sdk_settings = sdk_settings
        self.buid = buid
        self.device_properties = device_properties
        self.roxy_url = roxy_url

    def build_for_roxy(self):
        roxy_endpoint = urljoin(self.roxy_url, Environment.ROXY_INTERNAL_PATH)
        return self.build_request_with_full_params(roxy_endpoint)

    def build_for_cdn(self):
        return RequestData('%s/%s' % (Environment.CDN_PATH, self.buid.get_value()), {DISTINCT_ID.name: self.device_properties.distinct_id})

    def build_for_api(self):
        return self.build_request_with_full_params(Environment.API_PATH)

    def build_request_with_full_params(self, url):
        query_params = {}

        for key, value in self.buid.get_query_string_parts().items():
            if key not in query_params:
                query_params[key] = value

        for key, value in self.device_properties.get_all_properties().items():
            if key not in query_params:
                query_params[key] = value

        cdn_data = self.build_for_cdn()
        query_params[CACHE_MISS_URL.name] = cdn_data.url
        query_params['devModeSecret'] = self.sdk_settings.dev_mode_secret

        return RequestData(url, query_params)
