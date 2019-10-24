# -*- coding: utf-8 -*-

class SwitchDevice(object):
	"""
	Represents a switch installed in a datacenter.
	"""

	def __init__(self, network_equipment_position, network_equipment_provisioner_type, datacenter_name, network_equipment_driver, network_equipment_management_username, network_equipment_management_password, network_equipment_management_address, network_equipment_management_port, network_equipment_identifier_string, network_equipment_primary_wan_ipv4_subnet_pool, network_equipment_primary_wan_ipv6_subnet_pool, network_equipment_primary_san_subnet_pool, network_equipment_quarantine_vlan, network_equipment_quarantine_subnet_start, network_equipment_quarantine_subnet_end, network_equipment_quarantine_subnet_netmask, network_equipment_quarantine_subnet_gateway, network_equipment_country, network_equipment_city, network_equipment_datacenter, network_equipment_datacenter_room, network_equipment_datacenter_rack, network_equipment_rack_position_upper_u, network_equipment_rack_position_lower_u, network_equipment_is_virtual_chassis, network_equipment_serial_numbers, network_equipment_upstream_hostnames, chassis_rack_id):
		self.network_equipment_position = network_equipment_position;
		self.network_equipment_provisioner_type = network_equipment_provisioner_type;
		self.datacenter_name = datacenter_name;
		self.network_equipment_driver = network_equipment_driver;
		self.network_equipment_management_username = network_equipment_management_username;
		self.network_equipment_management_password = network_equipment_management_password;
		self.network_equipment_management_address = network_equipment_management_address;
		self.network_equipment_management_port = network_equipment_management_port;
		self.network_equipment_identifier_string = network_equipment_identifier_string;
		self.network_equipment_primary_wan_ipv4_subnet_pool = network_equipment_primary_wan_ipv4_subnet_pool;
		self.network_equipment_primary_wan_ipv6_subnet_pool = network_equipment_primary_wan_ipv6_subnet_pool;
		self.network_equipment_primary_san_subnet_pool = network_equipment_primary_san_subnet_pool;
		self.network_equipment_quarantine_vlan = network_equipment_quarantine_vlan;
		self.network_equipment_quarantine_subnet_start = network_equipment_quarantine_subnet_start;
		self.network_equipment_quarantine_subnet_end = network_equipment_quarantine_subnet_end;
		self.network_equipment_quarantine_subnet_netmask = network_equipment_quarantine_subnet_netmask;
		self.network_equipment_quarantine_subnet_gateway = network_equipment_quarantine_subnet_gateway;
		self.network_equipment_country = network_equipment_country;
		self.network_equipment_city = network_equipment_city;
		self.network_equipment_datacenter = network_equipment_datacenter;
		self.network_equipment_datacenter_room = network_equipment_datacenter_room;
		self.network_equipment_datacenter_rack = network_equipment_datacenter_rack;
		self.network_equipment_rack_position_upper_u = network_equipment_rack_position_upper_u;
		self.network_equipment_rack_position_lower_u = network_equipment_rack_position_lower_u;
		self.network_equipment_is_virtual_chassis = network_equipment_is_virtual_chassis;
		self.network_equipment_serial_numbers = network_equipment_serial_numbers;
		self.network_equipment_upstream_hostnames = network_equipment_upstream_hostnames;
		self.chassis_rack_id = chassis_rack_id;


	"""
	Specifies whether the switch faces the Internet (north) or is internal (tor)
	"""
	network_equipment_position = None;

	"""
	Provisioner of network encapsulation.
	"""
	network_equipment_provisioner_type = None;

	"""
	The datacenter where the network equipment is available for use.
	"""
	datacenter_name = None;

	"""
	The driver used by the network equipment.
	"""
	network_equipment_driver = None;

	"""
	The user name used to log in to the network equipment.
	"""
	network_equipment_management_username = None;

	"""
	The password used to log in to the network equipment.
	"""
	network_equipment_management_password = None;

	"""
	The address used to log in to the network equipment.
	"""
	network_equipment_management_address = None;

	"""
	The port utilized to log in to the network equipment.
	"""
	network_equipment_management_port = None;

	"""
	Optional if the <code>bAutoDescribe</code> parameter of
	<code>switch_device_create</code> is set to true.
	"""
	network_equipment_identifier_string = None;

	"""
	Network address (first IP) of a /22 subnet. <a:schema>Subnet</a:schema>
	configuration details.
	"""
	network_equipment_primary_wan_ipv4_subnet_pool = None;

	"""
	Network address (first IP) of a /53 subnet. <a:schema>Subnet</a:schema>
	configuration details
	"""
	network_equipment_primary_wan_ipv6_subnet_pool = None;

	"""
	Network address (first IP) of a /21 subnet. <a:schema>Subnet</a:schema>
	configuration details
	"""
	network_equipment_primary_san_subnet_pool = None;

	"""
	Normally <code>5</code>, by convention.
	"""
	network_equipment_quarantine_vlan = None;

	"""
	For example: 172.17.0.1 (subnet always allocated from this larger subnet:
	172.16.0.0/15).
	"""
	network_equipment_quarantine_subnet_start = None;

	"""
	For example: 172.17.0.254 (subnet always allocated from this larger subnet:
	172.16.0.0/15).
	"""
	network_equipment_quarantine_subnet_end = None;

	"""
	Normally always 255.255.255.0, by convention.
	"""
	network_equipment_quarantine_subnet_netmask = None;

	"""
	IPv4 address. Usually the same with the first IP in the subnet (.1).
	"""
	network_equipment_quarantine_subnet_gateway = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_country = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_city = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_datacenter = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_datacenter_room = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_datacenter_rack = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_rack_position_upper_u = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_rack_position_lower_u = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_is_virtual_chassis = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_serial_numbers = None;

	"""
	Information regarding the switch device's physical location.
	"""
	network_equipment_upstream_hostnames = None;

	"""
	Chassis_rack_id of associated chassis_rack, if existent (may be null).
	"""
	chassis_rack_id = None;

	"""
	network_equipment_id of a ToR logical (db) switch which is the same physical
	switch as this North switch. Must be Null if this North switch is
	independent, or if this is a ToR switch.
	"""
	network_equipment_tor_linked_id = None;

	"""
	The schema type.
	"""
	type = None;
