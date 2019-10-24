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


from radware.alteon.beans.Global \
    import Root, EnumAgApplyConfig, EnumAgSaveConfig, EnumAgRevert, EnumAgRevertApply, EnumAgReset, EnumAgDiffState, \
    EnumAgSyncStatus, EnumSlbOperConfigSync, EnumHaOperSwitchBackup
from radware.alteon.api import AlteonDeviceConnection
from radware.alteon.beans.AgApplyTable import *
from radware.alteon.beans.AgSaveTable import *
from radware.alteon.beans.AgDiffTable import *
from radware.alteon.beans.VADCNewCfgSysTable import *
from radware.sdk.management import DeviceInfo, DeviceOper, DeviceConfig, MSG_REBOOT_STATEFUL, MSG_REBOOT, \
    MSG_NOT_ACCESSIBLE, MSG_IMG_UPLOAD, MSG_CONFIG_DOWNLOAD, MSG_CONFIG_UPLOAD
from radware.alteon.api import AlteonDevice
from radware.alteon.exceptions import AlteonRequestError
from radware.sdk.exceptions import DeviceFunctionError
from radware.sdk.api import BaseAPI
from radware.sdk.device import DeviceType
from radware.sdk.common import generate_password, get_file_size, PasswordArgument
from abc import ABCMeta
from typing import Optional
import time
import logging


MSG_REVERT = 'unapplied changes reverted'
MSG_REVERT_APPLY = 'unsaved changes reverted'
MSG_DEVICE_TIMEOUT = 'device timeout'
DIFF_CHANGE = 'identical to new config'

log = logging.getLogger(__name__)


sys_info_map = dict(
    agSoftwareVersion='software_version',
    hwMACAddress='mac_address',
    agSwitchLastBootTime='last_boot_time',
    agSwitchLastApplyTime='last_apply_time',
    agSwitchLastSaveTime='last_save_time',
    agMgmtNewCfgIpAddr='management_ipv4_address',
    agMgmtNewCfgIpv6Addr='management_ipv6_address',
    agSwitchUpTime='switch_uptime',
    agFormFactor='form_factor',
    agPlatformIdentifier='platfrom_id',
    agRtcTime='system_time',
    mpMemStatsFree='free_memory_mb',
    agRtcDate='system_date',
    mpMemStatsTotal='total_memory_mb',
    agFipsSecurityLevel='fips_security_level',
    hwSerialNumber='serial_number',
    hwMainBoardNumber='mainboard_hw_number',
    hwMainBoardRevision='mainboard_hw_revision',
    hwEthernetBoardNumber='eth_board_hw_number',
    hwEthernetBoardRevision='eth_board_hw_revision',
    hardDiskMax='hard_disk_size_gb',
    hardDiskCur='hard_disk_used_gb',
    agSysCurUsedDiskspace='hard_disk_in_use_gb',
    ramSize='total_ram_size_gb',
    hwSslChipInfo='ssl_chip',
    connmngStatsFIPSCard='fips_card_status',
    hwTemperatureStatus='temperature_sensors',
    hwPowerSupplyStatus='power_supply',
    hwFanStatus='fan_status',
    cacheUsageMaxEnt='max_cache_mb',
    cacheUsageCurrEnt='used_cache_mb',
    switchCapVlanMaxEnt='max_vlans',
    switchCapVlanCurrEnt='cur_and_ena_vlans',
)

sys_capacity_vx_map = dict(
    vADCInfoAvailableCU='available_capacity_units:',
    vADCInfoMaxCU='max_capacity_units',
    vADCInfoAvailableThruput='current_vadc_throughput',
    vADCInfoMaxThruput='max_vadc_throughput',
    capacityUnitsCurr='used_capacity_units',
    vAdcMax='max_vadcs',
    vAdcCurr='current_vadcs',
    switchCapVlanMaxEnt='max_vlans',
    switchCapVlanCurrEnt='cur_and_ena_vlans'
)

