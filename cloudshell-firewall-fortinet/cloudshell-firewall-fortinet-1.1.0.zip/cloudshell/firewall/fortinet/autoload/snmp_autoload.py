import os
import re

from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder, AutoLoadDetails
from cloudshell.devices.standards.firewall.autoload_structure import GenericResource, \
    GenericChassis, GenericPort, GenericPortChannel

from cloudshell.firewall.fortinet.helpers.cached_property import cached_property
from cloudshell.firewall.fortinet.helpers.exceptions import FortiNetException

ENT_MIB = 'ENTITY-MIB'
ENT_PHYSICAL_CLASS = 'entPhysicalClass'
ENT_PHYSICAL_NAME = 'entPhysicalName'
ENT_PHYSICAL_MODEL_NAME = 'entPhysicalModelName'
ENT_PHYSICAL_CONTAINED_IN = 'entPhysicalContainedIn'
ENT_PHYSICAL_DESCR = 'entPhysicalDescr'
ENT_PHYSICAL_SERIAL_NUM = 'entPhysicalSerialNum'
IF_MIB = 'IF-MIB'
IF_NAME = 'ifName'
IF_DESCR = 'ifDesc'
IF_TYPE = 'ifType'
IF_ALIAS = 'ifAlias'
IF_PHYS_ADDRESS = 'ifPhysAddress'
IF_MTU = 'ifMtu'
IF_HIGH_SPEED = 'ifHighSpeed'
IP_MIB = 'IP-MIB'
IP_IF_INDEX = 'ipAdEntIfIndex'
IPV6_MIB = 'IPV6-MIB'
IPV6_ADDR_TYPE = 'ipv6AddrType'


