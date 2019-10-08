from behave import given

from rikki.behave.context import Context
import time


@given('Wait for shutdown')
def step_wait_for_shutdown(context: Context):
    time.sleep(100)
    step_wait_for_shutdown(context)