sys_capacity_standalone_map = dict(
    switchCapVlanMaxEnt='max_vlans',
    switchCapVlanCurrEnt='cur_and_ena_vlans',
    switchCapFDBMaxEnt='max_fdb_entries',
    switchCapFDBCurrEnt='cur_fdb_entries',
    switchCapFDBPerSPMaxEnt='max_fdb_per_sp',
    switchCapStaticTrunkGrpsMaxEnt='max_static_trunks',
    switchCapStaticTrunkGrpsCurrEnt='cur_and_ena_static_trunks',
    switchCapLACPTrunkGRs='max_lacp_trunks',
    switchCapTrunksperTrunkGR='max_trunks_per_trunk_group',
    switchCapSTGsMaxEnt='max_stg_groups',
    switchCapSTGsCurrEnt='cur_and_ena_stg_groups',
    switchCapPortTeamsMaxEnt='max_port_teams',
    switchCapPortTeamsCurrEnt='cur_and_ena_port_teams',
    switchCapMonitorPorts='max_monitor_ports',
    switchCapIpIntfMaxEnt='max_ip_interfaces',
    switchCapIpIntfCurrEnt='cur_ip_interfaces',
    switchCapIpGWMaxEnt='max_ip_gateways',
    switchCapIpGWCurrEnt='cur_and_ena_ip_gateways',
    switchCapIpRoutesMaxEnt='max_ip_route_entries',
    switchCapIpRoutesCurrEnt='cur_ip_route_entries',
    switchCapIpStaticRoutesMaxEnt='max_static_ip_routes',
    switchCapIpStaticRoutesCurrEnt='cur_static_ip_routes',
    switchCapIpARPMaxEnt='max_arp_entries',
    switchCapIpARPCurrEnt='cur_arp_entries',
    switchCapIpStaticARPMaxEnt='max_static_arp_entries',
    switchCapIpStaticARPCurrEnt='cur_static_arp_entries',
    switchCapLocNetsMaxEnt='max_local_nets',
    switchCapLocNetsCurrEnt='cur_local_nets',
    switchCapDNSSerMaxEnt='max_dns_servers',
    switchCapDNSSerCurrEnt='cur_dns_servers',
    switchCapBootpSerMaxEnt='max_bootp_servers',
    switchCapBootpSerCurrEnt='cur_bootp_servers',
    switchCapOSPFIntfMaxEnt='max_ospf_interfaces',
    switchCapOSPFIntfCurrEnt='cur_and_ena_ospf_interfaces',
    switchCapOSPFAreasMaxEnt='max_ospf_areas',
    switchCapOSPFAreasCurrEnt='cur_and_ena_ospf_areas',
    switchCapOSPFSummaryRangesMaxEnt='max_ospf_summary_ranges',
    switchCapOSPFSummaryRangesCurrEnt='cur_and_ena_ospf_summary_ranges',
    switchCapOSPFVirtLinksMaxEnt='max_ospf_virtual_links',
    switchCapOSPFVirtLinksCurrEnt='cur_and_ena_ospf_virtual_links',
    switchCapOSPFHostsMaxEnt='max_ospf_hosts',
    switchCapOSPFHostsCurrEnt='cur_and_ena_ospf_hosts',
    switchCapLSDBLimit='max_ospf_lsdb_limit',
    switchCapBGPPeersMaxEnt='max_bgp_peers',
    switchCapBGPPeersCurrEnt='cur_and_ena_bgp_peers',
    switchCapBGPRouteAggrsMaxEnt='max_bgp_route_aggrs',
    switchCapBGPRouteAggrsCurrEnt='cur_and_ena_bgp_route_aggrs',
    switchCapRouteMapsMaxEnt='max_route_maps',
    switchCapRouteMapsCurrEnt='cur_and_ena_route_maps',
    switchCapNwkFltsMaxEnt='max_network_filters',
    switchCapNwkFltsCurrEnt='cur_and_ena_network_filters',
    switchCapASFlts='max_as_filters',
    switchCapOSPFv3IntfMaxEnt='max_ospfv3_interfaces',
    switchCapOSPFv3IntfCurrEnt='cur_and_ena_ospfv3_interfaces',
    switchCapOSPFv3AreasMaxEnt='max_ospfv3_areas',
    switchCapOSPFv3AreasCurrEnt='cur_and_ena_ospfv3_areas',
    switchCapOSPFv3SummaryRangesMaxEnt='max_ospfv3_summary_ranges',
    switchCapOSPFv3SummaryRangesCurrEnt='cur_and_ena_ospfv3_summary_ranges',
    switchCapOSPFv3VirtLinksMaxEnt='max_ospfv3_virtual_links',
    switchCapOSPFv3VirtLinksCurrEnt='cur_and_ena_ospfv3_virtual_links',
    switchCapOSPFv3HostsMaxEnt='max_ospfv3_hosts',
    switchCapOSPFv3HostsCurrEnt='cur_and_ena_ospfv3_hosts',
    switchCapASFltsCurr='cur_as_filters',
    switchCapRealSersMaxEnt='max_real_servers',
    switchCapRealSersCurrEnt='cur_and_ena_real_servers',
    switchCapSerGRsMaxEnt='max_server_groups',
    switchCapSerGRsCurrEnt='cur_and_ena_server_groups',
    switchCapVirtSersMaxEnt='max_virtual_servers',
    switchCapVirtSersCurrEnt='cur_and_ena_virtual_servers',
    switchCapVirtServicesEnt='max_virtual_services',
    switchCapRealServicesEnt='max_real_services',
    switchCapRealIDSSer='max_real_ids_servers',
    switchCapIDSSerGRs='max_ids_groups',
    switchCapGSLBDomainsMaxEnt='max_gslb_domains',
    switchCapGSLBDomainsCurrEnt='cur_and_ena_gslb_domains',
    switchCapGSLBServicesMaxEnt='max_gslb_services',
    switchCapGSLBServicesCurrEnt='cur_and_ena_gslb_services',
    switchCapGSLBLocSersMaxEnt='max_gslb_local_servers',
    switchCapGSLBLocSersCurrEnt='cur_and_ena_gslb_local_servers',
    switchCapGSLBRemSersMaxEnt='max_gslb_remote_servers',
    switchCapGSLBRemSersCurrEnt='cur_and_ena_gslb_remote_servers',
    switchCapGSLBRemSitesMaxEnt='max_gslb_sites',
    switchCapGSLBRemSitesCurrEnt='cur_and_ena_gslb_sites',
    switchCapGSLBFailoversPerRemSiteMaxEnt='max_gslb_failovers_per_site',
    switchCapGSLBFailoversPerRemSiteCurrEnt='cur_and_ena_gslb_failovers_per_site',
    switchCapGSLBNetworksMaxEnt='max_gslb_networks',
    switchCapGSLBNetworksCurrEnt='cur_and_ena_gslb_networks',
    switchCapGSLBGeographicalRegionsMaxEnt='max_gslb_regions',
    switchCapGSLBGeographicalRegionsCurrEnt='cur_and_ena_gslb_regions',
    switchCapGSLBRulesMaxEnt='max_gslb_rules',
    switchCapGSLBRulesCurrEnt='cur_and_ena_gslb_rules',
    switchCapGSLBMetricsPerRuleMaxEnt='max_gslb_metrics_per_rule',
    switchCapGSLBMetricPerRuleCurrEnt='cur_and_ena_gslb_metrics_per_rule',
    switchCapGSLBDNSPersCacheMaxEnt='max_gslb_dns_persist_cache_entries',
    switchCapGSLBDNSPersCacheCurrEnt='cur_gslb_dns_persist_cache_entries',
    switchCapFltsMaxEnt='max_filters',
    switchCapFltsCurrEnt='cur_and_ena_filters',
    switchCapSLBSessionsMaxEnt='max_session_table_entries',
    switchCapSLBSessionsCurrEnt='cur_session_table_entries',
    switchCapNumofRportstoVport='max_rport_to_vport',
    switchCapNetworkClassesMaxEnt='max_network_classes',
    switchCapNetworkClassesCurrEnt='cur_network_classes',
    switchCapNetworkElementsMaxEnt='max_network_elements',
    switchCapNetworkElementsCurrEnt='cur_network_elements',
    switchCapAppShapeMaxEnt='max_appshape_scripts',
    switchCapAppShapeCurrEnt='cur_and_ena_appshape_scripts',
    switchCapDataClassClassesMaxEnt='max_data_classes',
    switchCapDataClassClassesCurEnt='cur_data_classes',
    switchCapDataClassManualEntriesPerClassMaxEnt='max_manual_entries_per_data_class',
    switchCapDataClassManualEntriesMaxEnt='max_data_class_manual_entries',
    switchCapDataClassManualEntriesCurEnt='cur_data_class_manual_entries',
    switchCapDataClassMemMaxSize='max_data_class_mem_size_bytes',
    switchCapDataClassMemCurSize='cur_data_class_mem_size_bytes',
    switchCapDynamicDataStoreMaxSize='max_dynamic_dd_entries',
    switchCapDynamicDataStoreCurSize='cur_dynamic_dd_entries',
    switchCapCachePolMaxEnt='max_cache_policies',
    switchCapCachePolCurrEnt='cur_and_ena_cache_policies',
    switchCapCacheRuleMaxEnt='max_caching_rules',
    switchCapCacheRuleCurrEnt='cur_and_ena_caching_rules',
    switchCapCacheRuleListMaxEnt='max_caching_rule_lists',
    switchCapCacheRuleListCurrEnt='cur_and_ena_caching_rule_lists',
    switchCapKeysMaxEnt='max_ssl_keys',
    switchCapKeysCurrEnt='cur_ssl_keys',
    switchCapCertSignReqMaxEnt='max_ssl_csrs',
    switchCapCertSignReqCurrEnt='cur_ssl_csrs',
    switchCapServerCertMaxEnt='max_ssl_certs',
    switchCapServerCertCurrEnt='cur_ssl_certs',
    switchCapTrusCACertMaxEnt='max_ssl_trust_ca_certs',
    switchCapTrusCACertCurrEnt='cur_ssl_trust_ca_certs',
    switchCapInterCACertMaxEnt='max_ssl_interm_ca_certs',
    switchCapInterCACertCurrEnt='cur_ssl_interm_ca_certs',
    switchCapCertGroupMaxEnt='max_ssl_cert_groups',
    switchCapCertGroupCurrEnt='cur_ssl_cert_groups',
    switchCapSecurityPolicyMaxEnt='max_security_policies',
    switchCapSecurityPolicyCurrEnt='cur_and_ena_security_policies',
    switchCapSmartNatMaxEnt='max_smart_nat_entries',
    switchCapSmartNatCurrEnt='cur_smart_nat_entries',
)


