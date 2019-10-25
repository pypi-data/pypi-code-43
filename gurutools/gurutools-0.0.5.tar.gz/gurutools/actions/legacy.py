"""
for versions of DRF prior to 3.10:
https://www.django-rest-framework.org/community/3.8-announcement/#deprecations
"""
from .base import BaseActionMixin
from rest_framework import decorators, response
import json

class ActionMixin(BaseActionMixin):
    @decorators.list_route(
        methods=['get'],
        url_path='actions/list'
    )
    def action_docs(self, request, action_id=None):
        return self._docs()

    @decorators.list_route(
        methods=['get', 'post'],
        url_path='actions/(?P<action_id>[^/.]+)'
    )
    def bulk_actions(self, request, action_id=None):
        return self._action(request, action_id=action_id, pk=None)

    @decorators.detail_route(
        methods=['get','post'],
        url_path='actions/(?P<action_id>[^/.]+)'
    )
    def actions(self, request, pk=None, action_id=None):
        return self._action(request, pk, action_id)
