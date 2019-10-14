import json
import logging

from activity.api import ActivityAPI

logger = logging.getLogger('Activity API Client')


# Activity API Client Python Interface #
class ActivityAPIClient(object):
    """
    Interface for interact with Ronan activity service
    """
    ALL = 'All'
    RESTRICTED = 'Restricted'

    def __init__(self):
        self.api = ActivityAPI()

    def create_process(self, process_type, external_key, status, additional_data={}):
        """
        Create process to Ronan activity service and
        return response's content. Raise ClientError when request is failed.
        :param process_type: string process_type that defined in Ronan
        :param external_key: string to identify process from consumer service (example: Project ID)
        :param status: enum(['On Hold', 'On Progress', 'Completed', 'Cancelled'])
        :param additional_data: dict()
        :return: dict
        {
            "processType": "...",
            "externalKey": "...",
            "status": "...",
            "additionalData": "..."
        }
        """
        uri = '/processes'
        data = {
            'processType': process_type,
            'externalKey': external_key,
            'status': status,
            'additionalData': json.dumps(additional_data)
        }
        return self.api.post(uri, data=data)

    def update_process(self, process_key, **kwargs):
        """
        Update process to Ronan activity service and
        return response's content. Raise ClientError when request is failed.
        :param process_type: string process_type that defined in Ronan
        :param external_key: string to identify process from consumer service (example: Project ID)
        :param status: enum(['On Hold', 'On Progress', 'Completed', 'Cancelled'])
        :return: dict
        {
            "processType": "...",
            "externalKey": "...",
            "status": "..."
        }
        """
        process_type = kwargs.get('process_type', None)
        external_key = kwargs.get('external_key', None)
        status = kwargs.get('status', None)
        additional_data = json.dumps(kwargs.get('additional_data', None))

        data = {}
        if process_type:
            data['processType'] = process_type
        if external_key:
            data['externalKey'] = external_key
        if status:
            data['status'] = status
        if additional_data:
            data['additionalData'] = additional_data

        uri = '/processes/%s' % str(process_key)
        return self.api.patch(uri, data=data)

    def create_activity(self, process_key, template_slug, additional_data=None,
                        **activity_data):
        """
        Create activity based on template activity slug given.
        Return response's content. Raise ClientError when request is failed.
        :param process_key: string to identify process that running in Ronan. You have to create Process first
                            before start and activity.
        :param template_slug: string slug based on template name to identify the template (example: TEMPLATE_NAME_SLUG).
        :param additional_data: dict contains optional data that you want to carry.
        :param activity_data: dict contains optional activity data.
                              You may want to override the default value of the template.
        :return: dict
        """
        uri = '/processes/%s/activities' % process_key
        data = activity_data.copy()
        data.update({
            'fromTemplateActivity': template_slug,
        })

        if additional_data is not None:
            data['additionalData'] = json.dumps(additional_data)

        return self.api.post(uri, data=data)

    def update_activity(self, process_key, activity_id, **activity_data):
        """
        Update activity. Return response's content. Raise ClientError when request is failed.
        :param process_key: string to identify process that running in Ronan. You have to create Process first
                            before start and activity.
        :param activity_id: int to identify the activity
        :param activity_data: dict
        :return: dict
        """
        uri = '/processes/%s/activities/%s' % (process_key, activity_id)
        return self.api.patch(uri, data=activity_data)

    def delete_activity(self, process_key, activity_id):
        """
        Delete activity. Return response's content. Raise ClientError when request is failed.
        :param process_key: string to identify process that running in Ronan. You have to create Process first
                            before start and activity.
        :param activity_id: int to identify the activity
        :param activity_data: dict
        :return: dict
        """
        uri = '/processes/%s/activities/%s' % (process_key, activity_id)
        return self.api.delete(uri)

    def retrieve_template_activity(self, template_slug):
        """
        Retreive template activity and return response's content.
        Raise ClientError when request is failed.
        :param template_slug: string slug based on template name to identify the template (example: TEMPLATE_NAME_SLUG)
        :return: dict
        """
        uri = '/template-activities/%s' % template_slug
        return self.api.get(uri)

    def retrieve_process_list(self):
        """
        Retrieve list of process and return response's content.
        Raise ClientError when request is failed
        :return: dict
        """
        uri = '/processes'
        return self.api.get(uri)

    def retrieve_process_activity_list(self, process_key, access_level):
        """
        Retrieve list of process and return response's content.
        Raise ClientError when request is failed
        :return: dict
        """
        uri = '/processes/%s/activities?access_level=%s' % (
            process_key, access_level)
        return self.api.get(uri)

    def retrieve_activity_list(self, activity_ids):
        """
        Retrieve list of activity with id included in activity_ids and return response's content.
        Raise ClientError when request is failed
        :return: dict
        """
        activity_ids_params = '&'.join(
            ['activityIds=%d' % id for id in activity_ids]
        )
        uri = '/activities?%s' % (activity_ids_params)
        return self.api.get(uri)
