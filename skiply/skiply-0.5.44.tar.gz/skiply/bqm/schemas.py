# Copyright 2018 Skiply SAS

""" Define schema of BQ tables. """

from __future__ import absolute_import


def getDWHSchema_alertDatamart():
	from apache_beam.io.gcp.internal.clients import bigquery
	table_schema = bigquery.TableSchema()

	# Fields that use standard types.	
	notif_id_schema = bigquery.TableFieldSchema()
	notif_id_schema.name = 'notif_id'
	notif_id_schema.type = 'integer'
	notif_id_schema.mode = 'required'
	notif_id_schema.description = 'ID of the notification'
	table_schema.fields.append(notif_id_schema)
	
	notif_timestamp_schema = bigquery.TableFieldSchema()
	notif_timestamp_schema.name = 'notif_timestamp'
	notif_timestamp_schema.type = 'timestamp'
	notif_timestamp_schema.mode = 'required'
	notif_timestamp_schema.description = 'Timestamp when was recorded the notification'
	table_schema.fields.append(notif_timestamp_schema)
	
	notif_type_schema = bigquery.TableFieldSchema()
	notif_type_schema.name = 'notif_type'
	notif_type_schema.type = 'string'
	notif_type_schema.mode = 'required'
	notif_type_schema.description = 'Type of notification'
	table_schema.fields.append(notif_type_schema)
	
	notif_recipients_schema = bigquery.TableFieldSchema()
	notif_recipients_schema.name = 'notif_recipients'
	notif_recipients_schema.type = 'string'
	notif_recipients_schema.mode = 'required'
	notif_recipients_schema.description = 'Recipients of the notification'
	table_schema.fields.append(notif_recipients_schema)
	
	data_id_schema = bigquery.TableFieldSchema()
	data_id_schema.name = 'data_id'
	data_id_schema.type = 'integer'
	data_id_schema.mode = 'required'
	data_id_schema.description = 'ID of the data associated in so_atim_data'
	table_schema.fields.append(data_id_schema)
	
	device_skiply_id_schema = bigquery.TableFieldSchema()
	device_skiply_id_schema.name = 'device_skiply_id'
	device_skiply_id_schema.type = 'string'
	device_skiply_id_schema.mode = 'nullable'
	device_skiply_id_schema.description = 'ID given by Skiply to the concerned device'
	table_schema.fields.append(device_skiply_id_schema)
	
	device_id_schema = bigquery.TableFieldSchema()
	device_id_schema.name = 'device_id'
	device_id_schema.type = 'string'
	device_id_schema.mode = 'required'
	device_id_schema.description = 'ID of the hardware for the concerned device'
	table_schema.fields.append(device_id_schema)
	
	device_description_schema = bigquery.TableFieldSchema()
	device_description_schema.name = 'device_description'
	device_description_schema.type = 'string'
	device_description_schema.mode = 'nullable'
	device_description_schema.description = 'Description of the device'
	table_schema.fields.append(device_description_schema)
	
	device_button_index_schema = bigquery.TableFieldSchema()
	device_button_index_schema.name = 'device_button_index'
	device_button_index_schema.type = 'integer'
	device_button_index_schema.mode = 'required'
	device_button_index_schema.description = 'Index of the pressed button'
	table_schema.fields.append(device_button_index_schema)
	
	device_button_label_schema = bigquery.TableFieldSchema()
	device_button_label_schema.name = 'device_button_label'
	device_button_label_schema.type = 'string'
	device_button_label_schema.mode = 'nullable'
	device_button_label_schema.description = 'Label of the pressed button'
	table_schema.fields.append(device_button_label_schema)
	
	device_latitude_schema = bigquery.TableFieldSchema()
	device_latitude_schema.name = 'device_latitude'
	device_latitude_schema.type = 'string'
	device_latitude_schema.mode = 'nullable'
	device_latitude_schema.description = 'Latitude of the device'
	table_schema.fields.append(device_latitude_schema)
	
	device_longitude_schema = bigquery.TableFieldSchema()
	device_longitude_schema.name = 'device_longitude'
	device_longitude_schema.type = 'string'
	device_longitude_schema.mode = 'nullable'
	device_longitude_schema.description = 'Longitude of the device'
	table_schema.fields.append(device_longitude_schema)
	
	device_battery_level_schema = bigquery.TableFieldSchema()
	device_battery_level_schema.name = 'device_battery_level'
	device_battery_level_schema.type = 'string'
	device_battery_level_schema.mode = 'nullable'
	device_battery_level_schema.description = 'Battery level of the device'
	table_schema.fields.append(device_battery_level_schema)
	
	device_last_transmission_schema = bigquery.TableFieldSchema()
	device_last_transmission_schema.name = 'device_last_transmission'
	device_last_transmission_schema.type = 'timestamp'
	device_last_transmission_schema.mode = 'nullable'
	device_last_transmission_schema.description = 'Timestamp when the device last transmits (vote, battery level, ...)'
	table_schema.fields.append(device_last_transmission_schema)
	
	device_last_data_transmission_schema = bigquery.TableFieldSchema()
	device_last_data_transmission_schema.name = 'device_last_data_transmission'
	device_last_data_transmission_schema.type = 'timestamp'
	device_last_data_transmission_schema.mode = 'nullable'
	device_last_data_transmission_schema.description = 'Timestamp when the device last transmits votes'
	table_schema.fields.append(device_last_data_transmission_schema)
	
	device_keyboard_id_schema = bigquery.TableFieldSchema()
	device_keyboard_id_schema.name = 'device_keyboard_id'
	device_keyboard_id_schema.type = 'integer'
	device_keyboard_id_schema.mode = 'nullable' # should be REQUIDRED
	device_keyboard_id_schema.description = 'ID of the keyboard'
	table_schema.fields.append(device_keyboard_id_schema)
	
	device_keyboard_name_schema = bigquery.TableFieldSchema()
	device_keyboard_name_schema.name = 'device_keyboard_name'
	device_keyboard_name_schema.type = 'string'
	device_keyboard_name_schema.mode = 'nullable'
	device_keyboard_name_schema.description = 'Name of the keyboard'
	table_schema.fields.append(device_keyboard_name_schema)
	
	device_keyboard_type_schema = bigquery.TableFieldSchema()
	device_keyboard_type_schema.name = 'device_keyboard_type'
	device_keyboard_type_schema.type = 'integer'
	device_keyboard_type_schema.mode = 'nullable'
	device_keyboard_type_schema.description = 'Type of keyboard'
	table_schema.fields.append(device_keyboard_type_schema)

	group_id_schema = bigquery.TableFieldSchema()
	group_id_schema.name = 'group_id'
	group_id_schema.type = 'integer'
	group_id_schema.mode = 'nullable' # should be REQUIRED
	group_id_schema.description = 'ID of the group'
	table_schema.fields.append(group_id_schema)
	
	group_name_schema = bigquery.TableFieldSchema()
	group_name_schema.name = 'group_name'
	group_name_schema.type = 'string'
	group_name_schema.mode = 'nullable'
	group_name_schema.description = 'Name of the group'
	table_schema.fields.append(group_name_schema)
	
	group_description_schema = bigquery.TableFieldSchema()
	group_description_schema.name = 'group_description'
	group_description_schema.type = 'string'
	group_description_schema.mode = 'nullable'
	group_description_schema.description = 'Description of the group'
	table_schema.fields.append(group_description_schema)
	
	entity_id_schema = bigquery.TableFieldSchema()
	entity_id_schema.name = 'entity_id'
	entity_id_schema.type = 'integer'
	entity_id_schema.mode = 'nullable'
	entity_id_schema.description = 'ID of the entity'
	table_schema.fields.append(entity_id_schema)
	
	entity_name_schema = bigquery.TableFieldSchema()
	entity_name_schema.name = 'entity_name'
	entity_name_schema.type = 'string'
	entity_name_schema.mode = 'nullable'
	entity_name_schema.description = 'Name of the entity'
	table_schema.fields.append(entity_name_schema)
	
	entity_description_schema = bigquery.TableFieldSchema()
	entity_description_schema.name = 'entity_description'
	entity_description_schema.type = 'string'
	entity_description_schema.mode = 'nullable'
	entity_description_schema.description = 'Description of the entity'
	table_schema.fields.append(entity_description_schema)
	
	entity_timezone_schema = bigquery.TableFieldSchema()
	entity_timezone_schema.name = 'entity_timezone'
	entity_timezone_schema.type = 'string'
	entity_timezone_schema.mode = 'nullable'
	entity_timezone_schema.description = 'Timezone of the entity'
	table_schema.fields.append(entity_timezone_schema)
		
	question_id_schema = bigquery.TableFieldSchema()
	question_id_schema.name = 'question_id'
	question_id_schema.type = 'integer'
	question_id_schema.mode = 'nullable'
	question_id_schema.description = 'ID of the question'
	table_schema.fields.append(question_id_schema)
	
	question_label_schema = bigquery.TableFieldSchema()
	question_label_schema.name = 'question_label'
	question_label_schema.type = 'string'
	question_label_schema.mode = 'nullable'
	question_label_schema.description = 'Label of the question'
	table_schema.fields.append(question_label_schema)

	return table_schema


