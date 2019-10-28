# -*- coding: utf-8 -*-
from .commonsocket import CommonSocket
from drummer.messages import Response
from drummer.errors import Errors

class SocketClient(CommonSocket):

    def __init__(self, config):

        super().__init__(config)

    def send_request(self, request):

        # init socket
        sock = self.sock
        server_address = self.server_address
        MSG_LEN = self.MSG_LEN

        # establish a connection
        try:
            sock.connect(server_address)

        except ConnectionRefusedError as e:
            raise ConnectionRefusedError(Errors.E0300)

        except Exception:
            raise ConnectionError(Errors.E0201)

        try:
            # encode and send request
            encoded_request = request.encode(MSG_LEN)

            res = sock.sendall(encoded_request)
            if res:
                raise ConnectionError(Errors.E0202)

            # get data from server and decode
            encoded_response = self.receive_data(sock)

            response = Response.decode(encoded_response)

        except:
            raise ConnectionError(Errors.E0202)

        finally:
            # close connection
            sock.close()

        return response

    def get_response(self, sock):

        response = b''
        receiving = True
        while receiving:

            new_data = sock.recv(self.MSG_LEN)
            if new_data:
                response += new_data
            else:
                receiving = False

        return response
