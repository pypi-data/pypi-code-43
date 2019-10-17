from django.http import Http404
from django.utils.module_loading import import_string
from rest_framework import response
import json

class BaseActionMixin():
    '''
    ## Perform Action (POST)
    Bulk actions:
    POST /resource/action/:action_id/
    Instance actions:
    POST /resource/:pk/action/:action_id/

    ## Docs: (GET)
    Bulk actions:
    GET /resource/action/:action_id/
    Instance actions:
    GET /resource/:pk/action/:action_id/
    '''
    def __get_form(self, definition, request, pk = None, instance = None):
        form_path = definition.get('form')
        form = import_string(form_path)
        has_custom_getter = getattr(form, 'get_form', None) is not None

        if has_custom_getter:
            return form.get_form(
                self,
                request,
                pk,
                instance = instance
            )
        else:
            return form(request.data)

    def __docs_result(self, request, pk=None, action_id=None):
        is_bulk_action = (pk is None)
        if action_id is None:
            data = self.action_registry
        else:
            data = self.__get_action_definition(action_id, is_bulk_action)
            if data is None:
                available_actions = [key for key, value in self.action_registry.get('actions',{}).items()]
                raise Exception('No action registered with name: {}. Available actions are: '.format(action_id, available_actions))

            if pk is not None:
                url = "{}{}/actions/{}/".format(
                    self.action_registry.get("basepath"),
                    pk,
                    action_id
                )
            else:
                url = "{}/actions/{}/".format(
                    self.action_registry.get("basepath"),
                    action_id
                )

            form = import_string(data.get('form'))()
            fields = []
            for key, value in form.fields.items():
                fields.append({
                    "name": key,
                    "required": value.required,
                    "description": value.help_text,
                    "type": value.__class__.__name__
                })

            serializer = import_string(data.get('serializer'))

            data.update({
                "url": url,
                "fields": fields,
                "example_response": [serializer().data]
            })
        return response.Response(data)

    def __get_action_definition(self, action_id, is_bulk_action):
        data = self.action_registry.get('actions', {}).get(action_id)
        if is_bulk_action:
            assert data.get('type') == 'bulk', 'No bulk action with that action_id. Try instance action'
        else:
            assert data.get('type') == 'instance', 'No instance action with that action_id. Try bulk action'
        return data

    def _docs(self):
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

    def _action(self, request, pk=None, action_id=None):
        is_bulk_action = (pk is None)
        action_config = self.__get_action_definition(action_id, is_bulk_action)
        if request.method == 'GET':
            return self.__docs_result(request, pk, action_id)
        if action_config is None:
            raise Http404('No action configuration exists for this action_id')

        # handle POST:
        form = None

        if is_bulk_action:
            form = self.__get_form(action_config, request, pk=None, instance=None)
        else:
            instance = self.get_object()
            form = self.__get_form(action_config, request, pk=pk, instance=instance)

        if form.is_valid():
            meta, result = form.save(request, pk)

            serializer_class = action_config.get('serializer')
            has_multiple_results = action_config.get('multiple_results', is_bulk_action)
            if serializer_class:
                result = import_string(serializer_class)(
                    result,
                    many=has_multiple_results,
                    context={'request': request}
                ).data

            if has_multiple_results:
                http_result = {
                    "meta": meta,
                    "results": result
                }
                return response.Response(http_result)
            else:
                result.update(meta)
                return response.Response(result)
        else:
            return response.Response(form.errors, status=400)