def getDWHSchema_datamart():
	from apache_beam.io.gcp.internal.clients import bigquery
	table_schema = bigquery.TableSchema()

	# Fields that use standard types.	
	data_id_schema = bigquery.TableFieldSchema()
	data_id_schema.name = 'data_id'
	data_id_schema.type = 'integer'
	data_id_schema.mode = 'required'
	data_id_schema.description = 'ID of the data associated in so_atim_data'
	table_schema.fields.append(data_id_schema)
	
	data_timestamp_schema = bigquery.TableFieldSchema()
	data_timestamp_schema.name = 'data_timestamp'
	data_timestamp_schema.type = 'timestamp'
	data_timestamp_schema.mode = 'required'
	data_timestamp_schema.description = 'Timestamp when was recorded the data'
	table_schema.fields.append(data_timestamp_schema)
	
	vote_schema = bigquery.TableFieldSchema()
	vote_schema.name = 'votes'
	vote_schema.type = 'integer'
	vote_schema.mode = 'required'
	vote_schema.description = 'Number of votes'
	table_schema.fields.append(vote_schema)
	
	device_skiply_id_schema = bigquery.TableFieldSchema()
	device_skiply_id_schema.name = 'device_skiply_id'
	device_skiply_id_schema.type = 'string'
	device_skiply_id_schema.mode = 'required'
	device_skiply_id_schema.description = 'ID given by Skiply to the concerned device'
	table_schema.fields.append(device_skiply_id_schema)
	
	device_id_schema = bigquery.TableFieldSchema()
	device_id_schema.name = 'device_id'
	device_id_schema.type = 'string'
	device_id_schema.mode = 'required'
	device_id_schema.description = 'ID of the hardware for the concerned device'
	table_schema.fields.append(device_id_schema)
	
	device_description_schema = bigquery.TableFieldSchema()
	device_description_schema.name = 'device_description'
	device_description_schema.type = 'string'
	device_description_schema.mode = 'nullable'
	device_description_schema.description = 'Description of the device'
	table_schema.fields.append(device_description_schema)
	
	device_button_index_schema = bigquery.TableFieldSchema()
	device_button_index_schema.name = 'device_button_index'
	device_button_index_schema.type = 'integer'
	device_button_index_schema.mode = 'required'
	device_button_index_schema.description = 'Index of the pressed button'
	table_schema.fields.append(device_button_index_schema)
	
	device_button_label_schema = bigquery.TableFieldSchema()
	device_button_label_schema.name = 'device_button_label'
	device_button_label_schema.type = 'string'
	device_button_label_schema.mode = 'nullable'
	device_button_label_schema.description = 'Label of the pressed button'
	table_schema.fields.append(device_button_label_schema)
	
	device_latitude_schema = bigquery.TableFieldSchema()
	device_latitude_schema.name = 'device_latitude'
	device_latitude_schema.type = 'string'
	device_latitude_schema.mode = 'nullable'
	device_latitude_schema.description = 'Latitude of the device'
	table_schema.fields.append(device_latitude_schema)
	
	device_longitude_schema = bigquery.TableFieldSchema()
	device_longitude_schema.name = 'device_longitude'
	device_longitude_schema.type = 'string'
	device_longitude_schema.mode = 'nullable'
	device_longitude_schema.description = 'Longitude of the device'
	table_schema.fields.append(device_longitude_schema)
	
	device_battery_level_schema = bigquery.TableFieldSchema()
	device_battery_level_schema.name = 'device_battery_level'
	device_battery_level_schema.type = 'string'
	device_battery_level_schema.mode = 'nullable'
	device_battery_level_schema.description = 'Battery level of the device'
	table_schema.fields.append(device_battery_level_schema)
	
	device_last_transmission_schema = bigquery.TableFieldSchema()
	device_last_transmission_schema.name = 'device_last_transmission'
	device_last_transmission_schema.type = 'timestamp'
	device_last_transmission_schema.mode = 'nullable'
	device_last_transmission_schema.description = 'Timestamp when the device last transmits (vote, battery level, ...)'
	table_schema.fields.append(device_last_transmission_schema)
	
	device_last_data_transmission_schema = bigquery.TableFieldSchema()
	device_last_data_transmission_schema.name = 'device_last_data_transmission'
	device_last_data_transmission_schema.type = 'timestamp'
	device_last_data_transmission_schema.mode = 'nullable'
	device_last_data_transmission_schema.description = 'Timestamp when the device last transmits votes'
	table_schema.fields.append(device_last_data_transmission_schema)
	
	device_keyboard_id_schema = bigquery.TableFieldSchema()
	device_keyboard_id_schema.name = 'device_keyboard_id'
	device_keyboard_id_schema.type = 'integer'
	device_keyboard_id_schema.mode = 'nullable' # should be REQUIDRED
	device_keyboard_id_schema.description = 'ID of the keyboard'
	table_schema.fields.append(device_keyboard_id_schema)
	
	device_keyboard_name_schema = bigquery.TableFieldSchema()
	device_keyboard_name_schema.name = 'device_keyboard_name'
	device_keyboard_name_schema.type = 'string'
	device_keyboard_name_schema.mode = 'nullable'
	device_keyboard_name_schema.description = 'Name of the keyboard'
	table_schema.fields.append(device_keyboard_name_schema)
	
	device_keyboard_type_schema = bigquery.TableFieldSchema()
	device_keyboard_type_schema.name = 'device_keyboard_type'
	device_keyboard_type_schema.type = 'integer'
	device_keyboard_type_schema.mode = 'nullable'
	device_keyboard_type_schema.description = 'Type of keyboard'
	table_schema.fields.append(device_keyboard_type_schema)

	group_id_schema = bigquery.TableFieldSchema()
	group_id_schema.name = 'group_id'
	group_id_schema.type = 'integer'
	group_id_schema.mode = 'nullable' # should be REQUIRED
	group_id_schema.description = 'ID of the group'
	table_schema.fields.append(group_id_schema)
	
	group_name_schema = bigquery.TableFieldSchema()
	group_name_schema.name = 'group_name'
	group_name_schema.type = 'string'
	group_name_schema.mode = 'nullable'
	group_name_schema.description = 'Name of the group'
	table_schema.fields.append(group_name_schema)
	
	group_description_schema = bigquery.TableFieldSchema()
	group_description_schema.name = 'group_description'
	group_description_schema.type = 'string'
	group_description_schema.mode = 'nullable'
	group_description_schema.description = 'Description of the group'
	table_schema.fields.append(group_description_schema)
	
	entity_id_schema = bigquery.TableFieldSchema()
	entity_id_schema.name = 'entity_id'
	entity_id_schema.type = 'integer'
	entity_id_schema.mode = 'required'
	entity_id_schema.description = 'ID of the entity'
	table_schema.fields.append(entity_id_schema)
	
	entity_name_schema = bigquery.TableFieldSchema()
	entity_name_schema.name = 'entity_name'
	entity_name_schema.type = 'string'
	entity_name_schema.mode = 'nullable'
	entity_name_schema.description = 'Name of the entity'
	table_schema.fields.append(entity_name_schema)
	
	entity_description_schema = bigquery.TableFieldSchema()
	entity_description_schema.name = 'entity_description'
	entity_description_schema.type = 'string'
	entity_description_schema.mode = 'nullable'
	entity_description_schema.description = 'Description of the entity'
	table_schema.fields.append(entity_description_schema)
	
	entity_timezone_schema = bigquery.TableFieldSchema()
	entity_timezone_schema.name = 'entity_timezone'
	entity_timezone_schema.type = 'string'
	entity_timezone_schema.mode = 'required'
	entity_timezone_schema.description = 'Timezone of the entity'
	table_schema.fields.append(entity_timezone_schema)
		
	question_id_schema = bigquery.TableFieldSchema()
	question_id_schema.name = 'question_id'
	question_id_schema.type = 'integer'
	question_id_schema.mode = 'required'
	question_id_schema.description = 'ID of the question'
	table_schema.fields.append(question_id_schema)
	
	question_label_schema = bigquery.TableFieldSchema()
	question_label_schema.name = 'question_label'
	question_label_schema.type = 'string'
	question_label_schema.mode = 'required'
	question_label_schema.description = 'Label of the question'
	table_schema.fields.append(question_label_schema)
	
	return table_schema


