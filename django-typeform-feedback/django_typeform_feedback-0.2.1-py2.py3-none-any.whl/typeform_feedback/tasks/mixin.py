import logging

from django.conf import settings


class TypeformWebhookMixin:

    def _get_form_response(self, response):
        return response.get(settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_FORM_RESPONSE)

    def _get_form_id(self, response):
        return response.get(settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_FORM_ID)

    def _get_hidden(self, response):
        return response.get(
            settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_HIDDEN,
            {}
        )

    def get_logger(self):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger('typeform')
        return self.logger

    def set_info(self, message):
        self.get_logger().info(message)

    def set_error(self, message):
        self.get_logger().error(message)
