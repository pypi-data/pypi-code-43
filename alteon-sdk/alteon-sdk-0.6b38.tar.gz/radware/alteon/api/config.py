#!/usr/bin/env python
# Copyright (c) 2019 Radware LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# @author: Leon Meguira, Radware


import logging
from radware.sdk.api import BaseAPI
from radware.sdk.configurator import DeviceConfigurationManager, DeviceConfigurator
from radware.sdk.exceptions import ArgumentNotExpectedTypeError
from radware.alteon.sdk.configurators.appshape import AppshapeConfigurator
from radware.alteon.sdk.configurators.gslb_network import GSLBNetworkConfigurator
from radware.alteon.sdk.configurators.gslb_rule import GSLBRuleConfigurator
from radware.alteon.sdk.configurators.health_check_http import HealthCheckHTTPConfigurator
from radware.alteon.sdk.configurators.health_check_logexp import HealthCheckLogExpConfigurator
from radware.alteon.sdk.configurators.health_check_tcp import HealthCheckTCPConfigurator
from radware.alteon.sdk.configurators.server import ServerConfigurator
from radware.alteon.sdk.configurators.server_group import ServerGroupConfigurator
from radware.alteon.sdk.configurators.ssl_cert import SSLCertConfigurator
from radware.alteon.sdk.configurators.ssl_client_auth_policy import SSLClientAuthPolicyConfigurator
from radware.alteon.sdk.configurators.ssl_key import SSLKeyConfigurator
from radware.alteon.sdk.configurators.ssl_policy import SSLPolicyConfigurator
from radware.alteon.sdk.configurators.ssl_server_auth_policy import SSLServerAuthPolicyConfigurator
from radware.alteon.sdk.configurators.vadc_instance import VADCInstanceConfigurator
from radware.alteon.sdk.configurators.virtual_server import VirtualServerConfigurator
from radware.alteon.sdk.configurators.virtual_service import VirtualServiceConfigurator
from radware.alteon.sdk.configurators.l2_vlan import VLANConfigurator
from radware.alteon.sdk.configurators.system_local_user import LocalUserConfigurator
from radware.alteon.sdk.configurators.system_management_access import ManagementAccessConfigurator
from radware.alteon.sdk.configurators.system_predefined_local_users import PredefinedLocalUsersConfigurator
from radware.alteon.sdk.configurators.system_radius_authentication import SystemRadiusAuthenticationConfigurator
from radware.alteon.sdk.configurators.system_tacacs_authentication import SystemTacacsAuthenticationConfigurator
from radware.alteon.sdk.configurators.system_snmp import SystemSNMPConfigurator
from radware.alteon.sdk.configurators.system_logging import SystemLoggingConfigurator
from radware.alteon.sdk.configurators.system_vx_peer_syncronization import VXPeerSyncConfigurator
from radware.alteon.sdk.configurators.system_alerts import SystemAlertsConfigurator
from radware.alteon.sdk.configurators.system_dns_client import SystemDNSClientConfigurator
from radware.alteon.sdk.configurators.system_time_date import SystemTimeDateConfigurator
from radware.alteon.sdk.configurators.physical_port import PhysicalPortConfigurator
from radware.alteon.sdk.configurators.lacp_aggregation import LACPAggregationConfigurator
from radware.alteon.sdk.configurators.spanning_tree import SpanningTreeConfigurator
from radware.alteon.sdk.configurators.l2_lldp import LLDPConfigurator
from radware.alteon.sdk.configurators.l3_interface import L3InterfaceConfigurator
from radware.alteon.sdk.configurators.l3_gateway import GatewayConfigurator
from radware.alteon.sdk.configurators.l3_bootp_relay import BOOTPRelayConfigurator
from radware.alteon.sdk.configurators.l3_static_routes import StaticRoutesConfigurator
from radware.alteon.sdk.configurators.ha_floating_ip import FloatingIPConfigurator
from radware.alteon.sdk.configurators.ha_configuration_sync import ConfigurationSyncConfigurator
from radware.alteon.sdk.configurators.high_availability import HighAvailabilityConfigurator
from radware.alteon.sdk.configurators.global_traffic_redirection import GlobalRedirectionConfigurator
from radware.alteon.sdk.configurators.fqdn_server import FQDNServerConfigurator
from radware.alteon.sdk.configurators.network_class_ip import NetworkClassIPConfigurator
from radware.alteon.sdk.configurators.network_class_region import NetworkClassRegionConfigurator
from radware.alteon.sdk.configurators.dns_responders import DNSRespondersConfigurator

