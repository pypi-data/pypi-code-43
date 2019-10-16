from activity.models import Process
from activity.models import Activity


def _save_process(process_key, internal_key, process_type, status):
    process, created = Process.objects.update_or_create(
        internal_key=internal_key,
        process_type_slug=process_type,
        defaults={'status': status, 'process_key': process_key},
    )
    return process


def _save_activity(process_key, activity_id, from_template_activity_slug):
    process = Process.objects.get(process_key=process_key)

    activity, created = Activity.objects.update_or_create(
        activity_id=activity_id,
        process=process,
        from_template_activity_slug=from_template_activity_slug,
    )
    return activity


def _delete_activity(activity_id):
    activity = Activity.objects.get(activity_id=activity_id)
    activity.delete()
    return activity


class BaseWebhookService(object):
    """
    Ronan webhook service.
    Ronan consumer will be notified if any one of these happened on ronan:
    - An process is created
    - An process is updated
    - An activity is created
    - An activity is updated
    - An activity is deleted
    - An activity is completed
    - A submission of an activity is submitted
    - A reminder for activities being sent
    The webhook will be hit if the activity is under a process which has process_type of this service as consumer
    Depending on the event, consumer service may return some value on the request to be processed by ronan.
    """

    def on_process_created(self, process_data):
        """
        Invoked when an process is created.
        You may override this method to react on an process created.
        You may return these data as dict, so Ronan will react to them:
        - TBD
        :param process_data: ronan activity that has been created
        :return: dictionary as specified on description
        """
        _save_process(
            process_data.get('process_key'),
            process_data.get('external_key'),
            process_data.get('process_type'),
            process_data.get('status'),
        )
        return {}

    def on_process_updated(self, process_data):
        """
        Invoked when an process is updated.
        You may override this method to react on an process created.
        You may return these data as dict, so Ronan will react to them:
        - TBD
        :param activity_data: ronan activity that has been created
        :return: dictionary as specified on description
        """
        _save_process(
            process_data.get('process_key'),
            process_data.get('external_key'),
            process_data.get('process_type'),
            process_data.get('status'),
        )
        return {}

    def on_activity_created(self, activity_data):
        """
        Invoked when an activity is created.
        You may override this method to react on an activity created.
        You may return these data as dict, so Ronan will react to them:
        - responsible_user_ids: responsible user id that will be added
        - accountable_user_id: accountable user id
        :param activity_data: ronan activity that has been created
        :return: dictionary as specified on description
        """
        from_template_activity = activity_data.get('from_template_activity')
        from_template_activity_slug = None

        if from_template_activity is not None:
            from_template_activity_slug = from_template_activity.get('slug')

        _save_activity(
            activity_data.get('process').get('process_key'),
            activity_data.get('id'),
            from_template_activity_slug,
        )
        return {}

    def on_activity_updated(self, activity_data):
        """
        Invoked when an activity is updated.
        You may override this method to react on an activity updated.
        :param activity_data: ronan activity that has been updated
        :return: empty dictionary
        """
        return {}

    def on_activity_completed(self, activity_data):
        """
        Invoked when an activity is completed.
        You may override this method to react on an activity completed.
        :param activity_data: ronan activity that has been completed
        :return: empty dictionary
        """
        return {}

    def on_activity_deleted(self, activity_data):
        """
        Invoked when an activity is deleted.
        You may override this method to react on an activity deleted.
        :param activity_data: ronan activity that has been deleted
        :return: empty dictionary
        """
        _delete_activity(activity_data.get('id'))
        return {}

    def on_activity_submission_submitted(self, activity_submission_data, activity_data):
        """
        Invoked when an activity submission is submitted.
        You may override this method to react on an activity submission submitted.
        :param activity_submission_data: ronan activity submission that have been submitted
        :param activity_data: ronan activity that contains the submission
        :return: empty dictionary
        """
        return {}

    def on_activities_reminder_sent(self, activities_by_remaining_days):
        """
        Invoked when an activities reminder is sent.
        You may override this method to react on an activities reminder sent.
        :param activities_by_remaining_days: ronan activities that have reminder configured for current day,
               grouped by remaining days
        :return: empty dictionary
        """
        return {}

    def on_internal_server_error(self, error, request_data):
        """
        Invoked when internal server error occur.
        You may want to log this error.
        """
        pass

    def on_value_error(self, error):
        """
        Invoked when value error occur.
        You may want to log this error.
        """
        pass
