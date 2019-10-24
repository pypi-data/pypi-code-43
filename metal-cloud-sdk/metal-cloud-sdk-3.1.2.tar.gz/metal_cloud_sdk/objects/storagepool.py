# -*- coding: utf-8 -*-

class StoragePool(object):
	"""
	Represents an iSCSI storage item in a datacenter
	"""

	def __init__(self, datacenter_name, storage_driver, storage_pool_endpoint, storage_pool_iscsi_hostname, storage_pool_name, storage_pool_options_json, storage_pool_target_iqn, storage_pool_username, storage_type, user_id):
		self.datacenter_name = datacenter_name;
		self.storage_driver = storage_driver;
		self.storage_pool_endpoint = storage_pool_endpoint;
		self.storage_pool_iscsi_hostname = storage_pool_iscsi_hostname;
		self.storage_pool_name = storage_pool_name;
		self.storage_pool_options_json = storage_pool_options_json;
		self.storage_pool_target_iqn = storage_pool_target_iqn;
		self.storage_pool_username = storage_pool_username;
		self.storage_type = storage_type;
		self.user_id = user_id;


	"""
	Datacenter where this storage resides.
	"""
	datacenter_name = None;

	"""
	The storage API driver.
	"""
	storage_driver = None;

	"""
	Endpoint for the pool's JSONRPC / REST API.
	"""
	storage_pool_endpoint = None;

	"""
	Unique identifier for the storage pool. It is automatically generated and
	cannot be changed.
	"""
	storage_pool_id = None;

	"""
	Boolean value that marks pool as being in use/in maintenance.
	"""
	storage_pool_in_maintenance = False;

	"""
	Boolean value that marks pool as being experimental or not.
	"""
	storage_pool_is_experimental = False;

	"""
	The primary iSCSI IP of the storage pool.
	"""
	storage_pool_iscsi_hostname = None;

	"""
	Secondary IPs on which the target is available
	"""
	storage_pool_alternate_san_ips = [];

	"""
	The iSCSI port on which the storage machine is listening (usually 3260).
	"""
	storage_pool_iscsi_port = 3260;

	"""
	The name of the storage pool.
	"""
	storage_pool_name = None;

	"""
	Options to pass to the storage pool, JSON encoded. Usually contains a
	"volume_name" field.
	"""
	storage_pool_options_json = None;

	"""
	Password used to authenticate to the storage pool's API.
	"""
	storage_pool_password = None;

	"""
	The status of the storage pool.
	"""
	storage_pool_status = "active";

	"""
	The storage pool's target iSCSI Qualified Name (IQN). This functions as a
	worldwide unique identifier to which initiators connect if there are
	multiple pools on the same iSCSI IP address.
	"""
	storage_pool_target_iqn = None;

	"""
	Username used to authenticate to the storage pool's API.
	"""
	storage_pool_username = None;

	"""
	The type of disks that will be used in the storage pool.
	"""
	storage_type = None;

	"""
	The ID of the user, if it is not null.
	"""
	user_id = None;

	"""
	Priority for allocation of drives on the storage pool, in the range 1-100.
	"""
	storage_pool_drive_priority = 50;

	"""
	Priority for allocation of shared drives on the storage pool, in the range
	1-100.
	"""
	storage_pool_shared_drive_priority = 50;

	"""
	The schema type.
	"""
	type = None;
