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


from radware.sdk.common import RadwareParametersStruct
from radware.alteon.sdk.alteon_configurator import MSG_UPDATE, AlteonConfigurator, NumericConfigurator
from radware.alteon.beans.GslbNewCfgRuleTable import *
from radware.alteon.beans.GslbNewCfgMetricTable import *
from typing import List, Optional, ClassVar


class GSLBRuleMetricEntry(RadwareParametersStruct):
    metric: EnumGslbMetricMetric
    network_ids: Optional[List[int]]

    def __init__(self, metric: EnumGslbMetricMetric = None):
        self.metric = metric
        self.network_ids = list()


class GSLBRuleMetrics(RadwareParametersStruct):
    first: Optional[GSLBRuleMetricEntry]
    second: Optional[GSLBRuleMetricEntry]
    third: Optional[GSLBRuleMetricEntry]
    fourth: Optional[GSLBRuleMetricEntry]
    fifth: Optional[GSLBRuleMetricEntry]

    def __init__(self):
        self.first = GSLBRuleMetricEntry()
        self.second = GSLBRuleMetricEntry()
        self.third = GSLBRuleMetricEntry()
        self.fourth = GSLBRuleMetricEntry()
        self.fifth = GSLBRuleMetricEntry()


class GSLBRuleParameters(RadwareParametersStruct):
    index: int
    state: Optional[EnumGslbRuleState]
    dns_ttl: Optional[int]
    max_dns_resource_records: Optional[int]
    domain_name: Optional[str]
    src_dns_persist_mask: Optional[str]
    dns_persist_timeout: Optional[int]
    src6_dns_persist_prefix: Optional[int]
    rule_type: Optional[EnumGslbRuleType]
    description: Optional[str]
    edns_persist_mode: Optional[EnumGslbRuleEdnsPrst]
    rule_network_fallback: Optional[EnumGslbRuleNetworkFallback]
    rule_metrics: Optional[GSLBRuleMetrics]

    def __init__(self, index: int = None):
        self.index = index
        self.state = None
        self.dns_ttl = None
        self.max_dns_resource_records = None
        self.domain_name = None
        self.src_dns_persist_mask = None
        self.dns_persist_timeout = None
        self.src6_dns_persist_prefix = None
        self.rule_type = None
        self.description = None
        self.edns_persist_mode = None
        self.rule_network_fallback = None
        self.rule_metrics = GSLBRuleMetrics()


bean_map = {
    GslbNewCfgRuleTable: dict(
        struct=GSLBRuleParameters,
        direct=True,
        attrs=dict(
            Indx='index',
            State='state',
            TTL='dns_ttl',
            RR='max_dns_resource_records',
            Dname='domain_name',
            IpNetMask='src_dns_persist_mask',
            Timeout='dns_persist_timeout',
            Ipv6Prefix='src6_dns_persist_prefix',
            Type='rule_type',
            Name='description',
            EdnsPrst='edns_persist_mode',
            NetworkFallback='rule_network_fallback'
        )
    ),
    GslbNewCfgMetricTable: dict(
        struct=List[GSLBRuleMetricEntry],
        direct=False,
        attrs=dict(
            RuleMetricIndx='index',
        )
    )
}

priority_to_num = dict(
    first=1,
    second=2,
    third=3,
    fourth=4,
    fifth=5
)


class GSLBRuleConfigurator(AlteonConfigurator, NumericConfigurator):
    parameters_class: ClassVar[GSLBRuleParameters]

    def __init__(self, alteon_connection):
        AlteonConfigurator.__init__(self, bean_map, alteon_connection)

    def _read(self, parameters: GSLBRuleParameters) -> GSLBRuleParameters:
        self._read_device_beans(parameters)
        if self._beans:
            parameters.rule_metrics = GSLBRuleMetrics()

            for entry in self._beans[GslbNewCfgMetricTable]:
                new_metric = GSLBRuleMetricEntry()
                new_metric.metric = entry.Metric
                new_metric.network_ids = BeanUtils.decode_bmp(entry.NetworkBmap)
                if entry.Metric != EnumGslbMetricMetric.none:
                    for k, v in priority_to_num.items():
                        if entry.Indx == v:
                            setattr(parameters.rule_metrics, k, new_metric)
                            break
            return parameters

    def _update(self, parameters: GSLBRuleParameters, dry_run: bool) -> str:
        self._write_device_beans(parameters, dry_run=dry_run)
        for key, val in parameters.rule_metrics.__dict__.items():
            if val and val.metric:
                entry = self._get_bean_instance(GslbNewCfgMetricTable, parameters)
                entry.Indx = int(priority_to_num.get(key))
                entry.Metric = val.metric
                self._device_api.update(entry, dry_run=dry_run)
                entry.Metric = None
                if val.network_ids:
                    for net_id in val.network_ids:
                        entry.AddNetwork = net_id
                        self._device_api.update(entry, dry_run=dry_run)
        return self._get_object_id(parameters) + MSG_UPDATE

    def _update_remove(self, parameters: GSLBRuleParameters, dry_run: bool) -> str:
        if parameters.rule_metrics:
            for k, v in parameters.rule_metrics.__dict__.items():
                if v.metric is not None and v.metric != EnumGslbMetricMetric.none:
                    instance = GslbNewCfgMetricTable()
                    instance.RuleMetricIndx = parameters.index
                    instance.Indx = priority_to_num.get(k)
                    instance.Metric = EnumGslbMetricMetric.none
                    self._device_api.update(instance, dry_run=dry_run)
                if v.network_ids:
                    for net in v.network_ids:
                        instance = GslbNewCfgMetricTable()
                        instance.RuleMetricIndx = parameters.index
                        instance.Indx = priority_to_num.get(k)
                        instance.RemNetwork = net
                        self._device_api.update(instance, dry_run=dry_run)
        return self._get_object_id(parameters) + MSG_UPDATE

    def _entry_bean_instance(self, parameters):
        return self._get_bean_instance(GslbNewCfgRuleTable, parameters)

