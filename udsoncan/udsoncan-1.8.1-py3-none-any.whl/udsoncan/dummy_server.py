from udsoncan import services, Request, Response
from udsoncan.connections import *
import struct
import time

conn = IsoTPConnection('vcan0', rxid=0x456, txid=0x123)
with conn.open():
    while True:
        payload = conn.wait_frame(timeout=None)
        if payload is not None:
            req = Request.from_payload(payload)
            response = Response(req.service, Response.Code.GeneralReject)

            # DiagnosticSessionControl
            if req.service == services.DiagnosticSessionControl:
                if req.subfunction == services.DiagnosticSessionControl.Session.extendedDiagnosticSession:
                    response = Response(
                        req.service, Response.Code.PositiveResponse, data=b'\x03')
                else:
                    response = Response(
                        req.service, Response.Code.SubFunctionNotSupported)

            # SecurityAccess
            elif req.service == services.SecurityAccess:
                if req.subfunction == 3:
                    response = Response(
                        req.service, Response.Code.PositiveResponse, data=b"\x03\x12\x34\x56\x78")
                elif req.subfunction == 4:
                    if req.data == b"\xed\xcb\xa9\x87":
                        response = Response(
                            req.service, Response.Code.PositiveResponse, data=b'\x04')
                    else:
                        response = Response(
                            req.service, Response.Code.InvalidKey)
                else:
                    response = Response(
                        req.service, Response.Code.SubFunctionNotSupported)
            # Tester present
            elif req.service == services.TesterPresent:
                response = Response(
                    req.service, Response.Code.PositiveResponse)

            # Read Data By identifier
            elif req.service == services.ReadDataByIdentifier:

                if req.data == b"\x00\x01":
                    response = Response(
                        req.service, Response.Code.PositiveResponse, data=b'\x00\x01\x12\x34')
                elif req.data == b"\x00\x02":
                    response = Response(
                        req.service, Response.Code.PositiveResponse, data=b'\x00\x02\x56\x78')
                elif req.data == b"\x00\x03":
                    response = Response(
                        req.service, Response.Code.PositiveResponse, data=b'\x00\x03\x9a\xbc')
                elif req.data == b"\x00\x01\x00\x02\x00\x03":
                    response = Response(req.service, Response.Code.PositiveResponse,
                                        data=b'\x00\x01\x12\x34\x00\x02\x56\x78\x00\x03\x9A\xBC\xDE\x0F')
                else:
                    response = Response(
                        req.service, Response.Code.RequestOutOfRange)

            # Write Data By identifier
            elif req.service == services.WriteDataByIdentifier:
                if req.data[0:2] in [b"\x00\x01", b"\x00\x02", b"\x00\x03", b'\xF1\x90']:
                    response = Response(
                        req.service, Response.Code.PositiveResponse, req.data[0:2])
                else:
                    response = Response(
                        req.service, Response.Code.RequestOutOfRange)

            elif req.service == services.ECUReset:
                if req.subfunction in [1, 2]:
                    response = Response(
                        req.service, Response.Code.PositiveResponse, data=struct.pack('B', req.subfunction))
                else:
                    response = Response(
                        req.service, Response.Code.SubFunctionNotSupported)

            else:
                response = Response(
                    req.service, Response.Code.ServiceNotSupported)

            if not response.positive or not req.suppress_positive_response:
                conn.send(response)
            else:
                print("Suppressing positive response.")
