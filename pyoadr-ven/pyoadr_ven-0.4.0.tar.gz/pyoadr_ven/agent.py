# Copyright 2017, Battelle Memorial Institute.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}
import json
import logging
import random
import sys
from collections import namedtuple
from datetime import datetime
from datetime import timedelta
from io import StringIO
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

import isodate
import lxml.etree as etree_
import pem
import requests
import signxml
from pony import orm
from requests.exceptions import ConnectionError

from . import builders
from . import database
from . import enums
from . import exceptions
from . import extractors
from . import models
from . import oadr_20b
from . import response_codes
from .utils import get_aware_utc_now

_LOGGER = logging.getLogger(__name__)

ENDPOINT_BASE = "/OpenADR2/Simple/2.0b/"
EIEVENT = ENDPOINT_BASE + "EiEvent"
EIREPORT = ENDPOINT_BASE + "EiReport"
EIREGISTERPARTY = ENDPOINT_BASE + "EiRegisterParty"
POLL = ENDPOINT_BASE + "OadrPoll"

Endpoint = namedtuple("Endpoint", ["url", "callback"])
OPENADR_ENDPOINTS = {
    "EiEvent": Endpoint(url=EIEVENT, callback="push_request"),
    "EiReport": Endpoint(url=EIREPORT, callback="push_request"),
    "EiRegisterParty": Endpoint(url=EIREGISTERPARTY, callback="push_request"),
}


MIN_LOOP_FREQUENCY_SECS = 5
DEFAULT_POLL_FREQUENCY_SECS = 15
DEFAULT_REPORT_INTERVAL_SECS = 15
DEFAULT_OPT_TIMEOUT_SECS = 30 * 60