def getDWHSchema_swipeDatamart():
	from apache_beam.io.gcp.internal.clients import bigquery
	table_schema = bigquery.TableSchema()

	# Fields that use standard types.	
	swipe_id_schema = bigquery.TableFieldSchema()
	swipe_id_schema.name = 'swipe_id'
	swipe_id_schema.type = 'integer'
	swipe_id_schema.mode = 'required'
	swipe_id_schema.description = 'ID of the data associated in so_timesheet'
	table_schema.fields.append(swipe_id_schema)
	
	swipe_timestamp_schema = bigquery.TableFieldSchema()
	swipe_timestamp_schema.name = 'swipe_timestamp'
	swipe_timestamp_schema.type = 'timestamp'
	swipe_timestamp_schema.mode = 'required'
	swipe_timestamp_schema.description = 'Timestamp when was recorded the swipe'
	table_schema.fields.append(swipe_timestamp_schema)
	
	device_skiply_id_schema = bigquery.TableFieldSchema()
	device_skiply_id_schema.name = 'device_skiply_id'
	device_skiply_id_schema.type = 'string'
	device_skiply_id_schema.mode = 'required'
	device_skiply_id_schema.description = 'ID given by Skiply to the concerned device'
	table_schema.fields.append(device_skiply_id_schema)
	
	device_id_schema = bigquery.TableFieldSchema()
	device_id_schema.name = 'device_id'
	device_id_schema.type = 'string'
	device_id_schema.mode = 'nullable'
	device_id_schema.description = 'ID of the hardware for the concerned device'
	table_schema.fields.append(device_id_schema)
	
	device_description_schema = bigquery.TableFieldSchema()
	device_description_schema.name = 'device_description'
	device_description_schema.type = 'string'
	device_description_schema.mode = 'nullable'
	device_description_schema.description = 'Description of the device'
	table_schema.fields.append(device_description_schema)
	
	device_latitude_schema = bigquery.TableFieldSchema()
	device_latitude_schema.name = 'device_latitude'
	device_latitude_schema.type = 'string'
	device_latitude_schema.mode = 'nullable'
	device_latitude_schema.description = 'Latitude of the device'
	table_schema.fields.append(device_latitude_schema)
	
	device_longitude_schema = bigquery.TableFieldSchema()
	device_longitude_schema.name = 'device_longitude'
	device_longitude_schema.type = 'string'
	device_longitude_schema.mode = 'nullable'
	device_longitude_schema.description = 'Longitude of the device'
	table_schema.fields.append(device_longitude_schema)
	
	device_battery_level_schema = bigquery.TableFieldSchema()
	device_battery_level_schema.name = 'device_battery_level'
	device_battery_level_schema.type = 'string'
	device_battery_level_schema.mode = 'nullable'
	device_battery_level_schema.description = 'Battery level of the device'
	table_schema.fields.append(device_battery_level_schema)
	
	device_last_transmission_schema = bigquery.TableFieldSchema()
	device_last_transmission_schema.name = 'device_last_transmission'
	device_last_transmission_schema.type = 'timestamp'
	device_last_transmission_schema.mode = 'nullable'
	device_last_transmission_schema.description = 'Timestamp when the device last transmits (vote, battery level, ...)'
	table_schema.fields.append(device_last_transmission_schema)
	
	device_last_data_transmission_schema = bigquery.TableFieldSchema()
	device_last_data_transmission_schema.name = 'device_last_data_transmission'
	device_last_data_transmission_schema.type = 'timestamp'
	device_last_data_transmission_schema.mode = 'nullable'
	device_last_data_transmission_schema.description = 'Timestamp when the device last transmits votes'
	table_schema.fields.append(device_last_data_transmission_schema)
	
	device_keyboard_id_schema = bigquery.TableFieldSchema()
	device_keyboard_id_schema.name = 'device_keyboard_id'
	device_keyboard_id_schema.type = 'integer'
	device_keyboard_id_schema.mode = 'nullable' # should be REQUIDRED
	device_keyboard_id_schema.description = 'ID of the keyboard'
	table_schema.fields.append(device_keyboard_id_schema)
	
	device_keyboard_name_schema = bigquery.TableFieldSchema()
	device_keyboard_name_schema.name = 'device_keyboard_name'
	device_keyboard_name_schema.type = 'string'
	device_keyboard_name_schema.mode = 'nullable'
	device_keyboard_name_schema.description = 'Name of the keyboard'
	table_schema.fields.append(device_keyboard_name_schema)
	
	device_keyboard_type_schema = bigquery.TableFieldSchema()
	device_keyboard_type_schema.name = 'device_keyboard_type'
	device_keyboard_type_schema.type = 'integer'
	device_keyboard_type_schema.mode = 'nullable'
	device_keyboard_type_schema.description = 'Type of keyboard'
	table_schema.fields.append(device_keyboard_type_schema)

	group_id_schema = bigquery.TableFieldSchema()
	group_id_schema.name = 'group_id'
	group_id_schema.type = 'integer'
	group_id_schema.mode = 'nullable' # should be REQUIRED
	group_id_schema.description = 'ID of the group'
	table_schema.fields.append(group_id_schema)
	
	group_name_schema = bigquery.TableFieldSchema()
	group_name_schema.name = 'group_name'
	group_name_schema.type = 'string'
	group_name_schema.mode = 'nullable'
	group_name_schema.description = 'Name of the group'
	table_schema.fields.append(group_name_schema)
	
	group_description_schema = bigquery.TableFieldSchema()
	group_description_schema.name = 'group_description'
	group_description_schema.type = 'string'
	group_description_schema.mode = 'nullable'
	group_description_schema.description = 'Description of the group'
	table_schema.fields.append(group_description_schema)
	
	entity_id_schema = bigquery.TableFieldSchema()
	entity_id_schema.name = 'entity_id'
	entity_id_schema.type = 'integer'
	entity_id_schema.mode = 'required'
	entity_id_schema.description = 'ID of the entity'
	table_schema.fields.append(entity_id_schema)
	
	entity_name_schema = bigquery.TableFieldSchema()
	entity_name_schema.name = 'entity_name'
	entity_name_schema.type = 'string'
	entity_name_schema.mode = 'nullable'
	entity_name_schema.description = 'Name of the entity'
	table_schema.fields.append(entity_name_schema)
	
	entity_description_schema = bigquery.TableFieldSchema()
	entity_description_schema.name = 'entity_description'
	entity_description_schema.type = 'string'
	entity_description_schema.mode = 'nullable'
	entity_description_schema.description = 'Description of the entity'
	table_schema.fields.append(entity_description_schema)
	
	entity_timezone_schema = bigquery.TableFieldSchema()
	entity_timezone_schema.name = 'entity_timezone'
	entity_timezone_schema.type = 'string'
	entity_timezone_schema.mode = 'required'
	entity_timezone_schema.description = 'Timezone of the entity'
	table_schema.fields.append(entity_timezone_schema)
		
	question_id_schema = bigquery.TableFieldSchema()
	question_id_schema.name = 'question_id'
	question_id_schema.type = 'integer'
	question_id_schema.mode = 'required'
	question_id_schema.description = 'ID of the question'
	table_schema.fields.append(question_id_schema)
	
	question_label_schema = bigquery.TableFieldSchema()
	question_label_schema.name = 'question_label'
	question_label_schema.type = 'string'
	question_label_schema.mode = 'required'
	question_label_schema.description = 'Label of the question'
	table_schema.fields.append(question_label_schema)

	# notif_id ?

	return table_schema