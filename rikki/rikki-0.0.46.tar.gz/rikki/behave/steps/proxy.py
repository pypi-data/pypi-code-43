from behave import given, then

from rikki.behave.context import Context
from rikki.behave.steps.utils import http_data
from rikki.behave.steps.utils import verify_number_of_request
from rikki.mitmproxy.delegate_replace import ReplacementConfig, InterceptAndReplace
from rikki.mitmproxy.delegate_delay import DelayConfig, Delay
from rikki.mitmproxy.delgate.dump import DumpWriterConfig, DumpWriterDelegate


@given("Delay request for {number:d} seconds")
def step_delay(context: Context, number):
    http_step_data = http_data(context)

    if http_step_data:
        config = DelayConfig(
            request=http_step_data.filter_request,
            response=http_step_data.filter_response,
            delay=number
        )
        plugin = Delay(config=config)
        context.proxy.add_delegate(plugin)


@given("Randomly delay request for {number:d} seconds")
def step_random_delay(context: Context, number):
    http_step_data = http_data(context)

    if http_step_data:
        config = DelayConfig(
            request=http_step_data.filter_request,
            response=http_step_data.filter_response,
            delay=number,
            random=True
        )
        plugin = Delay(config=config)
        context.proxy.add_delegate(plugin)


@given("Intercept and replace http data")
def step_replace_http_data(context: Context):
    http_step_data = http_data(context)

    if http_step_data:
        config = ReplacementConfig(
            filter_request=http_step_data.filter_request,
            filter_response=http_step_data.filter_response,
            replacement_request=http_step_data.replacement_request,
            replacement_response=http_step_data.replacement_response,
            wait_response=False
        )
        plugin = InterceptAndReplace(config=config, recursive=False)
        context.proxy.add_delegate(plugin)


@given("Replace http data")
def step_replace_http_data(context: Context):
    http_step_data = http_data(context)

    if http_step_data:
        config = ReplacementConfig(
            filter_request=http_step_data.filter_request,
            filter_response=http_step_data.filter_response,
            replacement_request=http_step_data.replacement_request,
            replacement_response=http_step_data.replacement_response,
        )
        plugin = InterceptAndReplace(config=config, recursive=False)
        context.proxy.add_delegate(plugin)


@then('Verify {number:d} requests for "{tag}"')
def step_verify_number_of_requests(context: Context, number, tag):
    verify_number_of_request(
        context=context,
        number=number,
        tag=tag,
        second_attempt=True
    )


@then('Check no "{data}" in any requests/responses because "{tag}"')
def step_check_for_data_in_http(context: Context, data: str, tag):
    verify_number_of_request(
        context=context,
        number=0,
        tag=tag,
        second_attempt=True,
        in_send=data,
        in_receive=data
    )


@then('Check no "{data}" in any request because "{tag}"')
def step_check_for_request_in_http(context: Context, data: str, tag):
    verify_number_of_request(
        context=context,
        number=0,
        tag=tag,
        second_attempt=True,
        in_send=data
    )


@then('Check no "{data}" in any responses because "{tag}"')
def step_check_for_response_in_http(context: Context, data: str, tag):
    verify_number_of_request(
        context=context,
        number=0,
        tag=tag,
        second_attempt=True,
        in_receive=data
    )


@given('Save network data in "{path}"')
def step_save_network_flows(context: Context, path: str):
    http_step_data = http_data(context)
    config = DumpWriterConfig(
        request=http_step_data.filter_request,
        response=http_step_data.filter_response,
        path=path
    )
    context.proxy.add_delegate(DumpWriterDelegate(config))