class OpenADRVenAgent:
    """
        OpenADR (Automated Demand Response) is a standard for alerting and responding
        to the need to adjust electric power consumption in response to fluctuations
        in grid demand.

        OpenADR communications are conducted between Virtual Top Nodes (VTNs) and Virtual End Nodes (VENs).
        In this implementation, a this agent is a VEN, implementing EiEvent and EiReport services
        in conformance with a subset of the OpenADR 2.0b specification.

        The VEN receives VTN requests via the web service.

        The VTN can 'call an event', indicating that a load-shed event should occur.
        The VEN responds with an 'optIn' acknowledgment.

        Events:
            The VEN agent maintains a persistent record of DR events.
            These events are stored in a sqlite database

        Reporting:
            The VEN agent configuration defines telemetry values (data points) to be reported to the VTN.
            The VEN agent maintains a persistent record of reportable/reported telemetry values over time.

        Supported requests/responses in the OpenADR VTN interface:
            VTN:
                oadrDistributeEvent (needed for event cancellation)
                oadrResponse
                oadrRegisteredReport
                oadrCreateReport
                oadrUpdatedReport
                oadrCancelReport
                oadrCreatedPartyRegistration
            VEN:
                oadrPoll
                oadrRequestEvent
                oadrCreatedEvent
                oadrResponse
                oadrRegisterReport
                oadrCreatedReport
                oadrUpdateReport
                oadrCanceledReport
                oadrCreatePartyRegistration
                oadrQueryRegistration


        Event workflow (see OpenADR Profile Specification section 8.1)...

        Event poll / creation:
            (VEN) oadrPoll
            (VTN) oadrDistributeEvent (all events are included; one oadrEvent element per event)
            (VEN) oadrCreatedEvent with optIn/optOut (if events had oadrResponseRequired)
                    If "always", an oadrCreatedEvent must be sent for each event.
                    If "never", it was a "broadcast" event -- never create an event in response.
                    Otherwise, respond if event state (eventID, modificationNumber) has changed.
            (VTN) oadrResponse

        Event change:
            (VEN) oadrCreatedEvent (sent if the optIn/optOut status has changed)
            (VTN) oadrResponse

        Sample oadrDistributeEvent use case from the OpenADR Program Guide:

            Event:
                Notification: Day before event
                Start Time: midnight
                Duration: 24 hours
                Randomization: None
                Ramp Up: None
                Recovery: None
                Number of signals: 2
                Signal Name: simple
                    Signal Type: level
                    Units: LevN/A
                    Number of intervals: equal TOU Tier change in 24 hours (2 - 6)
                    Interval Duration(s): TOU tier active time frame (i.e. 6 hours)
                    Typical Interval Value(s): 0 - 4 mapped to TOU Tiers (0 - Cheapest Tier)
                    Signal Target: None
                Signal Name: ELECTRICITY_PRICE
                    Signal Type: price
                    Units: USD per Kwh
                    Number of intervals: equal TOU Tier changes in 24 hours (2 - 6)
                    Interval Duration(s): TOU tier active time frame (i.e. 6 hours)
                    Typical Interval Value(s): $0.10 to $1.00 (current tier rate)
                    Signal Target: None
                Event Targets: venID_1234
                Priority: 1
                VEN Response Required: always
                VEN Expected Response: optIn
            Reports:
                None

        Report workflow (see OpenADR Profile Specification section 8.3)...

        Report registration interaction:
            (VEN) oadrRegisterReport (METADATA report)
                VEN sends its reporting capabilities to VTN.
                Each report, identified by a reportSpecifierID, is described as elements and attributes.
            (VTN) oadrRegisteredReport (with optional oadrReportRequests)
                VTN acknowledges that capabilities have been registered.
                VTN optionally requests one or more reports by reportSpecifierID.
                Even if reports were previously requested, they should be requested again at this point.
            (VEN) oadrCreatedReport (if report requested)
                VEN acknowledges that it has received the report request and is generating the report.
                If any reports were pending delivery, they are included in the payload.
            (VTN) oadrResponse
                Why??

        Report creation interaction:
            (VTN) oadrCreateReport
                See above - this is like the "request" portion of oadrRegisteredReport
            (VEN) oadrCreatedReport
                See above.

        Report update interaction - this is the actual report:
            (VEN) oadrUpdateReport (report with reportRequestID and reportSpecifierID)
                Send a report update containing actual data values
            (VTN) oadrUpdatedReport (optional oadrCancelReport)
                Acknowledge report receipt, and optionally cancel the report

        Report cancellation:
            (VTN) oadrCancelReport (reportRequestID)
                This can be sent to cancel a report that is in progress.
                It should also be sent if the VEN keeps sending oadrUpdateReport
                    after an oadrUpdatedReport cancellation.
                If reportToFollow = True, the VEN is expected to send one final additional report.
            (VEN) oadrCanceledReport
                Acknowledge the cancellation.
                If any reports were pending delivery, they are included in the payload.

        Key elements in the METADATA payload:
            reportSpecifierID: Report identifier, used by subsequent oadrCreateReport requests
            rid: Data point identifier
                This VEN reports only two data points: baselinePower, actualPower
            Duration: the amount of time that data can be collected
            SamplingRate.oadrMinPeriod: maximum sampling frequency
            SamplingRate.oadrMaxPeriod: minimum sampling frequency
            SamplingRate.onChange: whether or not data is sampled as it changes

        For an oadrCreateReport example from the OpenADR Program Guide, see test/xml/sample_oadrCreateReport.xml.

    """

    EiReports: List[models.EiReport] = []
    EiTelemetryValuess: List[models.EiTelemetryValues] = []

    _last_poll: Optional[datetime] = None

    reports_registered: bool = False

    def __init__(
        self,
        *,
        ven_id: str,
        vtn_id: str,
        vtn_address: str,
        client_pem_bundle: str,
        vtn_ca_cert: str,
        db_filepath: Optional[str] = None,
        log_xml: bool = False,
        opt_default_decision: str = enums.OptType.OPT_IN.value,
        opt_timeout_secs: int = DEFAULT_OPT_TIMEOUT_SECS,
        poll_interval_secs: int = DEFAULT_POLL_FREQUENCY_SECS,
        report_parameters={},
        security_level: str = "standard",
    ):
        """
        Initialize the agent.

        The ``report_parameters`` option should look like so:

        .. code-block:: python

            report_parameters={
                "reportSpecifierId": {
                    "report_interval_secs_default": 15,
                    "report_name": name,
                    "telemetry_parameters": { ... },  # Should be JSON-safe
                }
            }

        :param ven_id: OpenADR ID of this virtual end node. Identifies this VEN to the VTN.
        :param vtn_id: ID of the VTN with which this VEN will communicate
        :param vtn_address: URL of the VTN
        :param client_pem_bundle: The pem bundle (private key + certificate concatenated) to present to the server for HTTPS mutual auth
        :param vtn_ca_cert: The path of the certificate from the CA that the client certs have been signed with.
        :param db_filepath: The path to the SQLite database file.  If not provided, will be kept in-memory.
        :param log_xml: Whether to write inbound/outbound XML to the agent's log
        :param opt_default_decision: What opt-in/opt-out choice to make by default
        :param opt_timeout_secs: How long to wait before making a default opt-in/opt-out decision
        :param poll_interval_secs: How often the VEN should send an OadrPoll to the VTN
        :param report_parameters: A dictionary of definitions of reporting/telemetry parameters
        :param security_level: If 'high', the VTN and VEN use a third-party signing authority to sign and authenticate each request. Default is 'standard' (XML payloads do not contain Signature elements)
        """
        self.ven_id = ven_id
        self.vtn_id = vtn_id
        self.vtn_address = vtn_address
        self.client_pem_bundle = client_pem_bundle
        self.vtn_ca_cert = vtn_ca_cert
        self.log_xml = log_xml
        self.opt_default_decision = opt_default_decision
        self.opt_timeout_secs = opt_timeout_secs
        self.poll_interval_secs = poll_interval_secs
        self.report_parameters = report_parameters
        self.security_level = security_level

        if self.poll_interval_secs < MIN_LOOP_FREQUENCY_SECS:
            raise ValueError(
                f"Poll interval is too frequent; use one higher than {MIN_LOOP_FREQUENCY_SECS}"
            )

        if "pytest" not in sys.modules:
            database.setup_db(db_filepath)

        # State variables for VTN request/response processing
        self.ven_online = "false"
        self.ven_manual_override = "false"

        _LOGGER.info("Configuration parameters:")
        _LOGGER.info(f"  ven_id = {ven_id}")
        _LOGGER.info(f"  vtn_id = {vtn_id}")
        _LOGGER.info(f"  vtn_address = {vtn_address}")
        _LOGGER.info(f"  client_pem_bundle = {client_pem_bundle}")
        _LOGGER.info(f"  vtn_ca_cert = {vtn_ca_cert}")
        _LOGGER.info(f"  log_xml = {log_xml}")
        _LOGGER.info(f"  opt_default_decision = {opt_default_decision}")
        _LOGGER.info(f"  opt_timeout_secs = {opt_timeout_secs}")
        _LOGGER.info(f"  poll_interval_secs = {poll_interval_secs}")
        _LOGGER.info(f"  report_parameters = {report_parameters}")
        _LOGGER.info(f"  security_level = {security_level}")

    def register(self, ven_name: str) -> dict:
        """
        Send a one-time registration request to the VTN using oadrCreatePartyRegistration

        This results in a dictionary with up to three keys.  It definitely will contain
        ``ven_id`` and ``vtn_id``.  It may contain ``poll_interval_secs``. These values
        should be stored somewhere safe, and passed to future initialisations of the
        ``OpenADRVenAgent``.

        :param ven_name: The name of this VEN, according to the OpenADR specification.
        """
        if not ven_name:
            raise ValueError("You need a ven_name to register")

        # VEN registration with the VTN server.
        # Register the VEN, obtaining the VEN ID. This is a one-time action.
        self.send_oadr_create_party_registration(ven_name)

        result = {
            "vtn_id": self.vtn_id,
            "ven_id": self.ven_id,
            "poll_interval_secs": self.poll_interval_secs,
        }

        # We do this to get around the fact that the server might have returned nothing
        # for the poll interval.  It's easier to set this value to None in the depths of
        # the server response handling code (see handle_oadr_created_party_registration)
        # and re-set it here to something sensible, than it is to restructure the code
        # so that it could e.g. return a value that might percolate up to this layer.
        # As such, it is a code smell.   XXX
        if not self.poll_interval_secs:
            self.poll_interval_secs = DEFAULT_POLL_FREQUENCY_SECS

        return result

    def request_events(self):
        """
        Make a request to the VTN for all current events.
        """
        self.send_oadr_request_event()

    def tick(self):
        """
        Perform the following tasks:
        - Polling the VTN server, if it is long enough since the last poll
        - Perform event management tasks:
          - force an optIn/optOut decision if too much time has elapsed.
          - transition event state when appropriate.
          - expire events that have become completed or canceled.
        - Perform report management tasks:
          - send telemetry to the VTN for any active report.
          - transition report state when appropriate.
          - expire reports that have become completed or canceled.

        The first time this function is called in an instance's lifetime, it will
        send an oadrRegisterReport request.

        This method should be called by your update method every clock tick.
        """
        if not self.reports_registered:
            # Send an initial report-registration request to the VTN.
            self.send_oadr_register_report()
            self.reports_registered = True

        # If it's been poll_interval_secs since the last poll request, issue a new one.
        if self._last_poll is None or (
            (get_aware_utc_now() - self._last_poll).total_seconds()
            > self.poll_interval_secs
        ):
            self.send_oadr_poll()

        for event in self.active_or_pending_events:
            self.process_event(event)

        for report in self.active_or_pending_reports:
            self.process_report(report.id)

    @orm.db_session
    def process_event(self, event: database.Event):
        """
        Perform periodic maintenance for an event.

        Transition its state when appropriate.
        """

        _LOGGER.debug(f"Processing event::: {event.event_id}")
        if event.is_active_or_pending:
            _LOGGER.debug(f"Event {event.event_id} is {event.status}")
            _LOGGER.debug(f"{event}")
            self._complete_event_if_over(event.event_id)
            self._force_opt_type(event.event_id)
            if event.status != enums.EventStatus.ACTIVE.value:
                self._activate_event_if_starts_now(event)

    @orm.db_session
    def _force_opt_type(self, event_id):
        _LOGGER.debug("Forcing Opt Type")
        _LOGGER.debug(f"opt types ")
        event = self.get_event_for_id(event_id)
        if event.opt_type != enums.OptType.NONE.value:
            _LOGGER.debug(f"opt type is not none {event.opt_type}")
            return
        if self.opt_default_decision not in enums.OptType.list():
            _LOGGER.debug("not in opt type list")
            return
        if event.status == enums.EventStatus.ACTIVE.value:
            event.opt_type = self.opt_default_decision
        _LOGGER.debug(f"opt timeout secs {self.opt_timeout_secs}")
        if not bool(self.opt_timeout_secs):
            event.opt_type = self.opt_default_decision
        if datetime.utcnow() >= event.created + timedelta(
            seconds=self.opt_timeout_secs
        ):
            event.opt_type = self.opt_default_decision

    @orm.db_session
    def _complete_event_if_over(self, event_id):
        event = self.get_event_for_id(event_id)
        now = datetime.utcnow()
        if not event.is_active_or_pending:
            return
        if event.end_time is None:
            return
        if now > event.end_time:
            _LOGGER.debug(
                "Setting event %s to status %s",
                event.event_id,
                enums.EventStatus.COMPLETED.value,
            )
            self._set_event_status(event.event_id, enums.EventStatus.COMPLETED)

    @orm.db_session
    def _activate_event_if_starts_now(self, event):
        now = datetime.utcnow()
        if now < event.start_time:
            return
        if event.opt_type != enums.OptType.OPT_IN.value:
            return
        _LOGGER.debug(
            "Setting event {} to status {}".format(
                event.event_id, enums.EventStatus.ACTIVE.value
            )
        )
        self._set_event_status(event.event_id, enums.EventStatus.ACTIVE)

    @orm.db_session
    def process_report(self, rpt_id: int):
        """
        Perform periodic maintenance for a report.

        Send telemetry to the VTN if the report is active.
        Transition its state when appropriate.
        Expire it from the cache if it has become completed or canceled.
        """
        rpt = database.Report.get(id=rpt_id)
        _LOGGER.debug(f"Processing report::: {rpt.name}")

        def _activate_report():
            if not rpt.start_time:
                return
            if rpt.start_time < now and (rpt.end_time is None or now < rpt.end_time):
                _LOGGER.debug(
                    "Setting report {} to status {}".format(
                        rpt.request_id, enums.ReportStatus.ACTIVE.value
                    )
                )
                self.set_report_status(rpt, enums.ReportStatus.ACTIVE)

        if rpt.is_active_or_pending:
            now = datetime.utcnow()
            if rpt.status == enums.ReportStatus.ACTIVE.value:
                if rpt.end_time is None or rpt.end_time > now:
                    rpt_interval = (
                        rpt.interval_secs
                        if rpt.interval_secs is not None
                        else DEFAULT_REPORT_INTERVAL_SECS
                    )
                    next_report_time = rpt.last_report + timedelta(seconds=rpt_interval)
                    if datetime.utcnow() > next_report_time:
                        self.send_oadr_update_report(rpt.id)
                        if rpt_interval == 0:
                            # OADR rule 324: If rpt_interval == 0 it's a one-time report, so set status to COMPLETED.
                            rpt.status = enums.ReportStatus.COMPLETED.value
                else:
                    _LOGGER.debug(
                        "Setting report {} to status {}".format(
                            rpt.request_id, enums.ReportStatus.COMPLETED.value
                        )
                    )
                    self.set_report_status(rpt, enums.ReportStatus.COMPLETED)
            else:
                _activate_report()
        else:
            # Expire reports from the cache if they're completed or canceled.
            _LOGGER.debug("Expiring report {} from cache".format(rpt.request_id))
            self.expire_report(rpt)

    # ***************** Methods for Servicing VTN Requests ********************

    # def push_request(self, env, request):
    #     """Callback. The VTN pushed an http request. Service it."""
    #     _LOGGER.debug("Servicing a VTN push request")
    #     # self.core.spawn(self.service_vtn_request, request)    # **HA**
    #     self.service_vtn_request(request)
    #     # Return an empty response.
    #     return [response_codes.HTTP_STATUS_CODES[204], "", [("Content-Length", "0")]]

    RequestHandler = namedtuple(
        "RequestHandler", ["func", "ei_response", "id_location"]
    )

    RESP_ALWAYS = "always"
    RESP_OPTIONAL = "optional"
    RESP_NEVER = "never"

    LOCATION_ROOT = "root"
    LOCATION_RESPONSE = "ei_response"
    LOCATION_NONE = "none"

    REQUEST_HANDLERS = {
        "oadrDistributeEvent": RequestHandler(
            func="handle_oadr_distribute_event",
            ei_response=RESP_OPTIONAL,
            id_location=LOCATION_ROOT,
        ),
        "oadrRegisterReport": RequestHandler(
            func="handle_oadr_register_report",
            ei_response=RESP_NEVER,
            id_location=LOCATION_NONE,
        ),
        "oadrRegisteredReport": RequestHandler(
            func="handle_oadr_registered_report",
            ei_response=RESP_ALWAYS,
            id_location=LOCATION_RESPONSE,
        ),
        "oadrCreateReport": RequestHandler(
            func="handle_oadr_create_report",
            ei_response=RESP_NEVER,
            id_location=LOCATION_NONE,
        ),
        "oadrUpdatedReport": RequestHandler(
            func="handle_oadr_updated_report",
            ei_response=RESP_ALWAYS,
            id_location=LOCATION_RESPONSE,
        ),
        "oadrCancelReport": RequestHandler(
            func="handle_oadr_cancel_report",
            ei_response=RESP_NEVER,
            id_location=LOCATION_ROOT,
        ),
        "oadrResponse": RequestHandler(
            func="handle_oadr_response",
            ei_response=RESP_ALWAYS,
            id_location=LOCATION_RESPONSE,
        ),
        "oadrCreatedPartyRegistration": RequestHandler(
            func="handle_oadr_created_party_registration",
            ei_response=RESP_ALWAYS,
            id_location=LOCATION_RESPONSE,
        ),
    }

    @staticmethod
    def _find_request_handler(handlers: Dict[str, RequestHandler], signed_object):
        """
        Given a SignedObject from the VTN, return the request handler that tells us
        how to deal with it.
        """
        found = [
            payload_name
            for payload_name in handlers.keys()
            if getattr(signed_object, payload_name)
        ]

        if len(found) == 1:
            payload_name = found[0]
            return payload_name, handlers[payload_name]
        elif len(found) == 0:
            raise exceptions.OpenADRInterfaceException(
                f"Did not recognise payload.  Supported types are {handlers.keys()}",
                response_codes.OADR_NOT_RECOGNISED,
            )
        else:
            raise exceptions.OpenADRInterfaceException(
                f"Too many signedObject elements ({','.join(found)})",
                response_codes.OADR_INVALID_DATA,
            )

    @staticmethod
    def _get_signed_object(request):
        payload = oadr_20b.parseString(request, silence=True)
        signed_object = payload.oadrSignedObject
        if signed_object is None:
            raise exceptions.OpenADRInterfaceException(
                "No SignedObject in payload", response_codes.OADR_BAD_DATA
            )
        return signed_object

    def _check_ei_response(self, request_object, check_type, id_location) -> str:
        """
        An eiResponse can appear in multiple kinds of VTN requests.

        If an eiResponse has been received, check for a '200' (OK) response code.
        If any other code is received, the VTN is reporting an error -- log it and raise an exception.

        :param request_object: The VTN's request object..
        :return: The request ID
        """
        if check_type == self.RESP_ALWAYS or (
            check_type == self.RESP_OPTIONAL and getattr(request_object, "eiResponse")
        ):
            if (
                request_object.eiResponse.responseCode
                != response_codes.OADR_VALID_RESPONSE
            ):
                raise exceptions.OpenADRInternalException(
                    f"Error response from VTN: {request_object.eiResponse.responseCode}"
                    f" {request_object.eiResponse.responseDescription}"
                )

        if id_location == self.LOCATION_NONE:
            return ""
        elif id_location == self.LOCATION_ROOT:
            # OADR rule 41: There are two requestID fields in oadrDistributeEvent.
            # The field that must be populated with a requestID is located
            # at oadrDistributeEvent:requestID.
            return request_object.requestID
        else:
            return request_object.eiResponse.requestID

    def service_vtn_request(self, request: str):
        """
        Handle a payload received from the VTN.

        :param request: The request's XML payload (as a string)
        """
        if self.log_xml:
            xml = etree_.tostring(etree_.fromstring(request), pretty_print=True)
            _LOGGER.debug(f"VTN payload:\n{xml}")

        if self.security_level == "high":
            # At high security, the request is accompanied by a Signature.
            # The VEN should use a certificate authority to validate and decode the request.
            raise NotImplementedError("Security level 'high' is not implemented")

        #  We set this here so that it is defined before the exception handling blocks
        # which rely on it being set to *something*.
        request_id = ""

        try:
            signed_object = self._get_signed_object(request)
            payload_name, handler = self._find_request_handler(
                self.REQUEST_HANDLERS, signed_object
            )
            _LOGGER.debug(f"VTN request: {payload_name} -> {handler.func}")

            # e.g. signed_object.oadrDistributeEvent
            request_object = getattr(signed_object, payload_name)
            request_method = getattr(self, handler.func)

            request_id = self._check_ei_response(
                request_object, handler.ei_response, handler.id_location
            )
            request_method(request_id, request_object)
            if request_object.__class__.__name__ != "oadrResponseType":
                # A non-default response was received from the VTN. Issue a followup poll request.
                self.send_oadr_poll()

        except exceptions.OpenADRInternalException as err:
            _LOGGER.exception(
                f"Internal error when handling VTN request ({err.message})"
            )
        except exceptions.OpenADRInterfaceException as err:
            _LOGGER.warning(
                f"Error processing VTN request ({err.message})", exc_info=True
            )
            # OADR rule 48: Log the validation failure, send an oadrResponse.eiResponse with an error code.
            self.send_oadr_response(
                err.message, err.error_code or response_codes.OADR_BAD_DATA, request_id
            )
        except Exception as err:
            _LOGGER.exception("Unexpected error handling VTN request")
            self.send_oadr_response(str(err), response_codes.OADR_BAD_DATA, request_id)
            raise

    # ***************** Handle Requests from the VTN to the VEN ********************

    def handle_oadr_created_party_registration(
        self, request_id, oadr_created_party_registration
    ):
        """
        The VTN has responded to oadrCreatePartyRegistration
        by sending oadrCreatedPartyRegistration.
        """
        registration = extractors.decode_oadr_created_party_registration(
            oadr_created_party_registration
        )

        self.vtn_id = registration.vtn_id
        self.ven_id = registration.ven_id
        self.poll_interval_secs = registration.poll_interval_secs

    def handle_oadr_distribute_event(self, request_id, oadr_distribute_event):
        """
        The VTN has responded to an oadrPoll by sending an oadrDistributeEvent.

        Create or update an event, then respond with oadrCreatedEvent.

        For sample XML, see test/xml/sample_oadrDistributeEvent.xml.
        """

        vtn_id = oadr_distribute_event.vtnID
        if vtn_id is not None and vtn_id != self.vtn_id:
            raise exceptions.OpenADRInterfaceException(
                "vtnID failed to match agent config: {}".format(vtn_id),
                response_codes.OADR_BAD_DATA,
            )

        oadr_event_list = oadr_distribute_event.oadrEvent
        if len(oadr_event_list) == 0:
            raise exceptions.OpenADRInternalException(
                "oadrDistributeEvent received with no events"
            )

        oadr_event_ids = []
        for oadr_event in oadr_event_list:
            try:
                event = self.handle_oadr_event(request_id, oadr_event)
                if event:
                    oadr_event_ids.append(event.event_id)
            except exceptions.OpenADRInterfaceException as err:
                # OADR rule 19: If a VTN message contains a mix of valid and invalid events,
                # respond to the valid ones. Don't reject the entire message due to invalid events.
                # OADR rule 48: Log the validation failure and send the error code in oadrCreatedEvent.eventResponse.
                # (The oadrCreatedEvent's eiResponse should contain a 200 -- normal -- status code.)
                _LOGGER.warning("Event error: {}".format(err), exc_info=True)

                # Construct a temporary EIEvent to hold data that will be reported in the error return.
                if oadr_event.eiEvent and oadr_event.eiEvent.eventDescriptor:
                    event_id = oadr_event.eiEvent.eventDescriptor.eventID
                    modification_number = (
                        oadr_event.eiEvent.eventDescriptor.modificationNumber
                    )
                else:
                    event_id = None
                    modification_number = None
                with orm.db_session:
                    error_event = database.Event(
                        event_id=event_id,
                        request_id=request_id,
                        modification_number=modification_number,
                    )
                self.send_oadr_created_event(
                    error_event,
                    error_code=err.error_code or response_codes.OADR_BAD_DATA,
                    error_message=err.message,
                )

            except Exception as err:
                _LOGGER.warning(
                    "Unanticipated error during event processing: {}".format(err),
                    exc_info=True,
                )
                self.send_oadr_response(
                    str(err), response_codes.OADR_BAD_DATA, request_id
                )

        self._cancel_events_not_in_recent_event_list(oadr_event_ids)

    @orm.db_session
    def _cancel_events_not_in_recent_event_list(self, oadr_event_ids):
        """
        Implied cancel:

        OADR rule 61: If the VTN request omitted an active event, cancel it.

        Also, think about whether to alert the VTN about this cancellation by sending it an oadrCreatedEvent.
        """
        stored_events = database.Event.select()[:]
        for event in stored_events:
            if event.event_id not in oadr_event_ids:
                _LOGGER.debug(
                    "Event ID {} not in distributeEvent: canceling it.".format(
                        event.event_id
                    )
                )
                self.handle_event_cancellation(event, "never")

    @orm.db_session
    def handle_oadr_event(
        self, request_id, oadr_event: etree_.Element
    ) -> Optional[database.Event]:
        """
        An oadrEvent was received, usually as part of an oadrDistributeEvent.
        Handle the event creation/update.

        Respond with oadrCreatedEvent.

        For sample XML, see test/xml/sample_oadrDistributeEvent.xml.

        :return: the event that was created or updated
        """

        def _calculate_start_offset(event_data):
            # OADR rule 30: Randomize start_time and end_time if start_after is provided.
            if event_data.start_after:
                seconds = event_data.start_after.seconds * random.random()
                return timedelta(seconds=seconds)
            else:
                return timedelta(seconds=0)

        def _calculate_times(event_data, offset) -> Tuple[datetime, datetime]:
            start_time = event_data.official_start + offset

            # An interval with 0 duration has no defined endTime and remains active
            # until canceled.
            if event_data.duration.total_seconds() <= 0.0:
                end_time = None
            else:
                end_time = start_time + event_data.duration

            return start_time, end_time

        @orm.db_session
        def _create_pony_event(
            event_data: extractors.EiEventData, request_id
        ) -> database.Event:
            """Create an Event in the databse."""

            start_offset = _calculate_start_offset(event_data)
            start_time, end_time = _calculate_times(event_data, start_offset)

            pony_event = database.Event(
                event_id=event_data.event_id,
                request_id=request_id,
                status=event_data.status.value,
                modification_number=event_data.modification_number,
                priority=event_data.priority,
                official_start=event_data.official_start,
                duration=event_data.duration,
                start_after=event_data.start_after,
                start_offset=start_offset,
                start_time=start_time,
                end_time=end_time,
                signals=event_data.signals,
                test_event=event_data.test_event,
            )

            return pony_event

        @orm.db_session
        def _update_pony_event(
            new_event_data: extractors.EiEventData, existing_event_id, request_id
        ):
            event = database.Event.get(id=existing_event_id)
            assert _check_modification_number(
                existing_event_mod_number=event.modification_number,
                updated_event_mod_number=new_event_data.modification_number,
            )
            if event.opt_type == enums.OptType.OPT_OUT:
                # TODO: refactor
                # Do nothing if we have opted out of this event
                return
            if new_event_data.status is enums.EventStatus.CANCELED.value:
                if event.status is not enums.EventStatus.CANCELED.value:
                    # OADR rule 59: The event was just canceled. Process an event cancellation.
                    self.handle_event_cancellation(event, response_required)
                    return

            # Only recalculate date-related values if the VTN has changed them.
            #
            # This is because otherwise, every time we re-recieve an event with a
            # start_after (randomisation) value we would re-randomise the start and end
            # times.  Maybe that would be finebut new_event_dataems edge-casey so we avoid it.

            if (
                event.official_start != new_event_data.official_start
                or event.duration != new_event_data.duration
                or event.start_after != new_event_data.start_after
            ):
                event.start_offset = _calculate_start_offset(new_event_data)
                event.start_time, event.end_time = _calculate_times(
                    new_event_data, event.start_offset
                )

            event.event_id = new_event_data.event_id
            event.request_id = request_id
            event.priority = new_event_data.priority
            event.signals = new_event_data.signals
            event.modification_number = new_event_data.modification_number
            event.test_event = new_event_data.test_event
            event.official_start = new_event_data.official_start
            event.duration = new_event_data.duration
            event.start_after = new_event_data.start_after

            # XXX Is there a reason we don't set event.status to the VTN's provided status?

            return event

        def _check_modification_number(
            existing_event_mod_number, updated_event_mod_number
        ):
            if updated_event_mod_number > existing_event_mod_number:
                return True
            if updated_event_mod_number < existing_event_mod_number:
                _LOGGER.debug(
                    f"Out-of-order modification number: {updated_event_mod_number}"
                )
                # OADR rule 58: Respond with error code 450.
                raise exceptions.OpenADRInterfaceException(
                    "Invalid modification number (too low)",
                    response_codes.OADR_MOD_NUMBER_OUT_OF_ORDER,
                )
                return False
            else:
                _LOGGER.debug("No modification number change, taking no action")
                return True

        # Create a temporary EiEvent, constructed from the OadrDistributeEventType.
        ei_event = oadr_event.eiEvent
        response_required = oadr_event.oadrResponseRequired

        if (
            ei_event.eiTarget
            and ei_event.eiTarget.venID
            and self.ven_id not in ei_event.eiTarget.venID
        ):
            # Rule 22: If an eiTarget is furnished, handle the event only if this venID
            # is in the target list.
            return None
        else:
            event_data = extractors.decode_ei_event(ei_event)

            existing_event = database.Event.get(event_id=event_data.event_id)
            if existing_event:

                # if event exists already, check that the modification number has been incremented
                # if it has, update the event
                event = _update_pony_event(event_data, existing_event.id, request_id)
            else:
                # create a new event
                event = _create_pony_event(event_data, request_id)

            if response_required == "always":
                # OADR rule 12, 62: Send an oadrCreatedEvent if response_required == 'always'.
                # OADR rule 12, 62: If response_required == 'never', do not send an oadrCreatedEvent.
                self.send_oadr_created_event(event)

            return event

    @orm.db_session
    def handle_event_cancellation(self, event: database.Event, response_required: str):
        """
        An event was canceled by the VTN. Update local state and publish the news.

        :param event: The event that was cancelled.
        :param response_required: Does the VTN expect a response?  Can be "always" or "never".
        """
        if event.start_after:
            raise NotImplementedError(
                "Event cancellation with start_after not supported"
            )
            # OADR rule 65: If the event has a startAfter value,
            # schedule cancellation for a random future time between now and (now + startAfter).
            max_delay = isodate.parse_duration(event.start_after)  # noqa
            cancel_time = get_aware_utc_now() + timedelta(
                seconds=(max_delay.seconds * random.random())
            )
            cancel_time
            # self.core.schedule(
            #    cancel_time, self._handle_event_cancellation, event, response_required
            # )
        else:
            event.status = enums.EventStatus.CANCELED.value
            if response_required != "never":
                # OADR rule 36: If response_required != never, confirm cancellation with optType = optIn.
                event.optType = event.OPT_TYPE_OPT_IN.value
            self.commit()

    def handle_oadr_register_report(self, request_id, oadr_register_report):
        """
        The VTN is sending METADATA, registering the reports that it can send to the VEN.

        Send no response -- the VEN doesn't want any of the VTN's crumby reports.

        :param request: The VTN's request (unused)
        """
        # OADR rule 301: Sent when the VTN wakes up.
        pass

    def handle_oadr_registered_report(self, request_id, oadr_registered_report):
        """
        The VTN acknowledged receipt of the METADATA in oadrRegisterReport.

        If the VTN requested any reports (by specifier ID), create them.
        Send an oadrCreatedReport acknowledgment for each request.

        :param oadr_registered_report: the oadrRegisteredReportType element
        """
        _LOGGER.debug(
            "Handling oadrRegisteredReport from VTN: {}".format(
                str(oadr_registered_report)
            )
        )
        self.create_or_update_reports(
            oadr_registered_report.oadrReportRequest, request_id
        )

    def handle_oadr_create_report(self, request_id, oadr_create_report):
        """
        Handle an oadrCreateReport request from the VTN.

        The request could have arrived in response to a poll,
        or it could have been part of an oadrRegisteredReport response.

        Create a report for each oadrReportRequest in the list, sending an oadrCreatedReport in response.

        :param oadr_create_report: the oadrCreateReport element
        """

        self.create_or_update_reports(oadr_create_report.oadrReportRequest, None)

    def handle_oadr_updated_report(self, request_id, oadr_updated_report):
        """
        The VTN acknowledged receipt of an oadrUpdatedReport, and may have sent
        a report cancellation.

        Check for report cancellation, and cancel the report if necessary. No need to
        send a response to the VTN.

        :param oadr_updated_report: the oadrUpdatedReport element
        """
        oadr_cancel_report = oadr_updated_report.oadrCancelReport
        if oadr_cancel_report:
            self.cancel_report(
                oadr_cancel_report.reportRequestID,
                acknowledge=False,
                request_id=request_id,
            )

    def handle_oadr_cancel_report(self, request_id, oadr_cancel_report):
        """
        The VTN responded to an oadrPoll by requesting a report cancellation.

        Respond by canceling the report, then send oadrCanceledReport to the VTN.

        :param oadr_cancel_report: the oadrCancelReportType element
        """
        self.cancel_report(
            oadr_cancel_report.reportRequestID, acknowledge=True, request_id=request_id
        )

    def handle_oadr_response(self, request_id, oadr_response):
        """
        The VTN has acknowledged a VEN request such as oadrCreatedReport.

        No response is needed.

        :param oadr_response: The VTN's request.
        """
        pass

    def create_or_update_reports(self, report_list, request_id):
        """
        Process report creation/update requests from the VTN (which could have arrived in different payloads).

        The requests could have arrived in response to a poll,
        or they could have been part of an oadrRegisteredReport response.

        Create/Update reports, and publish info about them on the volttron message bus.
        Send an oadrCreatedReport response to the VTN for each report.

        :param report_list: A iterable of oadrReportRequest. Can be None.
        """

        def get_default_interval(report_specifier, report_params):
            if "report_interval_secs_default" in report_params:
                try:
                    return int(report_params["report_interval_secs_default"])
                except ValueError:
                    raise ValueError(
                        f"Default report interval {report_params['report_interval_secs_default']}"
                        f" for report {report_specifier} is not an integer number of seconds"
                    )
            else:
                return None

        @orm.db_session
        def _create_pony_report(report_request) -> database.Report:
            """ Create a report in the databse."""

            specifier_id = extractors.report_extract_specifier_id(report_request)
            if specifier_id not in self.report_parameters:
                raise exceptions.BadDataError(
                    f"No parameters found for report with specifier ID {specifier_id}"
                )
            report_params = self.report_parameters[specifier_id]

            report = extractors.decode_ei_report(
                eiReport=report_request,
                default_interval=get_default_interval(specifier_id, report_params),
            )

            pony_report = database.Report(
                name=report_params.get("report_name"),
                telemetry_parameters=json.dumps(
                    report_params.get("telemetry_parameters")
                ),
                start_time=report.start_time,
                end_time=report.end_time,
                duration=report.duration,
                interval_secs=report.interval_secs,
                granularity_secs=report.granularity_secs,
                request_id=report.request_id,
                specifier_id=report.specifier_id,
            )
            return pony_report

        @orm.db_session
        def _update_pony_report(new_report_data, existing_report_id):
            """If the report changed, update its parameters in the database"""
            report = database.Report.get(id=existing_report_id)
            report.request_id = new_report_data.request_id
            report.specifier_id = new_report_data.specifier_id
            report.start_time = new_report_data.start_time
            report.end_time = new_report_data.end_time
            report.interval_secs = new_report_data.interval_secs
            return report

        @orm.db_session
        def cancel_rpt(rpt):
            """A report cancellation was received. Process it and notify interested parties."""
            rpt.status = enums.ReportStatus.CANCELED.value

        oadr_report_request_ids = []
        _LOGGER.debug(
            "Processing report creating/update requests from VTN with request id {}".format(
                request_id
            )
        )
        _LOGGER.debug(
            "Processing report creating/update requests from VTN with report list {}".format(
                report_list
            )
        )
        try:
            if report_list:
                for oadr_report_request in report_list:
                    report_data = extractors.decode_ei_report(oadr_report_request)
                    existing_report = self.get_report_for_report_specifier_id(
                        report_data.specifier_id
                    )
                    if existing_report:
                        # if the report already exists, update it
                        _update_pony_report(report_data, existing_report.id)
                    else:
                        _create_pony_report(oadr_report_request)

        #             if temp_report.status == enums.ReportStatus.CANCELED.value:
        #                 if existing_report:
        #                     oadr_report_request_ids.append(temp_report.request_id)
        #                     cancel_rpt(existing_report)
        #                     self.send_oadr_created_report(oadr_report_request)
        #                     _LOGGER.debug(
        #                         "Cancelled an existing report as VTN sent CANCELLED: {}".format(
        #                             existing_report
        #                         ),
        #                         exc_info=True,
        #                     )
        #                 else:
        #                     # Received notification of a new report, but it's already canceled. Take no action.
        #                     _LOGGER.debug(
        #                         "Received notification of a new report, but it's already canceled. Take no action.: {}".format(
        #                             existing_report
        #                         ),
        #                         exc_info=True,
        #                     )
        #             else:
        #                 oadr_report_request_ids.append(temp_report.request_id)

        #                 if temp_report.report_specifier_id == "METADATA":
        #                     # Rule 301/327: If the request's specifierID is 'METADATA', send an oadrRegisterReport.
        #                     self.send_oadr_created_report(oadr_report_request)
        #                     self.send_oadr_register_report()
        #                     _LOGGER.debug(
        #                         "Report was METADATA report, acknowledging registration to VTN: ".format(
        #                             temp_report
        #                         ),
        #                         exc_info=True,
        #                     )
        #                 elif existing_report:
        #                     update_rpt(temp_report, existing_report)
        #                     self.send_oadr_created_report(oadr_report_request)
        #                     _LOGGER.debug(
        #                         "Report already exists, updating with : ".format(
        #                             temp_report
        #                         ),
        #                         exc_info=True,
        #                     )
        #                 else:
        #                     create_rpt(temp_report)
        #                     self.send_oadr_created_report(oadr_report_request)
        #                     _LOGGER.debug(
        #                         "Report does not exist, creating : ".format(
        #                             temp_report
        #                         ),
        #                         exc_info=True,
        #                     )
        except exceptions.OpenADRInterfaceException as err:
            # If a VTN message contains a mix of valid and invalid reports, respond to the valid ones.
            # Don't reject the entire message due to an invalid report.
            _LOGGER.warning("Report error: {}".format(err), exc_info=True)
            self.send_oadr_response(
                err.message, err.error_code or response_codes.OADR_BAD_DATA, request_id
            )
        except Exception as err:
            _LOGGER.warning(
                "Unanticipated error during report processing: {}".format(err),
                exc_info=True,
            )
            self.send_oadr_response(str(err), response_codes.OADR_BAD_DATA, request_id)

        all_active_reports = self._get_reports()
        for agent_report in all_active_reports:
            if agent_report.request_id not in oadr_report_request_ids:
                # If the VTN's request omitted an active report, treat it as an implied cancellation.
                report_request_id = agent_report.request_id
                _LOGGER.debug(
                    "Report request ID {} not sent by VTN, canceling the report.".format(
                        report_request_id
                    )
                )
                self.cancel_report(
                    report_request_id, acknowledge=True, request_id=request_id
                )

    def cancel_report(
        self, report_request_id: str, request_id: str, acknowledge: bool = False
    ):
        """
        The VTN asked to cancel a report, in response to either report telemetry or an oadrPoll. Cancel it.

        :param report_request_id: The report_request_id of the report to be canceled.
        :param acknowledge: If True, send an oadrCanceledReport acknowledgment to the VTN.
        """
        if report_request_id is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing oadrCancelReport.reportRequestID", response_codes.OADR_BAD_DATA
            )
        report = self.get_report_for_report_request_id(report_request_id)
        if report:
            report.status = enums.ReportStatus.CANCELED.value
            self.commit()
            if acknowledge:
                self.send_oadr_canceled_report(report_request_id, request_id)
        else:
            # The VEN got asked to cancel a report that it doesn't have. Do nothing.
            pass

    # ***************** Send Requests from the VEN to the VTN ********************

    def send_oadr_poll(self):
        """Send oadrPoll to the VTN."""
        _LOGGER.debug("VEN: oadrPoll")
        # OADR rule 37: The VEN must support the PULL implementation.
        self._last_poll = get_aware_utc_now()
        builder = builders.OadrPollBuilder(ven_id=self.ven_id)
        self.send_vtn_request(POLL, "oadrPoll", builder.build())

    def send_oadr_query_registration(self):
        """Send oadrQueryRegistration to the VTN."""
        _LOGGER.debug("VEN: oadrQueryRegistration")
        builder = builders.OadrQueryRegistrationBuilder()
        self.send_vtn_request(EIREGISTERPARTY, "oadrQueryRegistration", builder.build())

    def send_oadr_create_party_registration(self, ven_name):
        """Send oadrCreatePartyRegistration to the VTN."""
        _LOGGER.debug("VEN: oadrCreatePartyRegistration")
        send_signature = self.security_level == "high"
        # OADR rule 404: If the VEN hasn't registered before, venID and registrationID should be empty.
        builder = builders.OadrCreatePartyRegistrationBuilder(
            ven_id=None, xml_signature=send_signature, ven_name=ven_name
        )
        self.send_vtn_request(
            EIREGISTERPARTY, "oadrCreatePartyRegistration", builder.build()
        )

    def send_oadr_request_event(self):
        """Send oadrRequestEvent to the VTN."""
        _LOGGER.debug("VEN: oadrRequestEvent")
        builder = builders.OadrRequestEventBuilder(ven_id=self.ven_id)
        self.send_vtn_request(EIEVENT, "oadrRequestEvent", builder.build())

    def send_oadr_created_event(
        self, event: database.Event, error_code: str = None, error_message: str = None
    ):
        """
        Send oadrCreatedEvent to the VTN.

        :param event: The event that is the subject of the request.
        :param error_code: eventResponse error code. Used when reporting event protocol errors.
        :param error_message: eventResponse error message. Used when reporting event protocol errors.
        """
        _LOGGER.debug("VEN: oadrCreatedEvent")
        builder = builders.OadrCreatedEventBuilder(
            event=event,
            ven_id=self.ven_id,
            error_code=error_code,
            error_message=error_message,
        )
        self.send_vtn_request(EIEVENT, "oadrCreatedEvent", builder.build())

    def send_oadr_register_report(self):
        """
        Send oadrRegisterReport (METADATA) to the VTN.

        Sample oadrRegisterReport from the OpenADR Program Guide:

            <oadr:oadrRegisterReport ei:schemaVersion="2.0b">
                <pyld:requestID>RegReq120615_122508_975</pyld:requestID>
                <oadr:oadrReport>
                    --- See oadr_report() ---
                </oadr:oadrReport>
                <ei:venID>ec27de207837e1048fd3</ei:venID>
            </oadr:oadrRegisterReport>
        """
        _LOGGER.debug("VEN: oadrRegisterReport")
        # The VEN is currently hard-coded to support the 'telemetry' report, which sends baseline and measured power,
        # and the 'telemetry_status' report, which sends online and manual_override status.
        # In order to support additional reports and telemetry types, the VEN would need to store other data elements
        # as additional columns in its SQLite database.

        builder = builders.OadrRegisterReportBuilder(
            reports=self.metadata_reports(), ven_id=self.ven_id
        )
        # The EPRI VTN server responds to this request with "452: Invalid ID". Why?
        self.send_vtn_request(EIREPORT, "oadrRegisterReport", builder.build())

    @orm.db_session
    def send_oadr_update_report(self, report_id: int):
        """
        Send telemetry for a given report to the VTN using oadrUpdateReport.

        Sample oadrUpdateReport from the OpenADR Program Guide:

            <oadr:oadrUpdateReport ei:schemaVersion="2.0b">
                <pyld:requestID>ReportUpdReqID130615_192730_445</pyld:requestID>
                <oadr:oadrReport>
                    --- See OadrUpdateReportBuilder ---
                </oadr:oadrReport>
                <ei:venID>VEN130615_192312_582</ei:venID>
            </oadr:oadrUpdateReport>
        """
        report = database.Report.get(id=report_id)
        _LOGGER.debug("VEN: oadrUpdateReport (report {})".format(report.request_id))
        self.oadr_current_service = EIREPORT
        telemetry = self.get_new_telemetry_for_report(report.specifier_id)
        _LOGGER.debug("VEN: sending telemetry {}".format(telemetry))
        builder = builders.OadrUpdateReportBuilder(
            report=report,
            telemetry=telemetry,
            online=self.ven_online,
            manual_override=self.ven_manual_override,
            ven_id=self.ven_id,
        )
        self.send_vtn_request(EIREPORT, "oadrUpdateReport", builder.build())
        report.last_report = datetime.utcnow()

    def send_oadr_created_report(self, report_request):
        """
            Send oadrCreatedReport to the VTN.

        @param report_request: (oadrReportRequestType) The VTN's report request.
        """
        _LOGGER.debug("VEN: oadrCreatedReport")
        builder = builders.OadrCreatedReportBuilder(
            report_request_id=report_request.reportRequestID,
            ven_id=self.ven_id,
            pending_report_request_ids=self.get_pending_report_request_ids(),
        )
        self.send_vtn_request(EIREPORT, "oadrCreatedReport", builder.build())

    def send_oadr_canceled_report(self, report_request_id, request_id):
        """
            Send oadrCanceledReport to the VTN.

        @param report_request_id: (string) The reportRequestID of the report that has been canceled.
        """
        _LOGGER.debug("VEN: oadrCanceledReport")
        builder = builders.OadrCanceledReportBuilder(
            request_id=request_id,
            report_request_id=report_request_id,
            ven_id=self.ven_id,
            pending_report_request_ids=self.get_pending_report_request_ids(),
        )
        self.send_vtn_request(EIREPORT, "oadrCanceledReport", builder.build())

    def send_oadr_response(
        self, description: str, code: str, request_id: Optional[str]
    ):
        """
        Send an oadrResponse to the VTN.
        """
        _LOGGER.debug("VEN: oadrResponse")
        builder = builders.OadrResponseBuilder(
            response_code=code,
            response_description=description,
            request_id=request_id or "0",
            ven_id=self.ven_id,
        )
        self.send_vtn_request(POLL, "oadrResponse", builder.build())

    def send_vtn_request(self, service, request_name, request_object):
        """
            Send a request to the VTN. If the VTN returns a non-empty response, service that request.

            Wrap the request in a SignedObject and then in Payload XML, and post it to the VTN via HTTP.
            If using high security, calculate a digital signature and include it in the request payload.

        @param request_name: (string) The name of the SignedObject attribute where the request is attached.
        @param request_object: (various oadr object types) The request to send.
        """
        signed_object = oadr_20b.oadrSignedObject(**{request_name: request_object})
        try:
            # Export the SignedObject as an XML string.
            buff = StringIO()
            signed_object.export(buff, 1, pretty_print=True)
            signed_object_serialised_xml = buff.getvalue()
        except Exception as err:
            raise exceptions.OpenADRInterfaceException(
                "Error exporting the SignedObject: {}".format(err), None
            )

        if self.security_level == "high":
            try:
                signature_lxml, signed_object_lxml = self.calculate_signature(
                    signed_object_serialised_xml
                )
            except Exception as err:
                raise exceptions.OpenADRInterfaceException(
                    "Error signing the SignedObject: {}".format(err), None
                )
            payload_lxml = self.payload_element(signature_lxml, signed_object_lxml)
            try:
                # Verify that the payload, with signature, is well-formed and can be validated.
                signxml.XMLVerifier().verify(payload_lxml, ca_pem_file=self.vtn_ca_cert)
            except Exception as err:
                raise exceptions.OpenADRInterfaceException(
                    "Error verifying the SignedObject: {}".format(err), None
                )
        else:
            signed_object_lxml = etree_.fromstring(signed_object_serialised_xml)
            payload_lxml = self.payload_element(None, signed_object_lxml)

        if self.log_xml:
            _LOGGER.debug("VEN PAYLOAD:")
            _LOGGER.debug(
                "\n{}".format(etree_.tostring(payload_lxml, pretty_print=True))
            )

        # Post payload XML to the VTN as an HTTP request. Return the VTN's response, if any.
        endpoint = self.vtn_address + service
        payload_xml = etree_.tostring(payload_lxml)
        # OADR rule 53: If simple HTTP mode is used, send the following headers: Host, Content-Length, Content-Type.
        # The EPRI VTN server responds with a 400 "bad request" if a "Host" header is sent.
        _LOGGER.debug("Posting VEN request to {}".format(endpoint))

        try:
            payload_xml = etree_.tostring(payload_lxml)
            # OADR rule 53: If simple HTTP mode is used, send the following headers: Host, Content-Length, Content-Type.
            # The EPRI VTN server responds with a 400 "bad request" if a "Host" header is sent.
            _LOGGER.debug("Posting VEN request to {}".format(endpoint))
            response = requests.post(
                endpoint,
                cert=self.client_pem_bundle,
                data=payload_xml,
                headers={
                    # "Host": endpoint,
                    "Content-Length": str(len(payload_xml)),
                    "Content-Type": "application/xml",
                },
            )
            http_code = response.status_code
            if http_code == 200:
                if len(response.content) > 0:
                    self.service_vtn_request(response.content)
                else:
                    _LOGGER.warning("Received zero-length request from VTN")
            elif http_code == 204:
                # Empty response received. Take no action.
                _LOGGER.debug("Empty response received from {}".format(endpoint))
            else:
                _LOGGER.error(
                    "Error in http request to {}: response={}".format(
                        endpoint, http_code
                    ),
                    exc_info=True,
                )
                raise exceptions.OpenADRInterfaceException(
                    "Error in VTN request: {}".format(http_code)
                    + ":"
                    + str(response.content),
                    None,
                )
        except ConnectionError:
            _LOGGER.warning(
                "ConnectionError in http request to {} (is the VTN offline?)".format(
                    endpoint
                )
            )
            return None
        except Exception as err:
            raise exceptions.OpenADRInterfaceException(
                "Error posting OADR XML: {}".format(err), None
            )

    # ***************** Event database Requests ********************
    @property
    @orm.db_session
    def unresponded_events(self) -> List[database.Event]:
        return orm.select(
            e for e in database.Event if e.status == enums.EventStatus.UNRESPONDED.value
        )[:]

    @property
    @orm.db_session
    def near_events(self) -> List[database.Event]:
        return orm.select(
            e for e in database.Event if e.status == enums.EventStatus.NEAR.value
        )[:]

    @property
    @orm.db_session
    def far_events(self) -> List[database.Event]:
        return orm.select(
            e for e in database.Event if e.status == enums.EventStatus.FAR.value
        )[:]

    @property
    @orm.db_session
    def active_events(self) -> List[database.Event]:
        """Return a list of events that are currently in progress
           status is active.
        """
        query = orm.select(
            e for e in database.Event if e.status == enums.EventStatus.ACTIVE.value
        )
        query = query.filter(
            lambda event: event.opt_type != enums.OptType.OPT_OUT.value
        )
        return query[:]

    @property
    def active_or_pending_events(self) -> List[database.Event]:
        """ Returns active or pending events, in the sequence
        active, near, far, unresponded"""
        events: List[database.Event] = []
        if self.active_events:
            events += self.active_events
        if self.near_events:
            events += self.near_events
        if self.far_events:
            events += self.far_events
        if self.unresponded_events:
            events += self.unresponded_events
        return events

    @property
    def is_event_in_progress(self) -> bool:
        """ Is an event in progress? """
        return len(self.active_events) > 0

    @orm.db_session
    def get_event_for_id(self, event_id: str) -> Optional[database.Event]:
        """ Query the DB for the event with the given ID """
        return database.Event.get(event_id=event_id)

    @orm.db_session
    def _set_event_status(self, event_id, status_enum: enums.EventStatus):

        """
        Transition an event from its existing status to a new one.

        :raises exceptions.InvalidStatusException:
        """
        event = self.get_event_for_id(event_id)
        if not isinstance(status_enum, enums.EventStatus):
            raise exceptions.InvalidStatusException(
                "status provided is not a valid EventStatus"
            )
        if status_enum == enums.EventStatus.ACTIVE:
            if event.opt_type != enums.OptType.OPT_IN.value:
                raise exceptions.InvalidStatusException(
                    "can't transition status to ACTIVE if event not opted in"
                )
        _LOGGER.debug(
            f"Transitioning status to {status_enum} for event ID {event.event_id}"
        )
        event.status = status_enum.value

    @property
    @orm.db_session
    def active_reports(self) -> List[database.Report]:
        query = orm.select(
            r for r in database.Report if r.status == enums.ReportStatus.ACTIVE.value
        )
        return query[:]

    @property
    @orm.db_session
    def inactive_reports(self) -> List[database.Report]:
        query = orm.select(
            r for r in database.Report if r.status == enums.ReportStatus.INACTIVE.value
        )
        return query[:]

    @property
    def active_or_pending_reports(self) -> List[database.Report]:
        """Return a list of reports that are neither COMPLETED nor CANCELED."""
        reports: List[database.Report] = []
        if self.active_reports:
            reports += self.active_reports
        if self.inactive_reports:
            reports += self.inactive_reports

        return reports

    @orm.db_session
    def add_report(self, report):
        """A new report has been created. Add it to the database."""
        _LOGGER.warning("ADDING A REPORT!!!!!")
        database.Report(report)

    @orm.db_session
    def set_report_status(self, report: database.Report, status: enums.ReportStatus):
        _LOGGER.debug(
            "Transitioning status to {} for report request ID {}".format(
                status, report.request_id
            )
        )
        report.status = status.value

    def expire_report(self, report):
        """Remove the report from the report cache. (It remains in the SQLite database.)"""
        self._active_reports.pop(report.report_request_id)

    @orm.db_session
    def get_report_for_report_request_id(
        self, report_request_id: str
    ) -> Optional[database.Report]:
        """Return the Report with request ID report_request_id, or None if not found."""
        return database.Report.get(request_id=report_request_id)

    @orm.db_session
    def get_report_for_report_specifier_id(
        self, specifier_id: str
    ) -> Optional[database.Report]:
        """Return the Report with specifier ID specifier_id, or None if not found."""
        return database.Report.get(specifier_id=specifier_id)

    def get_pending_report_request_ids(self):
        """Return a list of reportRequestIDs for each active report."""
        # OpenADR rule 329: Include all current report request IDs in the oadrPendingReports list.
        return [r.report_request_id for r in self._get_reports()]

    def _get_reports(
        self,
        report_request_id: str = None,
        report_specifier_id: str = None,
        active_only: bool = True,
        started_after: datetime = None,
        end_time_before: datetime = None,
    ) -> List[models.EiReport]:
        """
        Return a list of reports in our in-agent database, filtered in various ways.

        By default, return only report requests with status=active.
        """
        # For requests by report ID, query the cache first before querying the database.
        if report_request_id:
            report = self._active_reports.get(report_request_id, None)
            if report:
                return [report]

        reports: Iterable[models.EiReport] = self.EiReports
        if report_request_id is not None:
            reports = filter(
                lambda x: x.report_request_id == report_request_id, reports
            )
        if report_specifier_id is not None:
            reports = filter(
                lambda x: x.report_specifier_id == report_specifier_id, reports
            )
        if active_only:
            reports = filter(
                lambda x: x.status
                not in [
                    enums.ReportStatus.COMPLETED.value,
                    enums.ReportStatus.CANCELED.value,
                ],
                reports,
            )
        if started_after:
            reports = filter(lambda x: x.start_time > started_after, reports)
        if end_time_before:
            # A report's end_time can be None, indicating that it doesn't expire until Canceled.
            # If the report's end_time is None, don't apply this filter to it.
            reports = filter(
                lambda x: x.end_time < end_time_before if x.end_time else True, reports
            )
        return list(reports)

    def metadata_reports(self):
        """Return an EiReport instance containing telemetry metadata for each report definition in agent config."""
        return [
            self.metadata_report(rpt_name) for rpt_name in self.report_parameters.keys()
        ]

    @orm.db_session
    def metadata_report(self, specifier_id):
        """Return an EiReport instance for the indicated specifier_id, or None if its' not in agent config."""
        params = self.report_parameters.get(specifier_id, None)
        # No requestID, no reportRequestID
        report = database.Report(request_id="", specifier_id=specifier_id)
        report.name = params.get("report_name_metadata", None)
        try:
            interval_secs = int(params.get("report_interval_secs_default", None))
        except ValueError:
            error_msg = "Default report interval {} is not an integer number of seconds".format(
                params.get("report_interval_secs_default")
            )
            raise exceptions.OpenADRInternalException(error_msg)
        report.interval_secs = interval_secs
        report.telemetry_parameters = json.dumps(
            params.get("telemetry_parameters", None)
        )
        report.report_specifier_id = specifier_id
        report.status = enums.ReportStatus.INACTIVE.value
        return report

    @orm.db_session
    def get_new_telemetry_for_report(
        self, report_specifier_id: str
    ) -> List[database.TelemetryValues]:
        """Query for relevant telemetry that's arrived since the report was last sent to the VTN."""
        report = database.Report(specifier_id=report_specifier_id)
        telemetry = orm.select(
            t
            for t in database.TelemetryValues
            if t.report_specifier_id == report.specifier_id
        )
        telemetry = telemetry.filter(lambda t: t.created > report.last_report)
        return list(telemetry)

    @orm.db_session
    def add_telemetry_json(
        self, report_specifier_id: str, values: Dict, start_time=None, end_time=None
    ):

        """New telemetry (JSON) has been received. Add it to the database."""
        if self.report_parameters[report_specifier_id] is None:
            raise exceptions.BadDataError(
                f"No parameters found for report with specifier ID {report_specifier_id}\n"
                + "Registered reports are: "
                + str(self.report_parameters.keys())
            )
        telemetry = database.TelemetryValues(
            report_specifier_id=report_specifier_id,
            start_time=start_time,
            end_time=end_time,
            values=json.dumps(values),
        )
        return telemetry

    def telemetry_cleanup(self):
        """gevent thread for periodically deleting week-old telemetry from the database."""
        telemetry = self.EiTelemetryValuess
        total_rows = len(telemetry)
        self.EiTelemetryValuess = list(
            filter(
                lambda x: x.created_on > get_aware_utc_now() - timedelta(days=7),
                telemetry,
            )
        )
        deleted_row_count = total_rows - len(self.EiTelemetryValuess)
        if deleted_row_count:
            _LOGGER.debug(
                "Deleting {} outdated of {} total telemetry rows in db".format(
                    deleted_row_count, total_rows
                )
            )
        self.commit()

    # ***************** Utility Methods ********************

    @staticmethod
    def payload_element(
        signature_lxml: Optional[etree_.Element], signed_object_lxml: etree_.Element
    ) -> etree_.Element:
        """
            Construct and return an XML element for Payload.

            Append a child Signature element if one is provided.
            Append a child SignedObject element.

        :param signature_lxml: Signature element.
        :param signed_object_lxml: SignedObject element.
        :return: Payload element.
        """
        payload = etree_.Element(
            "{http://openadr.org/oadr-2.0b/2012/07}oadrPayload",
            nsmap=signed_object_lxml.nsmap,
        )
        if signature_lxml:
            payload.append(signature_lxml)
        payload.append(signed_object_lxml)
        return payload

    @staticmethod
    def calculate_signature(
        self, serialised_xml: str
    ) -> Tuple[etree_.Element, etree_.Element]:
        """
        Calculate a digital signature for the SignedObject to be sent to the VTN.

        Returns a tuple of
            1. An object representing the root of the XML tree containing the signature and the payload data.
            2. The XML tree parsed from serialised_xml
        """

        private_key, certificate = pem.parse_file(self.client_pem_bundle)
        xml_tree = etree_.fromstring(serialised_xml)
        xml_tree.set("Id", "signedObject")
        # Use XMLSigner to create a Signature.
        # Use "detached method": the signature lives alonside the signed object in the XML element tree.
        # Use c14n "exclusive canonicalization": the signature is independent of namespace inclusion/exclusion.
        signer = signxml.XMLSigner(
            method=signxml.methods.detached,
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
        )
        signature_root = signer.sign(
            xml_tree,
            key=private_key.as_bytes(),
            cert=certificate.as_bytes(),
            key_name="123",
        )
        # This generated Signature lacks the ReplayProtect property described in
        # OpenADR profile spec section 10.6.3.
        return signature_root, xml_tree

    def json_object(self, obj):
        """Ensure that an object is valid JSON by dumping it with json_converter and then reloading it."""
        obj_string = json.dumps(obj, default=self.json_converter)
        obj_json = json.loads(obj_string)
        return obj_json

    @staticmethod
    def json_converter(object_to_dump):
        """When calling json.dumps, convert datetime instances to strings."""
        if isinstance(object_to_dump, datetime):
            return object_to_dump.__str__()