class AlteonMngBase(BaseAPI, AlteonDevice):
    __metaclass__ = ABCMeta

    def __init__(self, adc_connection):
        AlteonDevice.__init__(self, adc_connection)
        log.info(' {0} initialized, server: {1}'.format(self.__class__.__name__, adc_connection.id))


class AlteonMngInfo(AlteonMngBase, DeviceInfo):

    def __init__(self, adc_connection):
        AlteonMngBase.__init__(self, adc_connection)

    @property
    def device_name(self):
        return json.loads(self._rest.read_data_object('sysName'))['sysName']

    @property
    def software(self):
        return self._read_sys_info().agSoftwareVersion

    def is_accessible(self, timeout_second=5, retries=1):
        timeout_bck = self._rest.timeout
        self._rest._timeout = timeout_second
        try:
            self._read_sys_info(retries)
        except AlteonRequestError:
            log.debug(' {0} , server: {1} , {2}'.format(self.__class__.__name__, self.connection.id,
                                                        MSG_NOT_ACCESSIBLE))
            return False
        except Exception as e:
            raise e
        self._rest._timeout = timeout_bck
        return True

    @property
    def is_container(self):
        return self.form_factor.lower() == 'vx' or self.form_factor.lower() == 'standalone'

    @property
    def is_vx(self):
        return self.form_factor.lower() == 'vx'

    @property
    def is_standalone(self):
        return self.form_factor.lower() == 'standalone'

    @property
    def is_vadc(self):
        return self.form_factor.lower() == 'vadc'

    @property
    def is_master(self):
        if self.ha_state is not None:
            return self.ha_state.lower() == 'master'
        else:
            return False

    @property
    def is_backup(self):
        if self.ha_state is not None:
            return self.ha_state.lower() == 'backup'
        else:
            return False

    @property
    def ha_state(self):
        if not self.is_vx:
            root = Root()
            root.vrrpInfoHAState = READ_PROP
            return self._rest.read(root).vrrpInfoHAState
        return None

    @property
    def mac_address(self):
        return self._read_sys_info().hwMACAddress

    @property
    def form_factor(self):
        return self._read_sys_info().agFormFactor

    @property
    def platform_id(self):
        return self._read_sys_info().agPlatformIdentifier

    @property
    def hw_serial_number(self):
        return self._read_sys_info().hwSerialNumber

    @property
    def uptime(self):
        return self._read_sys_info().agSwitchUpTime

    @property
    def vadcs_address(self):
        if not self.is_vx:
            raise DeviceFunctionError(self.vadcs_address, DeviceType.Alteon, 'not a VX container')
        address = list()
        for vadc in self._rest.read_all(VADCNewCfgSysTable()):
            if vadc.MmgmtAddr is not None:
                address.append(vadc.MmgmtAddr)
            else:
                address.append(vadc.MmgmtIpv6Addr)
        return address

    def device_sys_info(self):
        result = dict()
        result.update(dict(
            device_name=self.device_name,
            ha_state=self.ha_state
        ))
        self._append_dict_result(self._read_sys_info(), result)
        if self.is_container:
            self._append_dict_result(self._read_sys_info_container(), result)
        return self._dict_keys_translation(result, sys_info_map)

    def device_sys_capacity(self):
        result = dict()
        if self.is_vx:
            self._append_dict_result(self._read_sys_capacity_vx(), result)
            return self._dict_keys_translation(result, sys_capacity_vx_map)
        else:
            self._append_dict_result(self._read_sys_capacity_standalone(), result)
            return self._dict_keys_translation(result, sys_capacity_standalone_map)

    def _read_sys_info(self, retries=3):
        root = Root()
        root.agSoftwareVersion = READ_PROP
        root.hwMACAddress = READ_PROP
        root.agSwitchLastBootTime = READ_PROP
        root.agSwitchLastApplyTime = READ_PROP
        root.agSwitchLastSaveTime = READ_PROP
        root.agMgmtNewCfgIpAddr = READ_PROP
        root.agMgmtNewCfgIpv6Addr = READ_PROP
        root.agSwitchUpTime = READ_PROP
        root.agFormFactor = READ_PROP
        root.agPlatformIdentifier = READ_PROP
        root.agRtcTime = READ_PROP
        root.mpMemStatsFree = READ_PROP
        root.agRtcDate = READ_PROP
        root.mpMemStatsTotal = READ_PROP
        root.agFipsSecurityLevel = READ_PROP
        root.hwSerialNumber = READ_PROP
        root.hwMainBoardNumber = READ_PROP
        root.hwMainBoardRevision = READ_PROP
        root.hwEthernetBoardNumber = READ_PROP
        root.hwEthernetBoardRevision = READ_PROP
        root.hardDiskMax = READ_PROP
        root.hardDiskCur = READ_PROP
        root.ramSize = READ_PROP
        root.hwSslChipInfo = READ_PROP
        root.connmngStatsFIPSCard = READ_PROP
        root.cacheUsageMaxEnt = READ_PROP
        root.cacheUsageCurrEnt = READ_PROP
        return self._rest.read(root, retries)

    def _read_sys_info_container(self, retries=3):
        root = Root()
        root.hwTemperatureStatus = READ_PROP
        root.hwPowerSupplyStatus = READ_PROP
        root.hwFanStatus = READ_PROP
        return self._rest.read(root, retries)

    def _read_sys_capacity_vx(self, retries=3):
        root = Root()
        for k in sys_capacity_vx_map.keys():
            setattr(root, k, READ_PROP)
        return self._rest.read(root, retries)

    def _read_sys_capacity_standalone(self, retries=3):
        root = Root()
        for k in sys_capacity_standalone_map.keys():
            setattr(root, k, READ_PROP)
        return self._rest.read(root, retries)

    @staticmethod
    def _append_dict_result(bean, result):
        for k, v in bean.obj_to_dict().items():
            if v is not None:
                result.update({k: v})


