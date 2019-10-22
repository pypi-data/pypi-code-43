import gossip
import logbook
import pytest
import uuid
from munch import Munch


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    logbook.compat.redirect_logging()
    logbook.StderrHandler().push_application()


@pytest.fixture
def called_counters(request):
    obj = CalledCounters()
    request.addfinalizer(obj.unregister)
    return obj


class CalledCounters:
    def __init__(self):
        super().__init__()
        self._called = Munch(start=0, error=0, end=0, success=0)
        self._token = str(uuid.uuid4())
        self._is_active = True
        gossip.register(self._on_step_start, 'slash.step_start', token=self._token)
        gossip.register(self._on_step_end, 'slash.step_end', token=self._token)
        gossip.register(self._on_step_success, 'slash.step_success', token=self._token)
        gossip.register(self._on_step_error, 'slash.step_error', token=self._token)

    def unregister(self):
        gossip.unregister_token(self._token)
        self._is_active = False

    def _on_step_start(self):
        self._called.start += 1

    def _on_step_error(self):
        self._called.error += 1

    def _on_step_end(self):
        self._called.end += 1

    def _on_step_success(self):
        self._called.success += 1

    def verify_calls(self, start=1, success=1, end=1, error=0):
        assert self._is_active
        assert self._called == dict(start=start, success=success, end=end, error=error)
