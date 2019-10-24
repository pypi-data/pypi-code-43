# -*- coding: utf-8 -*-

class Server(object):
	"""
	Represents a server in a datacenter.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the server. It is automatically generated and cannot be edited.
	"""
	server_id = None;

	"""
	Server UUID.
	"""
	server_uuid = None;

	"""
	Full bandwidth available.
	"""
	server_network_total_capacity_mbps = None;

	"""
	The server power status which can have one of the values:
	<code>SERVER_POWER_STATUS_ON</code>, <code>SERVER_POWER_STATUS_OFF</code>.
	"""
	server_power_status = None;

	"""
	The cores of a CPU.
	"""
	server_processor_core_count = 1;

	"""
	The clock speed of a CPU.
	"""
	server_processor_core_mhz = 1000;

	"""
	The CPU count on the server.
	"""
	server_processor_count = 1;

	"""
	The RAM capacity.
	"""
	server_ram_gbytes = 1;

	"""
	The minimum number of physical disks.
	"""
	server_disk_count = 0;

	"""
	The minimum size of a single disk.
	"""
	server_disk_size_mbytes = 0;

	"""
	The type of physical disks.
	"""
	server_disk_type = "none";

	"""
	The name of the processor.
	"""
	server_processor_name = None;

	"""
	The name of the server.
	"""
	server_product_name = None;

	"""
	The ID of the server type. See <code>server_types()</code> for more detalis.
	"""
	server_type_id = None;

	"""
	The <a:schema>ServerInterface</a:schema> objects.
	"""
	server_interfaces = None;

	"""
	The <a:schema>ServerDisk</a:schema> objects
	"""
	server_disks = None;

	"""
	The schema type
	"""
	type = None;
