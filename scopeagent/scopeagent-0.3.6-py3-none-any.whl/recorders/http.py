import gzip
import io
import logging
import uuid

import certifi
import msgpack
import urllib3

from .asyncrecorder import AsyncRecorder
from ..formatters.dict import DictFormatter

logger = logging.getLogger(__name__)


class HTTPRecorder(AsyncRecorder):
    def __init__(self, api_key, api_endpoint, metadata=None, dry_run=False, **kwargs):
        super(HTTPRecorder, self).__init__(**kwargs)
        self._api_key = api_key
        self._ingest_endpoint = "%s/%s" % (api_endpoint, 'api/agent/ingest')
        self.metadata = metadata or {}
        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        self.dry_run = dry_run

    def flush(self, spans):
        payload = {
            "metadata": self.metadata,
            "spans": [],
            "events": [],
        }

        # TODO: limit number of objects sent per request
        for span in spans:
            span_dict = DictFormatter.dumps(span)
            events = span_dict.pop('logs')
            payload['spans'].append(span_dict)
            span_context = span_dict['context']
            for event in events:
                event['context'] = {
                    'trace_id': span_context['trace_id'],
                    'span_id': span_context['span_id'],
                    'event_id': str(uuid.uuid4()),
                }
                payload['events'].append(event)
        self._send(payload)

    def _send(self, body):
        from .. import version
        payload_msgpack = msgpack.dumps(body, default=lambda value: str(value))
        logger.debug("uncompressed msgpack payload size is %d bytes", len(payload_msgpack))
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="wb") as f:
            f.write(payload_msgpack)
        payload_gzip = out.getvalue()
        logger.debug("compressed gzip payload size is %d bytes", len(payload_gzip))

        headers = {
            "User-Agent": "scope-agent-python/%s" % version,
            "Content-Type": "application/msgpack",
            "X-Scope-ApiKey": self._api_key,
            "Content-Encoding": "gzip",
        }
        if not self.dry_run:
            resp = self.http.request('POST', self._ingest_endpoint,
                                     headers=headers, body=payload_gzip,
                                     retries=10)
            logger.debug("response from server: %d %s", resp.status, resp.data)
        else:
            logger.debug("dry run active, payload not sent to server")