class SNMPAutoload(object):
    VENDOR = 'FortiNet'
    FORTINET_SYS_OBJ_ID = '12356'

    def __init__(self, snmp_service, shell_name, shell_type, resource_name, logger):
        """SNMP Autoload

        :param cloudshell.snmp.quali_snmp.QualiSnmp snmp_service:
        :param str shell_name:
        :param str shell_type:
        :param str resource_name:
        :param logging.Logger logger:
        """

        self.snmp_service = snmp_service
        self.shell_name = shell_name
        self.shell_type = shell_type
        self.resource_name = resource_name
        self.logger = logger

        self.chassis = {}
        self.resource = GenericResource(shell_name, resource_name, resource_name, shell_type)

        self._chassis_ent_ids = set()
        self._ports_ent_ids = set()

    def discover(self, supported_os):
        """General entry point for autoload,
            read device structure and attributes: chassis, ports, port-channels

        :return: AutoLoadDetails object
        :rtype: AutoLoadDetails
        """

        if not self._is_valid_device_os(supported_os):
            raise FortiNetException('Unsupported device OS')

        self.logger.info('*' * 70)
        self.logger.info('Start SNMP discovery process .....')

        self._load_mibs()
        self.snmp_service.load_mib(['FORTINET-FORTIGATE-MIB', 'FORTINET-CORE-MIB'])
        self._get_device_details()

        self._load_snmp_tables()
        self._get_entity_ids()
        self._add_chassis()
        self._add_ports()
        self._add_port_channels()

        autoload_details = AutoloadDetailsBuilder(self.resource).autoload_details()
        self._log_autoload_details(autoload_details)
        return autoload_details

    @cached_property
    def _dict_if_port_name_to_id(self):
        table = self.snmp_service.get_table(IF_MIB, IF_NAME)
        return {attrs[IF_NAME]: id_ for id_, attrs in table.items()}

    @cached_property
    def _dict_if_port_desc_to_id(self):
        table = self.snmp_service.get_table(IF_MIB, IF_DESCR)
        return {attrs[IF_DESCR]: id_ for id_, attrs in table.items()}

    @cached_property
    def _dict_if_port_id_to_ipv4_addr(self):
        table = self.snmp_service.get_table(IP_MIB, IP_IF_INDEX)
        return {int(attrs[IP_IF_INDEX]): ip for ip, attrs in table.items()}

    @cached_property
    def _dict_if_port_id_to_ipv6_addr(self):
        table = self.snmp_service.get_table(IPV6_MIB, IPV6_ADDR_TYPE)
        result_table = {}
        for index in table:
            if_port_id, ipv6_addr = index.split('.', 1)
            result_table[int(if_port_id)] = ipv6_addr
        return result_table

    def _load_mibs(self):
        """Loads FortiNet specific mibs inside snmp handler"""

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp_service.update_mib_sources(path)

    def _load_snmp_tables(self):
        """Load all FortiNet required snmp tables"""

        self.logger.info('Start loading MIB tables:')

        self.port_channel_table = self.snmp_service.get_table(
            'IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID')
        self.lldp_remote_table = self.snmp_service.get_table('LLDP-MIB', 'lldpRemSysName')
        self.lldp_local_table = {v['lldpLocPortDesc']: k for k, v in self.snmp_service.get_table(
            'LLDP-MIB', 'lldpLocPortDesc').iteritems()}

        self.logger.info('MIB Tables loaded successfully')

    def _get_unique_id(self, obj_type, id_):
        return '{}.{}.{}'.format(self.resource_name, obj_type, id_)

    def _get_entity_ids(self):
        table = self.snmp_service.get_table(ENT_MIB, ENT_PHYSICAL_CLASS)
        for id_, attrs in table.items():
            if attrs[ENT_PHYSICAL_CLASS].strip("'") == 'port':
                self._ports_ent_ids.add(id_)
            elif attrs[ENT_PHYSICAL_CLASS].strip("'") == 'chassis':
                self._chassis_ent_ids.add(id_)

    def _build_chassis(self, index):
        uniq_id = self._get_unique_id('chassis', index)
        chassis_obj = GenericChassis(self.shell_name, 'Chassis {}'.format(index), uniq_id)

        chassis_obj.model = (
                self.snmp_service.get_property(ENT_MIB, ENT_PHYSICAL_MODEL_NAME, index)
                or self.snmp_service.get_property(ENT_MIB, ENT_PHYSICAL_DESCR, index)
        )
        chassis_obj.serial_number = self.snmp_service.get_property(
            ENT_MIB, ENT_PHYSICAL_SERIAL_NUM, index
        )

        return chassis_obj

    def _add_chassis(self):
        self.logger.info('Building Chassis')

        for id_ in self._chassis_ent_ids:
            chassis_obj = self._build_chassis(id_)
            self.resource.add_sub_resource(id_, chassis_obj)
            self.chassis[id_] = chassis_obj

        self.logger.info('Building Chassis completed')

    def _build_port(self, port_if_id, name):
        unique_id = self._get_unique_id('port', port_if_id)
        port_obj = GenericPort(self.shell_name, name, unique_id)

        port_obj.port_description = self.snmp_service.get_property(
            IF_MIB, IF_ALIAS, port_if_id
        )
        port_obj.l2_protocol_type = self.snmp_service.get_property(
            IF_MIB, IF_TYPE, port_if_id
        ).strip("'")
        port_obj.mac_address = self.snmp_service.get_property(
            IF_MIB, IF_PHYS_ADDRESS, port_if_id
        )
        port_obj.mtu = int(self.snmp_service.get_property(IF_MIB, IF_MTU, port_if_id))
        port_obj.bandwidth = int(
            self.snmp_service.get_property(IF_MIB, IF_HIGH_SPEED, port_if_id)
        )
        port_obj.ipv4_address = self._dict_if_port_id_to_ipv4_addr.get(port_if_id)
        port_obj.ipv6_address = self._dict_if_port_id_to_ipv6_addr.get(port_if_id)
        port_obj.duplex = self._get_port_duplex(port_if_id)
        port_obj.auto_negotiation = self._get_port_auto_negotiation(port_if_id)
        port_obj.adjacent = self._get_adjacent(name)

        self.logger.info('Added {} Port'.format(name))
        return port_obj

    def _add_ports(self):
        self.logger.info('Loading Ports')

        if self._ports_ent_ids:
            self._add_ports_with_ent_table()
        else:
            self.logger.info(
                "Entity table doesn't have ports in it. "
                "Try to autoload ports from IF table."
            )
            self._add_ports_without_ent_table()

        self.logger.info('Building Ports completed')

    @staticmethod
    def _is_valid_port_name(port_name):
        return port_name.lower() != 'modem'

    def _add_ports_with_ent_table(self):
        for ent_id in self._ports_ent_ids:
            ent_name = self.snmp_service.get_property(
                ENT_MIB, ENT_PHYSICAL_NAME, ent_id
            )
            if not self._is_valid_port_name(ent_name):
                continue

            if_port_id = self._get_if_port_id(ent_name)
            port_obj = self._build_port(if_port_id, ent_name)
            parent_id = self.snmp_service.get_property(
                ENT_MIB,  ENT_PHYSICAL_CONTAINED_IN, ent_id
            )

            chassis = self.chassis[int(parent_id)]
            chassis.add_sub_resource(ent_id, port_obj)

    def _get_if_port_id(self, ent_name):
        if_port_id = self._dict_if_port_name_to_id.get(ent_name)
        if not if_port_id:
            if_port_id = self._dict_if_port_desc_to_id.get(ent_name)

        return if_port_id

    def _add_ports_without_ent_table(self):
        table = self.snmp_service.get_table(IF_MIB, IF_TYPE)
        for if_port_id, attrs in table.items():
            if attrs[IF_TYPE].strip("'") == 'ethernetCsmacd':
                name = self.snmp_service.get_property(IF_MIB, IF_NAME, if_port_id)
                if not name:
                    name = self.snmp_service.get_property(IF_MIB, IF_DESCR, if_port_id)

                port_obj = self._build_port(if_port_id, name)

                if len(self.chassis) > 1:
                    self.logger.info(
                        "Entity table doesn't have ports so we don't know in which "
                        "chassis add it. So we will add to the first chassis."
                    )

                chassis = self.chassis[min(self.chassis.keys())]
                chassis.add_sub_resource(if_port_id, port_obj)

    def _get_port_duplex(self, id_):
        duplex = self.snmp_service.get_property('EtherLike-MIB', 'dot3StatsDuplexStatus', id_)
        if duplex.strip("'") != 'fullDuplex':
            return 'Half'
        return 'Full'

    def _get_port_auto_negotiation(self, id_):
        status = self.snmp_service.get_property('MAU-MIB', 'ifMauAutoNegAdminStatus', id_)
        return status.strip("'") == 'enabled'

    def _build_port_channel(self, id_):
        unique_id = self._get_unique_id('port_channel', id_)
        if_name = self.snmp_service.get_property(IF_MIB, IF_NAME, id_)

        port_channel = GenericPortChannel(self.shell_name, if_name, unique_id)

        port_channel.port_description = self.snmp_service.get_property(
            IF_MIB, IF_ALIAS, id_
        )
        port_channel.associated_ports = '; '.join(self._get_associated_ports(id_))
        port_channel.ipv4_address = self._dict_if_port_id_to_ipv4_addr.get(id_)
        port_channel.ipv6_address = self._dict_if_port_id_to_ipv6_addr.get(id_)

        self.logger.info('Added {} Port Channel'.format(if_name))
        return port_channel

    def _add_port_channels(self):
        self.logger.info('Building Port Channels')

        table = self.snmp_service.get_table(IF_MIB, IF_TYPE)
        for id_, attrs in table.items():
            if attrs[IF_TYPE].strip("'") == 'ieee8023adLag':
                port_channel = self._build_port_channel(id_)
                self.resource.add_sub_resource(id_, port_channel)

        self.logger.info('Building Port Channels completed')

    def _get_associated_ports(self, pc_id):
        return [key for key, attrs in self.port_channel_table.items()
                if str(pc_id) in attrs['dot3adAggPortAttachedAggID']]

    def _log_autoload_details(self, autoload_details):
        """Logging autoload details

        :param autoload_details:
        """

        self.logger.debug('-------------------- <RESOURCES> ----------------------')
        for resource in autoload_details.resources:
            self.logger.debug(
                '{0:15}, {1:20}, {2}'.format(resource.relative_address, resource.name,
                                             resource.unique_identifier))
        self.logger.debug('-------------------- </RESOURCES> ----------------------')

        self.logger.debug('-------------------- <ATTRIBUTES> ---------------------')
        for attribute in autoload_details.attributes:
            self.logger.debug('-- {0:15}, {1:60}, {2}'.format(attribute.relative_address,
                                                              attribute.attribute_name,
                                                              attribute.attribute_value))
        self.logger.debug('-------------------- </ATTRIBUTES> ---------------------')

    def _is_valid_device_os(self, supported_os):
        """Validate device OS using snmp

        :rtype: bool
        :return: True or False
        """

        sys_obj_id = self.snmp_service.get_property('SNMPv2-MIB', 'sysObjectID', 0)

        if re.search(r'\.{}\.'.format(self.FORTINET_SYS_OBJ_ID), sys_obj_id):
            return True
        else:
            error_message = 'Incompatible driver! Please use this driver for "{0}" ' \
                            'operation system(s)'.format(str(tuple(supported_os)))
            self.logger.error(error_message)
            return False

    def _get_device_details(self):
        """ Get root element attributes """

        self.logger.info('Building Root')

        self.resource.contact_name = self.snmp_service.get_property('SNMPv2-MIB', 'sysContact', '0')
        self.resource.system_name = self.snmp_service.get_property('SNMPv2-MIB', 'sysName', '0')
        self.resource.location = self.snmp_service.get_property('SNMPv2-MIB', 'sysLocation', '0')
        self.resource.vendor = self.VENDOR
        self.resource.os_version = self.snmp_service.get_property(
            'FORTINET-FORTIGATE-MIB', 'fgSysVersion', 0)
        self.resource.model = self._get_device_model()

    def _get_device_model(self):
        """Get device model

        :return: device model
        :rtype: str
        """

        output = self.snmp_service.get_property('SNMPv2-MIB', 'sysObjectID', '0')
        match = re.search(r'::(?P<model>\S+$)', output)
        return match.groupdict()['model']

    def _get_adjacent(self, interface_name):
        """Get connected device interface and device name to the specified port
            using lldp protocol

        :param interface_name:
        :return: device's name and port connected to port id
        :rtype: str
        """

        result_template = '{remote_host} through {remote_port}'
        result = ''
        if self.lldp_local_table:
            key = self.lldp_local_table.get(interface_name, None)
            if key:
                for port_id, rem_table in self.lldp_remote_table.iteritems():
                    if '.{0}.'.format(key) in port_id:
                        remoute_sys_name = rem_table.get('lldpRemSysName', '')
                        remoute_port_name = self.snmp_service.get_property(
                            'LLDP-MIB', 'lldpRemPortDesc', port_id)
                        if remoute_port_name and remoute_sys_name:
                            result = result_template.format(remote_host=remoute_sys_name,
                                                            remote_port=remoute_port_name)
                            break
        return result
