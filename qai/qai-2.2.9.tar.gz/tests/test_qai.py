import asyncio

import uvloop  # from requirements-dev.txt
from qai.issues.issues import make_issue
from qai.qconnect.qrest import QRest
from qai.qonfigs import get_configs
from qai.strings import get_strings_json


class MockAnalyzer:
    def __init__(self):
        pass

    def analyze(self, *args, **kwargs):
        return make_issue(
            "test",
            0,
            1,
            "test_issue_type",
            0,
            description="test issue description",
            suggestions=["X"],
        )


def whitelister(issues, meta_value, sub_groups=[]):
    if meta_value is not None:
        assert isinstance(meta_value, int)
    return issues


def test_server():
    server = QRest(
        MockAnalyzer(), category="test_qai", white_lister=whitelister
    ).get_future()

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    _ = asyncio.ensure_future(server)

    loop.stop()  # I am pretty sure that this starts the loop for one loop
