import os
import threading

from stackifyapm.conf.constants import DEFAULT_CONFIG_FILE
from stackifyapm.instrumentation.control import instrument
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import execution_context


class DummyClient(object):
    # Dummy client since the original client is not pickable

    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        self.config_file = config_file

    def get_application_info(self):
        return {
            "config_file": self.config_file,
        }


class MultiprocessingRunWrapper(object):
    # class that will wrap multiprocessing run method

    def __init__(self, run, client=None):
        self.run = run
        self.client = client

    def run_wrapper(self, *args, **kwargs):
        # we need to run instrument() before the child process
        # start running the target run method
        instrument(client=self.client)
        return self.run(*args, **kwargs)


def wrap_target(function, args, transaction=None, span=None):
    thread = threading.current_thread()
    thread.transaction = transaction
    thread.span = span
    transaction and execution_context.set_transaction(transaction)
    span and execution_context.set_span(span)
    return function(*args)


class ThreadInstrumentation(AbstractInstrumentedModule):
    name = "thread"

    instrument_list = [
        ("threading", "Thread.start"),
        ("thread", "start_new_thread"),
        ("_thread", "start_new_thread"),
        ("multiprocessing", "Process.start"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        transaction = execution_context.get_transaction()

        if transaction:
            transaction.set_has_async_spans(True)
            span = execution_context.get_span()

            if method == 'start_new_thread':
                args = (wrap_target, args, {'transaction': transaction, 'span': span})
            elif method == 'Thread.start':
                instance.transaction = transaction
                instance.span = span
            elif method == 'Process.start':
                instance.transaction = transaction
                instance.span = span
                if os.name == 'nt' and self._get_framework_name() not in ['flask']:
                    # since windows is using spawn for multiprocessing
                    # we need to re-instrument on each child process
                    # so we can capture spans instrumentation
                    dummy_client = DummyClient(config_file=self.client.get_application_info().get('config_file'))
                    wrapper = MultiprocessingRunWrapper(instance.run, client=dummy_client)
                    instance.run = wrapper.run_wrapper

        return wrapped(*args, **kwargs)

    def _get_framework_name(self):
        return self.client.config.framework_name and self.client.config.framework_name.lower()
