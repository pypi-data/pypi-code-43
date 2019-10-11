from alas_tools.wrappers.datetime_wrapper import DatetimeWrapper

from alas_tools.common.clients.api_client import ApiHttpClientBase, ApiClientRequest

class IntergradialClientBase(ApiHttpClientBase):
    entity_endpoint_base_url = ''

    def __init__(self, **kwargs):
        super(IntergradialClientBase, self).__init__(**kwargs)
        self.username_default = kwargs.pop('username_default', None)
        self.password_default = kwargs.pop('password_default', None)
        self.agent_default = kwargs.pop('agent_default', None)
        self.source_default = kwargs.pop('source_default', None)

    def call_function(self, request_params):

        self.check_default_params(request_params)

        url_str = self.entity_endpoint_base_url

        for item in request_params:
            url_str += "&{}=".format(item) + "{" + item + "}"

        url = url_str.replace("?&", "?").format(**request_params)

        request = ApiClientRequest(url, json_request=False)
        response = self.http_get(request)

        return response

    def check_default_params(self, request_params):

        if 'user' not in request_params:
            request_params.update({'user': self.username_default})

        if 'pass' not in request_params:
            request_params.update({'pass': self.password_default})

        if 'source' not in request_params:
            request_params.update({'source': self.source_default})

    def process_response(self, response):
        """
        :type response: str
        """
        result = {
            'status': 'ERROR',
            'message': 'NOT MESSAGE',
            'info': ''
        }

        if response is None or response == '':
            return result

        aux = response.split(':')
        status = aux[0]

        aux = aux[1].split('-')
        message = aux[0].strip(' ')

        aux = aux[1].split('|')

        result = {
            'status': status,
            'message': message,
            'info': aux
        }

        return result

    def line_to_dic(self, keys, line):

        aux = line.split('|')

        result = {}

        for i in range(len(keys)):
            result.update({keys[i]: aux[i]})

        return result


class AgentIntergradialClient(IntergradialClientBase):
    entity_endpoint_base_url = '/agc/api.php?'

    def __init__(self, **kwargs):
        super(AgentIntergradialClient, self).__init__(**kwargs)

    def external_dial(self, request_params):

        if 'function' not in request_params:
            request_params.update({'function': 'external_dial'})

        if 'phone_code' not in request_params:
            request_params.update({'phone_code': '56'})

        if 'search' not in request_params:
            request_params.update({'search': 'NO'})

        if 'preview' not in request_params:
            request_params.update({'preview': 'NO'})

        if 'focus' not in request_params:
            request_params.update({'focus': 'YES'})

        if 'agent_user' not in request_params:
            request_params.update({'agent_user': self.agent_default})

        response = self.call_function(request_params)
        return self.process_response(response.content)


class NonAgentIntergradialClient(IntergradialClientBase):
    entity_endpoint_base_url = '/vicidial/non_agent_api.php?'

    def __init__(self, **kwargs):
        super(NonAgentIntergradialClient, self).__init__(**kwargs)

    def get_last_dial(self, request_params):

        items = self.phone_number_log(request_params)
        if len(items) > 0:
            keys = "phone_number|call_date|list_id|length_in_sec|lead_status|hangup_reason|call_status|source_id|user" \
                .split('|')

            return self.line_to_dic(keys, items[0])

        return None

    def phone_number_log(self, request_params):

        if 'function' not in request_params:
            request_params.update({'function': 'phone_number_log'})

        if 'stage' not in request_params:
            request_params.update({'stage': 'pipe'})

        response = self.call_function(request_params)
        result = []
        if response.response.status == 200:
            content = response.content  # type: str
            if content.startswith("ERROR:") or content.startswith("NOTICE:"):
                result = self.process_response(content)
            else:
                result = response.content.split('\n')

        return result

    def recording_lookup(self, request_params):

        if 'function' not in request_params:
            request_params.update({'function': 'recording_lookup'})

        if 'stage' not in request_params:
            request_params.update({'stage': 'pipe'})

        if 'agent_user' not in request_params:
            request_params.update({'agent_user': self.agent_default})

        if 'date' not in request_params:
            local_day = DatetimeWrapper.today()
            request_params.update({'date': DatetimeWrapper.datetime_to_str(local_day, "%Y-%m-%d")})

        response = self.call_function(request_params)

        keys = "start_time|user|recording_id|lead_id|location" \
            .split('|')

        result = []
        if response.response.status == 200:
            content = response.content  # type: str
            if content.startswith("ERROR:") or content.startswith("NOTICE:"):
                result = self.process_response(content)
            else:
                items = response.content.split('\n')
                for item in items:
                    result.append(self.line_to_dic(keys, item))

        return result
