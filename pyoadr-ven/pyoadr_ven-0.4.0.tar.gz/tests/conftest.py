import pytest

from pyoadr_ven import database
from pyoadr_ven import OpenADRVenAgent


LOCAL_VTN_ADDRESS = "http://localhost:3000"
LOCAL_VEN_ID = "1"
LOCAL_VTN_ID = "ccoopvtn01"

MOCK_VTN_ADDRESS = "https://openadr-staging"
MOCK_VEN_ID = "ven01"
MOCK_VTN_ID = "vtn01"

CERT_PATH = "/home/peter/carboncoop/pyoadr-ven/tests/client.pem"
CA_PATH = "/home/peter/carboncoop/pyoadr-ven/tests/ca.crt"

database.setup_db()

evese_telemetry_short_status_parameters = {
    "state": {
        "r_id": "evse state",
        "units": "NA",
        "min_frequency": 30,
        "max_frequency": 30,
        "report_type": "",
        "reading_type": "",
        "method_name": "state",
    },
    "amp": {
        "r_id": "evse charging current",
        "units": "A",
        "min_frequency": 30,
        "max_frequency": 30,
        "report_type": "",
        "reading_type": "",
        "method_name": "amp",
    },
    "wh": {
        "r_id": "evse energy used in session",
        "units": "Wh",
        "min_frequency": 30,
        "max_frequency": 30,
        "report_type": "",
        "reading_type": "",
        "method_name": "wh",
    },
}

evse_telemetry_short_status_report_parameters = {
    "ccoop_telemetry_evse_status": {
        "report_name_metadata": "ccoop_telemetry_evse_status",
        "report_interval_secs_default": 30,
        "telemetry_parameters": evese_telemetry_short_status_parameters,
    }
}


@pytest.fixture
def mocked_agent():

    agent = OpenADRVenAgent(
        ven_id=MOCK_VEN_ID,
        vtn_id=MOCK_VTN_ID,
        vtn_address=MOCK_VTN_ADDRESS,
        security_level="standard",
        poll_interval_secs=15,
        log_xml=True,
        opt_timeout_secs=30,
        opt_default_decision="optIn",
        report_parameters=evse_telemetry_short_status_report_parameters,
        client_pem_bundle=CERT_PATH,
        vtn_ca_cert=CA_PATH,
    )
    return agent


@pytest.fixture
def local_agent():
    agent = OpenADRVenAgent(
        ven_id=LOCAL_VEN_ID,
        vtn_id=LOCAL_VTN_ID,
        vtn_address=LOCAL_VTN_ADDRESS,
        security_level="standard",
        poll_interval_secs=15,
        log_xml=True,
        opt_timeout_secs=30,
        opt_default_decision="optIn",
        report_parameters=evse_telemetry_short_status_report_parameters,
        client_pem_bundle=CERT_PATH,
        vtn_ca_cert=CA_PATH,
    )
    return agent
