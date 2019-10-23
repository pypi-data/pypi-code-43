import base64
import datetime
import gzip
import json
import os
import platform
import sys
import uuid

from multiprocessing import Pool

import click
import requests

from .cloudformation import SUCCESSFUL_TERMINAL_STATES as CFN_SUCCESSFUL_TERMINAL_STATES
from .config import (
    TELEMETRY_URL,
    TELEMETRY_USER_AGENT,
    TELEMETRY_DISABLE_ENVVAR_NAME,
    TELEMETRY_CLIENT_TYPE,
    TELEMETRY_CLIENT_VERSION,
    TELEMETRY_SCHEMA_VERSION,
    get_cross_session_id
)


def now_str():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()


def send_mp(data):
    requests.post(TELEMETRY_URL, json=data, headers={'User-Agent': TELEMETRY_USER_AGENT})


def mute_stdout_and_stderr():
    sys.stderr = open(os.devnull, 'w')
    sys.stdout = open(os.devnull, 'w')

class SessionLog:
    def __init__(self, disable_metrics=False):

        self.mixpanel_enabled = not disable_metrics
        self.session_id = str(uuid.uuid4())
        self.cross_session_id = get_cross_session_id()
        self.event_log = [{
            "event": "start",
            "event_detail": f"session_id: {self.session_id}",
            "timestamp": now_str()
        }]

    def __enter__(self):
        self.pool = Pool(1, initializer=mute_stdout_and_stderr)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.close()

        if exc_type == click.exceptions.Abort:
            print("\n")
            print("Aborted!")
            return True  # Returning True suppresses the normal exception raising flow and ugly traceback

    def add_event(self, event):
        assert self._is_valid_event(event)
        self.event_log.append(event)

    def dump_base64(self):
        return str(base64.b64encode(gzip.compress(json.dumps(self.event_log).encode("utf-8"))))

    @classmethod
    def decode_base64(cls, b64_encoded_sessionlog):
        return json.loads(gzip.decompress(base64.b64decode(b64_encoded_sessionlog)).decode("utf-8"))

    def send_action_event(self, action_name, action_detail=None):
        if not self.mixpanel_enabled:
            return
        data = {
            'telemetry_schema_version': TELEMETRY_SCHEMA_VERSION,
            'session_id': self.session_id,
            'cross_session_id': self.cross_session_id,
            'client_type': TELEMETRY_CLIENT_TYPE,
            'client_version': TELEMETRY_CLIENT_VERSION,
            'action': action_name,
            'action_detail': action_detail,
            'platform': sys.platform,
            'python_implementation': platform.python_implementation(),
            'python_version_major': platform.python_version_tuple()[0],
            'python_version_minor': platform.python_version_tuple()[1],
            'python_version_patch': platform.python_version_tuple()[2]
        }
        self.pool.apply_async(send_mp, [data])


    def log_start(self, config_file_version, config_schema_version, template_url):
        t = now_str()

        action_name = f"Start installer (config file version)"
        self.event_log.append({"event": action_name, "event_detail": config_file_version, "timestamp": t})
        self.send_action_event(action_name, action_detail=config_file_version)

        action_name = f"Start installer (config file schema version)"
        self.event_log.append({"event": action_name, "event_detail": config_schema_version, "timestamp": t})
        self.send_action_event(action_name, action_detail=config_schema_version)

        action_name = f"Start installer (template url)"
        self.event_log.append({"event": action_name, "event_detail": template_url, "timestamp": t})
        self.send_action_event(action_name, action_detail=template_url)

    def log_valid_param_set_event(self, param_name):
        action_name = f"Set Valid Param: {param_name}"
        self.event_log.append({
            "event": action_name,
            "event_detail": None,
            "timestamp": now_str()
        })
        self.send_action_event(action_name)

    def log_cfn_event(self, logical_resource_id, resource_status, resource_status_reason, timestamp):

        action_name = f"CFN Stack Creation Event: {logical_resource_id} | {resource_status}"
        if resource_status_reason is not None:
            action_name += f" | {resource_status_reason}"
        self.event_log.append({
            "event": action_name,
            "event_detail": resource_status_reason,
            "timestamp": timestamp.replace(microsecond=0).isoformat()
        })
        self.send_action_event(action_name)

    def log_cfn_stack_reached_terminal_state(self, terminal_status, detail):
        outcome_str = "successfully" if terminal_status in CFN_SUCCESSFUL_TERMINAL_STATES else "unsuccessfully"
        action_name = f"CFN stack finished {outcome_str} - {terminal_status}"
        self.event_log.append({
            "event": action_name,
            "event_detail": detail,
            "timestamp": now_str()
        })
        self.send_action_event(action_name)

    @staticmethod
    def _is_valid_event(event):
        assert len(event.keys()) == 3
        assert "event" in event.keys()
        assert "event_detail" in event.keys()
        assert "timestamp" in event.keys()



