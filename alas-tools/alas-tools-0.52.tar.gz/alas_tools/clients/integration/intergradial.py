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

        if 'user' not in request_params and self.username_default is not None:
            request_params.update({'user': self.username_default})

        if 'pass' not in request_params and self.password_default is not None:
            request_params.update({'pass': self.password_default})

        if 'source' not in request_params and self.source_default is not None:
            request_params.update({'source': self.source_default})

    def process_response(self, response, keys=None, keys_error=None):
        """
        :param keys_error:
        :param keys:
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

        if status == "ERROR" and keys_error is not None:
            aux = self.line_to_dic(keys_error, aux[1])
        elif status == "SUCCESS"  and keys is not None:
            aux = self.line_to_dic(keys, aux[1])
        else:
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
            request_params.update({'phone_code': '1'})

        if 'search' not in request_params:
            request_params.update({'search': 'NO'})

        if 'preview' not in request_params:
            request_params.update({'preview': 'NO'})

        if 'focus' not in request_params:
            request_params.update({'focus': 'YES'})

        if 'agent_user' not in request_params:
            request_params.update({'agent_user': self.agent_default})

        keys = "phone_number|agent_user|phone_code|search|preview|focus|vendor_id|epoch|dial_prefix|group_alias" \
               "|caller_id_number|alt_dial" \
            .split('|')

        response = self.call_function(request_params)
        result = self.process_response(response.content, keys)
        return result


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

        keys = "phone_number|call_date|list_id|length_in_sec|lead_status|hangup_reason|call_status|source_id|user" \
        .split("|")
        response = self.call_function(request_params)
        result = []
        if response.response.status == 200:
            content = response.content  # type: str
            if content.startswith("ERROR:") or content.startswith("NOTICE:"):
                result = self.process_response(content)
            else:
                aux = response.content.split('\n')
                for item in aux:
                    if item:
                        result.append(self.line_to_dic(keys, item))

        return result

    def agent_status(self, request_params):

        if 'function' not in request_params:
            request_params.update({'function': 'agent_status'})

        if 'agent_user' not in request_params:
            request_params.update({'agent_user': self.username_default})

        if 'stage' not in request_params:
            request_params.update({'stage': 'pipe'})

        keys = 'status|call_id|lead_id|campaign_id|calls_today|full_name|user_group|user_level|pause_code' \
               '|real_time_sub_status|phone_number|vendor_lead_code|session_id'.split('|')
        response = self.call_function(request_params)
        result = []
        if response.response.status == 200:
            content = response.content  # type: str
            if content.startswith("ERROR:") or content.startswith("NOTICE:"):
                result = self.agent_status_process_response(content)
            else:
                # aux = response.content.split('\n')
                result = self.line_to_dic(keys, response.content)

        return result

    def agent_status_process_response(self, response, keys=None, keys_error=None):
        """
        :param keys_error:
        :param keys:
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
        message = aux[1].strip(' ')

        if status == "ERROR" and keys_error is not None:
            aux = self.line_to_dic(keys_error, aux[1])
        elif status == "SUCCESS"  and keys is not None:
            aux = self.line_to_dic(keys, aux[1])
        else:
            aux = aux[2].split('|')

        result = {
            'status': status,
            'message': message,
            'info': aux
        }

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
                result = self.process_response(content, keys)
            else:
                items = response.content.split('\n')
                for item in items:
                    if item:
                        result.append(self.line_to_dic(keys, item))

        return result
