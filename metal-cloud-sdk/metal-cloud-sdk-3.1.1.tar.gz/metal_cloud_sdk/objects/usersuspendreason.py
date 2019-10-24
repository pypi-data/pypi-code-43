# -*- coding: utf-8 -*-

class UserSuspendReason(object):
	"""
	A group of InstanceArray and DriveArray infrastructure elements
	preconfigured for specific workloads or roles. Software (SaaS) is
	automatically installed for new instances. The preinstalled software is
	informed when instances are made available or removed.
	"""

	def __init__(self):
		pass;


	"""
	"""
	user_suspend_reason_id = None;

	"""
	"""
	user_id = None;

	"""
	"""
	user_suspend_reason_public_comment = None;

	"""
	ISO 8601 timestamp which holds the date and time when the user suspend
	reason was added.
	"""
	user_suspend_reason_created_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the user suspend
	reason was ended.
	"""
	user_suspend_reason_end_timestamp = None;

	"""
	The schema type
	"""
	type = None;
