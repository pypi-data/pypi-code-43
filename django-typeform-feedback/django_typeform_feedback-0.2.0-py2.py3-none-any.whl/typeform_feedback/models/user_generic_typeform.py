# -*- coding: utf-8 -*-
import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel

from ..conf import settings
from ..signals_define import (
    new_user_typeform_response,
    user_response_approved,
)


class UserGenericTypeformFeedback(TimeStampedModel):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.CASCADE,
    )
    feedback = models.ForeignKey(
        'GenericTypeformFeedback',
        related_name='responses',
        on_delete=models.CASCADE,
    )
    _response = JSONField(
        default=list,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=1,
        choices=settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_CHOICES,
        default=settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_DEFAULT,
    )

    def __str__(self):
        return '{} - {}'.format(
            self.user, self.feedback,
        )

    @property
    def url(self):
        return self.feedback.url

    @property
    def response(self):
        return self.first_response

    @property
    def responses(self):
        return self._response

    @property
    def first_response(self):
        return self._response[0] if len(self._response) > 0 else {}

    @property
    def last_response(self):
        return self._response[-1] if len(self._response) > 0 else {}

    def parse_response(self, response):
        question_parsed = {
            'id': '',
            'title': '',
            'type': '',
            'responses': [],
            'options': [],
        }
        parsed_response = []

        form_body = response.get(settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_FORM_RESPONSE)
        questions_definition = form_body.get(settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_QUESTIONS_DEFINITION)
        questions = questions_definition.get(settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_QUESTIONS)
        answers = {
            _.get('field').get('id'): _
            for _ in form_body.get(settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_ANSWERS)
        }

        for question in questions:
            new_question = question_parsed.copy()
            new_question['id'] = question.get('id')
            new_question['title'] = question.get('title')
            new_question['type'] = question.get('type')

            if question.get('type') in settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_QUESTION_TYPE_CHOICE:
                new_question['options'] = [_.get('label') for _ in question.get('choices')]

            answer = answers.get(question.get('id'), {})
            if answer.get('type') == 'choices':
                new_question['responses'] = answer.get('choices').get('labels')

            elif answer.get('type') == 'choice':
                new_question['responses'] = [answer.get('choice').get('label')]

            else:
                new_question['responses'] = ['{}'.format(answer.get(answer.get('type')))]

            parsed_response.append(new_question)

        return parsed_response

    def set_typeform_response(self, response):
        self._response.append(response)
        self.save(update_fields=['_response', 'modified'])

        status_to_notify = [
            settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_PENDING,
            settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_FAIL,
        ]
        should_be_notified = self.status in status_to_notify

        if self.status != settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_DONE:
            self.status = settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_ANSWERED
            self.save(update_fields=['status'])

        if should_be_notified or settings.TYPEFORM_FEEDBACK_NOTIFICATE_ALL_USER_RESPONSES:
            new_user_typeform_response.send(
                sender=self,
                uuid=self.uuid.__str__(),
                response=self.parse_response(response)
            )

    def mark_as_approved(self):
        self.status = settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_DONE
        self.save(update_fields=['status', 'modified'])
        user_response_approved.send(
            sender=self,
            uuid=self.uuid.__str__(),
        )

    def mark_as_fail(self):
        self.status = settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_FAIL
        self.save(update_fields=['status', 'modified'])
