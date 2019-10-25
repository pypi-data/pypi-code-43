import json
import re


class Planner(object):

    def __init__(self, api_client):
        self.api_client = api_client

    def set_template(self, template):
        self.wflowns = self.api_client.get_export_url() + "workflows/" + template + ".owl#"
        self.wflowid = self.wflowns + template

    def _set_bindings(self, invar, val, data_bindings, parameter_bindings, parameter_types):
        if isinstance(val, basestring) and val.startswith('file:'):
            data = data_bindings.get(self.wflowns + invar, [])
            data.append(self.api_client.libns + val[5:])
            data_bindings[self.wflowns + invar] = data
        else:
            parameter_bindings[self.wflowns + invar] = val
            typeid = self.api_client.xsdns + "string"
            if type(val) is int:
                typeid = self.api_client.xsdns + "integer"
            elif type(val) is float:
                typeid = self.api_client.xsdns + "float"
            elif type(val) is bool:
                typeid = self.api_client.xsdns + "boolean"
            parameter_types[self.wflowns + invar] = typeid

    def get_expansions(self, inputs):
        postdata = [('templateId', self.wflowid),
                    ('componentBindings', '{}'), ('parameterBindings', '{}')]
        data_bindings = dict()
        parameter_bindings = dict()
        parameter_types = dict()
        for invar in inputs:
            if type(inputs[invar]) is list:
                for val in inputs[invar]:
                    self._set_bindings(
                        invar, val, data_bindings, parameter_bindings, parameter_types)
            else:
                self._set_bindings(
                    invar, inputs[invar], data_bindings, parameter_bindings, parameter_types)
        postdata = {
            "templateId": self.wflowid,
            "dataBindings": data_bindings,
            "parameterBindings": parameter_bindings,
            "parameter_types": parameter_types,
            "componentBindings": dict()
        }
        resp = self.api_client.session.post(
            self.api_client.get_request_url() + 'plan/getExpansions', json=postdata)
        return resp.json()

    def select_template(self, templates):
        from sys import version_info
        py3 = version_info[0] > 2

        i = 1
        num = len(templates)
        for tpl in templates:
            print("%s. %s" %
                  (i, self.api_client.get_template_description(tpl['template'])))
            i += 1
        index = 0
        while True:
            if py3:
                index = int(input("Please enter your selection: "))
            else:
                index = int(raw_input("Please enter your selection: "))
            if index < 1 or index > num:
                print("Invalid Selection. Try again")
            else:
                break
        return templates[index - 1]

    def get_template_description(self, template):
        regex = re.compile(r"^.*#")
        components = {}
        for nodeid in template['Nodes']:
            node = template['Nodes'][nodeid]
            comp = regex.sub("", node['componentVariable']['binding']['id'])
            if comp in components:
                components[comp] += 1
            else:
                components[comp] = 1

        description = regex.sub("", template['id']) + " ( "
        i = 0
        for comp in components:
            if i > 0:
                description += ", "
            description += str(components[comp]) + " " + comp
            i += 1
        description += " )"
        return description

    def run_workflow(self, template, seed):
        postdata = {
            'template_id': seed["template"]["id"],
            'json': json.dumps(template["template"]),
            'constraints_json': json.dumps(template["constraints"]),
            'seed_json': json.dumps(seed["template"]),
            'seed_constraints_json': json.dumps(seed["constraints"])
        }
        resp = self.api_client.session.post(self.api_client.get_request_url(
        ) + 'executions/runWorkflow', data=postdata)
        regex = re.compile(r"^.*#")
        return regex.sub("", resp.text)
