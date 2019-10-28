import logging

from pyoadr_ven import OpenADRVenAgent

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
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
        "report_name": "ccoop_telemetry_evse_status",
        "report_interval_secs_default": 30,
        "telemetry_parameters": evese_telemetry_short_status_parameters,
    }
}

agent = OpenADRVenAgent(
    ven_id="1",
    vtn_id="ccoopvtn01",
    vtn_address="http://localhost:3000",
    client_pem_bundle="/home/peter/carboncoop/pyoadr-ven/tests/client.pem",
    vtn_ca_cert="/home/peter/carboncoop/pyoadr-ven/tests/ca.crt",
    report_parameters=evse_telemetry_short_status_report_parameters,
    log_xml=True,
    db_filepath="/home/peter/carboncoop/pyoadr-ven/db.sqlite",
)

agent.send_oadr_register_report()