class AlteonMngConfig(AlteonMngBase, DeviceConfig):

    def __init__(self, adc_connection):
        AlteonMngBase.__init__(self, adc_connection)

    def commit(self):
        try:
            apply_result = self.apply()
        except DeviceFunctionError as e:
            self.revert()
            return dict(
                success=False,
                state=e.message
            )
        return dict(
            success=True,
            state=apply_result
        )

    def commit_save(self):
        commit_result = self.commit()
        if commit_result['success']:
            try:
                commit_result = self.save()
            except DeviceFunctionError as e:
                return dict(
                    success=False,
                    state=e.message
                )
        return commit_result

    def apply(self):
        log.debug(' {0}: APPLY, server: {1}'.format(self.__class__.__name__, self.connection.id))
        root = Root()
        root.agApplyConfig = EnumAgApplyConfig.idle
        self._rest.update(root)
        root.agApplyConfig = EnumAgApplyConfig.apply
        self._rest.update(root)
        apply_state = None
        for x in range(0, 20):
            time.sleep(3)
            apply_state = self._rest.read(root)
            if apply_state.agApplyConfig != EnumAgApplyConfig.inprogress:
                break

        if apply_state.agApplyConfig == EnumAgApplyConfig.complete:
            log.debug(' {0}: APPLY, server: {1}, State: {2}'.format(self.__class__.__name__, self.connection.id,
                                                                    apply_state.agApplyConfig.name))
            return apply_state.agApplyConfig.name
        apply_table = self._rest.read_all_no_translation(AgApplyTable())
        raise DeviceFunctionError(self.apply, DeviceType.Alteon, apply_table, apply_state.agApplyConfig)

    def save(self):
        log.debug(' {0}: SAVE, server: {1}'.format(self.__class__.__name__, self.connection.id))
        root = Root()
        root.agSaveConfig = EnumAgSaveConfig.idle
        self._rest.update(root)
        root.agSaveConfig = EnumAgSaveConfig.save
        self._rest.update(root)
        save_state = None
        for x in range(0, 5):
            time.sleep(1)
            save_state = self._rest.read(root)
            if save_state.agSaveConfig != EnumAgSaveConfig.inprogress:
                break

        if save_state.agSaveConfig == EnumAgSaveConfig.complete:
            log.debug(' {0}: SAVE, server: {1}, State: {2}'.format(self.__class__.__name__, self.connection.id,
                                                                   save_state.agSaveConfig.name))
            return save_state.agSaveConfig.name
        save_table = self._rest.read_all_no_translation(AgSaveTable())
        raise DeviceFunctionError(self.save, DeviceType.Alteon, save_table, save_state.agSaveConfig)

    def revert(self):
        log.debug(' {0}: REVERT, server: {1}'.format(self.__class__.__name__, self.connection.id))
        root = Root()
        root.agRevert = EnumAgRevert.revert
        self._rest.update(root)
        return MSG_REVERT

    def revert_apply(self):
        log.debug(' {0}: REVERT_APPLY, server: {1}'.format(self.__class__.__name__, self.connection.id))
        root = Root()
        root.agRevertApply = EnumAgRevertApply.revertApply
        self._rest.update(root)
        return MSG_REVERT_APPLY

    def sync(self):
        log.debug(' {0}: SYNC, server: {1}'.format(self.__class__.__name__, self.connection.id))
        root = Root()
        root.slbOperConfigSync = EnumSlbOperConfigSync.sync
        self._rest.update(root)

        root.slbOperConfigSync = None
        root.agSyncStatus = READ_PROP
        root.agLastSyncInfoTableToString = READ_PROP
        sync_state = None
        for x in range(0, 20):
            time.sleep(1)
            sync_state = self._rest.read(root)
            if sync_state.agSyncStatus != EnumAgSyncStatus.inprogress:
                break
        if sync_state.agSyncStatus == EnumAgSyncStatus.success:
            log.debug(' {0}: SYNC, server: {1}, State: {2}'.format(self.__class__.__name__, self.connection.id,
                                                                   sync_state.agSyncStatus.name))
            return sync_state.agSyncStatus.name

        raise DeviceFunctionError(self.sync, DeviceType.Alteon, sync_state.agLastSyncInfoTableToString,
                                  sync_state.agSyncStatus)

    def diff(self):
        log.debug(' {0}: DIFF, server: {1}'.format(self.__class__.__name__, self.connection.id))
        return self._get_diff(EnumAgDiffState.diff)

    def diff_flash(self):
        log.debug(' {0}: DIFF_FLASH, server: {1}'.format(self.__class__.__name__, self.connection.id))
        return self._get_diff(EnumAgDiffState.flashdiff)

    def _get_diff(self, diff_type):
        root = Root()
        root.agDiffState = EnumAgDiffState.idle
        self._rest.update(root)
        root.agDiffState = diff_type
        self._rest.update(root)
        diff_state = None
        for x in range(0, 5):
            time.sleep(1)
            diff_state = self._rest.read(root)
            if diff_state.agDiffState != EnumAgDiffState.inprogress:
                break

        if diff_state.agDiffState == EnumAgDiffState.complete:
            diff_items = list()
            for item in self._rest.read_all_no_translation(AgDiffTable()):
                diff_items.append(Decoders.hex_str_to_ascii(item['StringVal']))

            log.debug(' {0}: {2}, server: {1} Content: {3}'.format(self.__class__.__name__, self.connection.id,
                                                                   diff_type, diff_items))
            return diff_items

        raise DeviceFunctionError(self.diff, DeviceType.Alteon, None, diff_state.agDiffState)

    def pending_configuration_validation(self):
        diff = self.diff()
        diff_flash = self.diff_flash()
        if DIFF_CHANGE not in diff[0]:
            raise DeviceFunctionError(self.pending_configuration_validation, DeviceType.Alteon,
                                      "pending diff:\n{0}".format(diff))
        if DIFF_CHANGE not in diff_flash[0]:
            raise DeviceFunctionError(self.pending_configuration_validation, DeviceType.Alteon,
                                      "pending diff_flash:\n{0}".format(diff_flash))


