from .base import BaseActionMixin
from rest_framework import decorators, response
import json

class ActionMixin(BaseActionMixin):
    '''
    Bulk actions:
    POST /resource/action/:action_id/
    Instance actions:
    POST /resource/:pk/action/:action_id/

    ## View docs:

    Bulk actions:
    GET /resource/action/:action_id/
    Instance actions:
    GET /resource/:pk/action/:action_id/
    '''

    @decorators.action(
        detail=False,
        methods=['get'],
        url_path='actions/list'
    )
    def action_docs(self, request, action_id=None):
        reg = json.loads(json.dumps(self.action_registry))

        all_actions = reg.pop('actions')
        reg.update({
            "bulk_actions": [],
            "instance_actions": []
        })
        for action_id, action_defn in all_actions.items():
            action_defn['id'] = action_id
            if (action_defn.get('type') == 'bulk'):
                action_defn['url'] = '{}/{}/'.format(reg.get('basepath'), action_id)
                reg['bulk_actions'].append(action_defn)
            else:
                action_defn['url'] = '{}:pk/{}/'.format(reg.get('basepath'), action_id)
                reg['instance_actions'].append(action_defn)

        return response.Response(reg)

    @decorators.action(
        detail=False,
        methods=['get', 'post'],
        url_path='actions/(?P<action_id>[^/.]+)'
    )
    def bulk_actions(self, request, action_id=None):
        return self._action(request, action_id=action_id, pk=None)

    @decorators.action(
        detail=True,
        methods=['get','post'],
        url_path='actions/(?P<action_id>[^/.]+)'
    )
    def actions(self, request, pk=None, action_id=None):
        return self._action(request, pk, action_id)