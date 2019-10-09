#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#

import json
from copy import deepcopy


class AAPluginTester:
    def __init__(self, plugin_cls, plugin_configuration, parameters):
        self.plugin_cls = plugin_cls
        self.plugin_configuration = plugin_configuration
        self.parameters = parameters

    @classmethod
    def run_rdp_authenticate(cls, plugin_cls, plugin_configuration, target_username=None,
                             gateway_username=None):
        tester = cls(
            plugin_cls,
            plugin_configuration,
            {
                'cookie': {},
                'session_cookie': {},
                'session_id': 'example-1',
                'protocol': 'rdp',
                'connection_name': 'example',
                'client_ip': '1.2.3.4',
                'client_port': 14124,
                'gateway_user': gateway_username if gateway_username else 'wsmith',
                'target_username': target_username if target_username else 'target_wsmith',
                'key_value_pairs': {},
            }
        )
        return tester.execute_authenticate()

    def execute_authenticate(self):
        preamble = "plugin authenticate "
        while True:
            verdict = self.plugin_cls(self.plugin_configuration).authenticate(**deepcopy(self.parameters))
            assert verdict is not None, "{} should return a value".format(preamble)
            assert isinstance(verdict, dict), "{} should return a dict".format(preamble)
            assert json.dumps(verdict) is not None, "{} result must be possible to encode into JSON".format(preamble)

            # convert to what SPS sees
            verdict = json.loads(json.dumps(verdict))

            assert 'verdict' in verdict, "{} result must contain the 'verdict' key".format(preamble)
            final_verdict = ('ACCEPT', 'DENY')
            needinfo_verdict = ('NEEDINFO', )
            possible_verdicts = final_verdict + needinfo_verdict
            assert verdict['verdict'] in possible_verdicts,\
                "{} result must be one of {}".format(preamble, possible_verdicts)
            if verdict['verdict'] in final_verdict:
                print("{} finished with: {}".format(
                    preamble,
                    json.dumps(self.clean(verdict), sort_keys=True, indent=4))
                )
                break

            assert verdict['verdict'] == 'NEEDINFO'
            assert 'question' in verdict, "{} needinfo verdict must contain the 'question' key".format(preamble)
            question = verdict['question']
            assert isinstance(question, list), "{} needinfo question should be a list".format(preamble)
            assert len(question) == 3, "{} needinfo question should have 3 items".format(preamble)
            assert isinstance(question[0], str),\
                "{} needinfo question 1st item should be key string".format(preamble)
            assert isinstance(question[1], str),\
                "{} needinfo question 2nd item should be prompt string".format(preamble)
            assert isinstance(question[2], bool),\
                "{} needinfo question 3rd item should be disble_echo boolean".format(preamble)
            answer = input(question[1])
            self.parameters['key_value_pairs'][question[0]] = answer
            if 'cookie' in verdict:
                self.parameters['cookie'] = verdict['cookie']
            if 'session_cookie' in verdict:
                self.parameters['session_cookie'] = verdict['session_cookie']

    @classmethod
    def clean(cls, data):
        if isinstance(data, dict):
            return {k: cls.clean(v) for k, v in data.items() if '_' != k[0]}
        else:
            return data
