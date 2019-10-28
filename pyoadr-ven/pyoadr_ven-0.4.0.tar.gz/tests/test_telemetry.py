import json
import logging
from datetime import datetime

import pytest

from pyoadr_ven import database


_LOGGER = logging.getLogger(__name__)
pytestmark = pytest.mark.pony


class TestTelemetry:
    def test_add_telemetry_json(self, mocked_agent):
        values_dict = {"state": "on"}
        mocked_agent.add_telemetry_json(
            "ccoop_telemetry_evse_status",
            start_time=datetime.utcnow(),
            values=values_dict,
        )
        assert database.TelemetryValues[1].values == json.dumps(values_dict)
        assert (
            database.TelemetryValues[1].report_specifier_id
            == "ccoop_telemetry_evse_status"
        )

    # def test_get_new_telemetry_for_report(self, mocked_agent):
    #     mocked_agent.get_new_telemetry_for_report()
