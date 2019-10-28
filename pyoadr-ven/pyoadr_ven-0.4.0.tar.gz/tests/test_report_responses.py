import logging

import pytest
import responses

_LOGGER = logging.getLogger(__name__)

VTN_ADDRESS = "https://openadr-staging"
ENDPOINT_BASE = "/OpenADR2/Simple/2.0b/"
ENDPOINT = VTN_ADDRESS + ENDPOINT_BASE
EIEVENT = ENDPOINT + "EiEvent"
EIREPORT = ENDPOINT + "EiReport"
EIREGISTERPARTY = ENDPOINT + "EiRegisterParty"
POLL = ENDPOINT + "OadrPoll"

with open("tests/xml/ven_oadrRegisterReport.xml", "r") as f:
    oadrRegisterReport_body = f.read()

with open("tests/xml/vtn_oadrRegisterReport_response.xml", "r") as f:
    oadrRegisterReport_response_body = f.read()

pytestmark = pytest.mark.pony(db_session=False)


class TestRegisterReport:
    @responses.activate
    def test_register_report(self, mocked_agent):
        responses.add(
            responses.POST,
            EIREPORT,
            content_type="text/xml",
            body=oadrRegisterReport_body,
        )
        responses.add(
            responses.POST,
            EIREPORT,
            content_type="text/xml",
            body=oadrRegisterReport_response_body,
        )
        mocked_agent.send_oadr_register_report()
        assert responses.calls[0].request.url == EIREPORT
