import os
import re
import time

from json import JSONDecoder
from pathlib import Path
from typing import Optional, Pattern

from rikki.behave.context import Context
from rikki.mitmproxy.delegate_accumulate import AccumulateFilterConfig, Accumulate
from rikki.mitmproxy.model import Request, Response


def __take_not_empty_request(request: Request) -> Optional[Request]:
    if not request.empty():
        return request
    else:
        return None


def __take_not_empty_response(response: Response) -> Optional[Response]:
    if not response.empty():
        return response
    else:
        return None


def variable_for_key(key: str) -> str:
    if key.startswith("os."):
        var_name = key.replace("os.", "").upper()
        if var_name in os.environ:
            return os.environ[var_name]
        else:
            assert False, "Can't find environment variable {0}, did you forget to add it?".format(var_name)
    elif key.startswith("file."):
        file_name = key.replace("file.", "")
        path = Path("res/{0}".format(file_name))
        if os.path.exists(path):
            with open(path, "r") as file:
                return file.read()
        else:
            assert False, "Can't find file {0}, in {1}?".format(file_name, path.resolve())


def resolve_variables(candidate):
    result = candidate
    if isinstance(result, str):
        vars = re.findall(r'%{[^}%]+}%', result)
        for var in vars:
            result = result.replace(var, variable_for_key(var.replace('%{', '').replace('}%', '')))

    return result


class HttpStepData:

    def __init__(
            self,
            filter_request: Optional[Request] = None,
            filter_response: Optional[Response] = None,
            replacement_request: Optional[Request] = None,
            replacement_response: Optional[Response] = None
    ) -> None:
        self.filter_request: Optional[Request] = filter_request
        self.filter_response: Optional[Response] = filter_response
        self.replacement_request: Optional[Request] = replacement_request
        self.replacement_response: Optional[Response] = replacement_response

    def empty(self) -> bool:
        if self.filter_request or self.filter_response or self.replacement_request or self.replacement_response:
            return False
        else:
            return True


def http_data(context: Context) -> Optional[HttpStepData]:
    if context.table:
        json_decoder = JSONDecoder()

        filter_request = Request()
        filter_response = Response()
        replacement_request = Request()
        replacement_response = Response()

        for row in context.table:
            if row['option'] == 'port':
                filter_request.port = resolve_variables(row['value'])
            if row['option'] == 'host':
                filter_request.host = resolve_variables(row['value'])
            if row['option'] == 'method':
                filter_request.method = resolve_variables(row['value'])
            if row['option'] == 'path':
                filter_request.path = resolve_variables(row['value'])
            if row['option'] == 'headers':
                filter_request.headers = json_decoder.decode(resolve_variables(row['value']))
            if row['option'] == 'params':
                filter_request.params = json_decoder.decode(resolve_variables(row['value']))
            if row['option'] == 'content':
                filter_request.content = resolve_variables(row['value'])
            if row['option'] == 'response_code':
                filter_response.code = resolve_variables(row['value'])
            if row['option'] == 'response_headers':
                filter_response.headers = json_decoder.decode(resolve_variables(row['value']))
            if row['option'] == 'response_content':
                filter_response.content = resolve_variables(row['value'])
            if row['option'] == 'replace_port':
                replacement_request.port = resolve_variables(row['value'])
            if row['option'] == 'replace_host':
                replacement_request.host = resolve_variables(row['value'])
            if row['option'] == 'replace_path':
                replacement_request.path = resolve_variables(row['value'])
            if row['option'] == 'replace_headers':
                replacement_request.headers = json_decoder.decode(resolve_variables(row['value']))
            if row['option'] == 'replace_params':
                replacement_request.params = json_decoder.decode(resolve_variables(row['value']))
            if row['option'] == 'replace_content':
                replacement_request.content = resolve_variables(row['value'])
            if row['option'] == 'replace_response_code':
                replacement_response.code = resolve_variables(row['value'])
            if row['option'] == 'replace_response_content':
                replacement_response.content = resolve_variables(row['value'])
            if row['option'] == 'replace_response_headers':
                replacement_response.headers = json_decoder.decode(resolve_variables(row['value']))

        result = HttpStepData(
            filter_request=__take_not_empty_request(filter_request),
            filter_response=__take_not_empty_response(filter_response),
            replacement_request=__take_not_empty_request(replacement_request),
            replacement_response=__take_not_empty_response(replacement_response)
        )

        if not result.empty():
            return result
    return None


def verify_number_of_request(
        context: Context,
        number: int,
        tag: str,
        second_attempt: bool = False,
        delay: int = 5,
        in_send: Optional[str] = None,
        in_receive: Optional[str] = None
):
    """

    :param in_receive: will search in request for the data
    :param in_send: will search in response for the data
    :param context: behave context to work with
    :param number: number of requests to verify
    :param tag: string to use with exception output to identify particular request
    :param second_attempt: if True will make delay and second attempt after specified delay
    :param delay: seconds to wait before next attempt
    """
    http_step_data = http_data(context)
    filter_request = None
    filter_response = None
    if http_step_data:
        filter_request = http_step_data.filter_request
        filter_response = http_step_data.filter_response

    if http_step_data or in_send or in_receive:
        config = AccumulateFilterConfig(
            request=filter_request,
            response=filter_response,
            in_send=in_send,
            in_receive=in_receive
        )
        plugin = Accumulate(filter_config=config)
        context.proxy.add_delegate(plugin)

        if not second_attempt:
            assert number == len(plugin.accumulated_items), \
                "Expected number of requests {0} is {1}, but actual is {2}\n{3}".format(
                    tag,
                    number,
                    len(plugin.accumulated_items),
                    plugin.accumulated_items
                )
        else:
            if number != len(plugin.accumulated_items):
                time.sleep(delay)
                verify_number_of_request(context, number, tag, False)


def create_pattern(input: str) -> Pattern:
    if input.startswith("r\"") and input.endswith("\""):
        cleaned_up_input = input[2:len(input)-1]
        return __create_full_featured_pattern(cleaned_up_input)
    else:
        return __create_simplified_pattern(input)


def __create_full_featured_pattern(input: str) -> Pattern:
    return re.compile(input)


def __create_simplified_pattern(input: str) -> Pattern:
    pattern_ready = input.replace(".", r"\.").replace("*", ".*")
    return re.compile(pattern_ready)