log = logging.getLogger(__name__)


class AlteonConfigurators(object):
    def __init__(self, connection):
        self.appshape = AppshapeConfigurator(connection)
        self.gslb_network = GSLBNetworkConfigurator(connection)
        self.gslb_rule = GSLBRuleConfigurator(connection)
        self.hc_http = HealthCheckHTTPConfigurator(connection)
        self.hc_logexp = HealthCheckLogExpConfigurator(connection)
        self.hc_tcp = HealthCheckTCPConfigurator(connection)
        self.server = ServerConfigurator(connection)
        self.server_group = ServerGroupConfigurator(connection)
        self.ssl_cert = SSLCertConfigurator(connection)
        self.ssl_client_auth_policy = SSLClientAuthPolicyConfigurator(connection)
        self.ssl_key = SSLKeyConfigurator(connection)
        self.ssl_policy = SSLPolicyConfigurator(connection)
        self.ssl_server_auth_policy = SSLServerAuthPolicyConfigurator(connection)
        self.vadc_instance = VADCInstanceConfigurator(connection)
        self.virtual_server = VirtualServerConfigurator(connection)
        self.virtual_service = VirtualServiceConfigurator(connection)
        self.l2_vlan = VLANConfigurator(connection)
        self.sys_local_user = LocalUserConfigurator(connection)
        self.sys_management_access = ManagementAccessConfigurator(connection)
        self.sys_predefined_local_users = PredefinedLocalUsersConfigurator(connection)
        self.sys_radius_auth = SystemRadiusAuthenticationConfigurator(connection)
        self.sys_tacacs_auth = SystemTacacsAuthenticationConfigurator(connection)
        self.sys_snmp = SystemSNMPConfigurator(connection)
        self.sys_logging = SystemLoggingConfigurator(connection)
        self.sys_vx_peer_sync = VXPeerSyncConfigurator(connection)
        self.sys_alerts = SystemAlertsConfigurator(connection)
        self.sys_dns_client = SystemDNSClientConfigurator(connection)
        self.sys_time_date = SystemTimeDateConfigurator(connection)
        self.physical_port = PhysicalPortConfigurator(connection)
        self.lacp_aggregation = LACPAggregationConfigurator(connection)
        self.spanning_tree = SpanningTreeConfigurator(connection)
        self.l2_lldp = LLDPConfigurator(connection)
        self.l3_interface = L3InterfaceConfigurator(connection)
        self.l3_gateway = GatewayConfigurator(connection)
        self.l3_bootp_relay = BOOTPRelayConfigurator(connection)
        self.l3_static_routes = StaticRoutesConfigurator(connection)
        self.ha_floating_ip = FloatingIPConfigurator(connection)
        self.ha_config_sync = ConfigurationSyncConfigurator(connection)
        self.high_availability = HighAvailabilityConfigurator(connection)
        self.global_redirection = GlobalRedirectionConfigurator(connection)
        self.fdn_server = FQDNServerConfigurator(connection)
        self.network_class_ip = NetworkClassIPConfigurator(connection)
        self.network_class_region = NetworkClassRegionConfigurator(connection)
        self.dns_responders = DNSRespondersConfigurator(connection)


class AlteonConfiguration(BaseAPI):
    def __init__(self, connection):
        self._connection = connection
        self._configurators = AlteonConfigurators(connection)
        self._config_manager = DeviceConfigurationManager()
        log.info(' Alteon Configuration Module initialized, server: {0}'.format(self._connection.id))

    def execute(self, command, parameters, **kw):
        configurator = self._find_configurator(parameters)
        return self._config_manager.execute(configurator, command, parameters, **kw)

    def _find_configurator(self, parameters):
        for k, v in self._configurators.__dict__.items():
            if isinstance(v, DeviceConfigurator):
                if v.get_parameters_class() == type(parameters):
                    return v
        raise ArgumentNotExpectedTypeError(parameters, 'no Configurator found for argument type')

    @property
    def manager(self):
        return self._config_manager

    @property
    def type(self):
        return self._configurators