class AlteonMngOper(AlteonMngBase, DeviceOper):
    REBOOT = 'reboot'
    REBOOT_STATEFUL = 'reboot_stateful'
    SOFTWARE_UPLOAD = 'software_upload'
    CONFIG_DOWNLOAD = 'config_download'
    CONFIG_UPLOAD = 'config_upload'
    
    def __init__(self, adc_connection):
        AlteonMngBase.__init__(self, adc_connection)
        self._mng_info = AlteonMngInfo(adc_connection)

    @staticmethod
    def _add_pkey(mode):
        if mode:
            return 'pkey=yes'
        else:
            return 'pkey=no'

    def reboot(self):
        log.debug(' {0}: {1}, server: {2}'.format(self.__class__.__name__, self.REBOOT.upper(), self.connection.id))
        root = Root()
        root.agReset = EnumAgReset.reset
        self._rest.update(root)
        return MSG_REBOOT

    def reboot_stateful(self, timeout_seconds: Optional[int] = 600):
        self.reboot()
        while timeout_seconds > 0:
            time.sleep(10)
            if self._mng_info.is_accessible():
                log.debug(' {0}: {1}, server: {2}, State: {3}'.format(self.__class__.__name__,
                                                                      self.REBOOT_STATEFUL.upper(), self.connection.id,
                                                                      MSG_REBOOT_STATEFUL))
                return MSG_REBOOT_STATEFUL
            timeout_seconds -= 10
        raise DeviceFunctionError(self.reboot_stateful, DeviceType.Alteon, 'device timeout')

    def software_upload(self, file_path: str, adc_slot: Optional[int] = None, vadc_slot: Optional[int] = None,
                        password: Optional[str] = None, generate_pass: Optional[bool] = False,
                        timeout_seconds: Optional[int] = 300, http_proxy: Optional[str] = None):
        if adc_slot is None and vadc_slot is None:
            raise DeviceFunctionError(self.software_upload, DeviceType.Alteon, 'no image slot specified')
        else:
            if password is not None:
                path = 'softwareimport?pass={0}&'.format(password)
            else:
                if generate_pass:
                    path = 'softwareimport?pass={0}&'.format(generate_password(self._mng_info.mac_address,
                                                                               get_file_size(file_path),
                                                                               http_proxy_url=http_proxy))
                else:
                    path = 'softwareimport?'
            if adc_slot and vadc_slot:
                path = path + 'type=all&adcimg={0}&vadcimg={1}'.format(adc_slot, vadc_slot)
            else:
                if adc_slot:
                    path = path + 'type=adc&adcimg={0}'.format(adc_slot)
                else:
                    path = 'type=vadc&vadcimg={0}'.format(vadc_slot)
            try:
                with open(file_path, 'rb') as fp_image:
                    self._rest.upload_file_object(path, fp_image, timeout=timeout_seconds)
                    log.debug(' {0}: {1}, server: {2}, State: {3}'.format(self.__class__.__name__,
                                                                          self.SOFTWARE_UPLOAD.upper(),
                                                                          self.connection.id, MSG_IMG_UPLOAD))
                    return MSG_IMG_UPLOAD
            except IOError as e:
                raise DeviceFunctionError(self.software_upload, DeviceType.Alteon, e)

    def config_download(self, file_path: str, include_keys: Optional[bool] = False,
                        passphrase: Optional[PasswordArgument] = None, vx_cfg_only: Optional[bool] = False):
        path = 'getcfg?{0}'.format(self._add_pkey(include_keys))
        if passphrase:
            path += '&passphrase={0}'.format(passphrase)
        if self._mng_info.is_vx:
            if vx_cfg_only:
                path += '&type=global&recovery=all'
            else:
                path += '&type=all&recovery=all'
        r = self._rest.download_file_object(path)
        if not file_path.endswith('.tgz'):
            file_path += '.tgz'
        try:
            with open(file_path, 'w+b') as file:
                file.write(r.raw_content)
                log.debug(' {0}: {1}, server: {2}, State: {3}'.format(self.__class__.__name__,
                                                                      self.CONFIG_DOWNLOAD.upper(),
                                                                      self.connection.id, MSG_CONFIG_DOWNLOAD))
                return MSG_CONFIG_DOWNLOAD
        except IOError as e:
            raise DeviceFunctionError(self.config_download, DeviceType.Alteon, e)

    def config_upload(self, file_path: str, include_keys: Optional[bool] = False, passphrase: Optional[str] = None):
        path = 'configimport?{0}'.format(self._add_pkey(include_keys))
        if passphrase:
            path += '&passphrase={0}'.format(passphrase)
        if self._mng_info.is_vx:
            path += '&type=all&recovery=all'
        try:
            with open(file_path, 'rb') as fp_image:
                self._rest.upload_file_object(path, fp_image)
                log.debug(' {0}: {1}, server: {2}, State: {3}'.format(self.__class__.__name__,
                                                                      self.CONFIG_UPLOAD.upper(),
                                                                      self.connection.id, MSG_CONFIG_UPLOAD))
                return MSG_CONFIG_UPLOAD
        except IOError as e:
            raise DeviceFunctionError(self.config_upload, DeviceType.Alteon, e)

    def set_ha_backup(self, validate_backup_state: Optional[bool] = False, vadc_user: Optional[str] = None,
                      vadc_password: Optional[str] = None):
        def _ha_oper_bck():
            log.debug('device: {0} try to switch to backup'.format(device_name))
            root = Root()
            root.haOperSwitchBackup = EnumHaOperSwitchBackup.backup
            self._rest.update(root)

        device_name = self._mng_info.device_name
        if device_name == '':
            device_name = self._mng_info.connection.get_connection_details()['server']
        if not self._mng_info.is_vx:
            if not self._mng_info.is_master:
                return True
            _ha_oper_bck()
            if validate_backup_state:
                time.sleep(5)
                if self._mng_info.is_master:
                    raise DeviceFunctionError(self.set_ha_backup, DeviceType.Alteon, '{0} is still Master'.format(
                        device_name), 'aborted')
        else:
            connection_details = self.connection.get_connection_details()
            for vadc_addr in self._mng_info.vadcs_address:
                connection_details['server'] = vadc_addr
                if vadc_user:
                    connection_details['user'] = vadc_user
                if vadc_password:
                    connection_details['password'] = vadc_password
                vadc_connection = AlteonDeviceConnection(**connection_details)
                vadc_mng_oper = AlteonMngOper(vadc_connection)
                log.debug('vadc: {0} call set_ha_backup'.format( connection_details['server']))
                vadc_mng_oper.set_ha_backup(validate_backup_state)
        return True
