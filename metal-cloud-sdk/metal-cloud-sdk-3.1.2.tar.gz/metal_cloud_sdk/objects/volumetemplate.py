# -*- coding: utf-8 -*-

class VolumeTemplate(object):
	"""
	A template can be created based on a drive and it has the same
	characteristics and holds the same information as the parent drive.
	"""

	def __init__(self, volume_template_label, volume_template_size_mbytes):
		self.volume_template_label = volume_template_label;
		self.volume_template_size_mbytes = volume_template_size_mbytes;


	"""
	The ID of the volume template.
	"""
	volume_template_id = None;

	"""
	The volume template's unique label. It is editable and can be used to call
	API functions.
	"""
	volume_template_label = None;

	"""
	The volume template's display name.
	"""
	volume_template_display_name = None;

	"""
	Size of the template.
	"""
	volume_template_size_mbytes = None;

	"""
	Wether the template supports booting and running from local disks.
	"""
	volume_template_local_disk_supported = False;

	"""
	A set of all supported methods
	"""
	volume_template_boot_methods_supported = "pxe_iscsi";

	"""
	An arbitrary UTF-8 string which provides a description of the template.
	"""
	volume_template_description = "";

	"""
	Date and time of the template's creation. ISO 8601 timestamp. Example
	format: 2013-11-29T13:00:01Z
	"""
	volume_template_created_timestamp = None;

	"""
	User owner ID.
	"""
	user_id = None;

	"""
	OperatingSystem
	"""
	volume_template_operating_system = None;

	"""
	http(s) template base URL.
	"""
	volume_template_repo_url = None;

	"""
	The deprecation status of the volume template.
	"""
	volume_template_deprecation_status = "not_deprecated";

	"""
	The schema type.
	"""
	type = None;
