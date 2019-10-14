from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from activity.constants import K_TRIGGER_PROCESS_ON_CREATE
from activity.constants import K_TRIGGER_PROCESS_ON_UPDATE
from activity.constants import K_TRIGGER_ACTIVITY_ON_COMPLETE
from activity.constants import K_TRIGGER_ACTIVITY_ON_CREATE
from activity.constants import K_TRIGGER_ACTIVITY_ON_UPDATE
from activity.constants import K_TRIGGER_ACTIVITY_ON_DELETE
from activity.constants import K_TRIGGER_ACTIVITY_SUBMISSION_ON_SUBMIT
from activity.constants import K_TRIGGER_ACTIVITIES_REMINDER_ON_SEND
from activity.services import BaseWebhookService


class BaseWebhookView(APIView):
    webhook_service = None

    def get_webhook_service(self):
        if self.webhook_service is None:
            raise NotImplementedError('No webhook service')
        if not issubclass(type(self.webhook_service), BaseWebhookService):
            raise ValueError(
                'Webhook service not inherit from BaseWebhookService')
        return self.webhook_service

    def perform_on_process_created(self, request):
        return self.get_webhook_service() \
            .on_process_created(request.data['process'])

    def perform_on_process_updated(self, request):
        return self.get_webhook_service() \
            .on_process_updated(request.data['process'])

    def perform_on_activity_completed(self, request):
        return self.get_webhook_service() \
            .on_activity_completed(request.data['activity'])

    def perform_on_activity_created(self, request):
        return self.get_webhook_service() \
            .on_activity_created(request.data['activity'])

    def perform_on_activity_updated(self, request):
        return self.get_webhook_service() \
            .on_activity_updated(request.data['activity'])

    def perform_on_deleted(self, request):
        return self.get_webhook_service() \
            .on_activity_deleted(request.data['activity'])

    def perform_on_submission_submitted(self, request):
        return self.get_webhook_service() \
            .on_activity_submission_submitted(
            request.data['activity_submission'], request.data['activity'])

    def perform_on_activities_reminder_sent(self, request):
        return self.get_webhook_service() \
            .on_activities_reminder_sent(
            request.data['activities_by_remaining_days'])

    def perform_on_value_error(self, error):
        return self.get_webhook_service() \
            .on_value_error(error)

    def perform_on_internal_server_error(self, error, request_data):
        return self.get_webhook_service() \
            .on_internal_server_error(error, request_data)

    def validate_trigger_type(self, request):
        if 'trigger_type' not in request.data:
            raise ValueError({'trigger_type': 'missing trigger_type'})
        return request.data['trigger_type']

    def post(self, request, *args, **kwargs):
        try:
            trigger_type = self.validate_trigger_type(request)

            if trigger_type == K_TRIGGER_PROCESS_ON_CREATE:
                res = self.perform_on_process_created(request)
            elif trigger_type == K_TRIGGER_PROCESS_ON_UPDATE:
                res = self.perform_on_process_updated(request)
            elif trigger_type == K_TRIGGER_ACTIVITY_ON_COMPLETE:
                res = self.perform_on_activity_completed(request)
            elif trigger_type == K_TRIGGER_ACTIVITY_ON_CREATE:
                res = self.perform_on_activity_created(request)
            elif trigger_type == K_TRIGGER_ACTIVITY_ON_UPDATE:
                res = self.perform_on_activity_updated(request)
            elif trigger_type == K_TRIGGER_ACTIVITY_ON_DELETE:
                res = self.perform_on_deleted(request)
            elif trigger_type == K_TRIGGER_ACTIVITY_SUBMISSION_ON_SUBMIT:
                res = self.perform_on_submission_submitted(request)
            elif trigger_type == K_TRIGGER_ACTIVITIES_REMINDER_ON_SEND:
                res = self.perform_on_activities_reminder_sent(request)
            else:
                raise ValueError({'trigger_type': 'invalid trigger_type'})
            return Response(res, status.HTTP_200_OK)
        except ValueError as e:
            self.perform_on_value_error(e)
            return Response(e, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.perform_on_internal_server_error(e, request.data)
            return Response({'msg': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
