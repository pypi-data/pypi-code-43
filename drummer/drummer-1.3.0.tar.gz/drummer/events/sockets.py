# -*- coding: utf-8 -*-
from drummer.messages import Response, StatusCode, FollowUp

class SocketTestEvent:
    """Simple event to check socket connection."""

    def __init__(self, config):
        self.config = config

    def execute(self, request):
        """Performs a socket connection test."""

        config = self.config

        response = Response()

        follow_up = FollowUp(None)

        try:
            response.set_status(StatusCode.STATUS_OK)

        except Exception:
            response.set_status(StatusCode.STATUS_ERROR)

        return response, follow_up
