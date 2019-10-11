import requests
import logging
import socket
import threading
import time
import random
import string
try:
    import queue
except ImportError:
    import Queue as queue

logger = logging.getLogger("opentsdb_metrics")

MPS_LIMIT = 0  # Limit on metrics per second to send to OpenTSDB

_last_timestamp = None
_last_metrics = set()

_valid_metric_chars = set(string.ascii_letters + string.digits + '-_./')


def _post(host, port, q, done, mps, stop, test_mode, http_end_point):
    """Worker thread. Connect to host/port, pull data from q until done is set"""
    retry_line = None
    while not (stop.is_set() or (done.is_set() and retry_line is None and q.empty())):
        stime = time.time()

        if retry_line:
            line = retry_line
            retry_line = None
        else:
            try:
                line = q.get(True, 1)  # blocking, with 1 second timeout
            except Exception:
                if done.is_set():  # no items in queue, and parent finished
                    break
                else:  # no items in queue, but parent might send more
                    continue

        if not send_request(http_end_point, line, test_mode=test_mode):
            retry_line = line

        etime = time.time() - stime  # time that actually elapsed

        # Expected value of wait_time is 1/MPS_LIMIT, ie. MPS_LIMIT per second.
        if mps > 0:
            wait_time = (2.0 * random.random()) / (mps)
            if wait_time > etime:  # if we should wait
                time.sleep(wait_time - etime)  # then wait


def send_request(http_end_point, json_line, test_mode=False):
    if not test_mode:
        try:
            response = requests.post(http_end_point, json=json_line)
            if not (response.status_code == requests.codes.ok or response.status_code == requests.codes.no_content):
                logger.warning("Failed to send metric {} to endpoint {}".format(json_line['metric'], http_end_point))
                return False
        except requests.exceptions.RequestException as e:
            logger.warning("Problem with connection to {}: {}".format(http_end_point, repr(e)))
            return False
    return True


class Client():
    def __init__(self, host, port, test_api, put_api, qsize=100000, host_tag=True,
                 mps=MPS_LIMIT, check_host=True, test_mode=False, service='opentsdb'):
        """Main tsdb client. Connect to host/port. Buffer up to qsize metrics"""
        self.metric_name_set = set([])
        self.q = queue.Queue(maxsize=qsize)
        self.done = threading.Event()
        self._stop = threading.Event()
        self.host = host
        self.port = int(port)
        self.queued = 0
        self.end_point = "http://{}:{}{}".format(host, port, put_api)
        self.service = service
        self.test_mode = test_mode
        self.test_point = "http://{}:{}{}".format(host, port, test_api)

        # Make initial check that the host is up, because once in the
        # background thread it will be silently ignored/retried
        if check_host:
            response = requests.get(self.test_point)
            if not response.status_code == requests.codes.ok:
                logger.warning(
                    "failed to connect to host test_point: {}, check if this is the correct host and port and test endpoint".format(self.test_point)
                )

        if host_tag:
            self.host_tag = socket.gethostname()
        elif isinstance(host_tag, str):
            self.host_tag = host_tag

        self.t = threading.Thread(target=_post,
                                  args=(host, self.port, self.q, self.done, mps, self._stop, test_mode, self.end_point))

        self.t.start()

    def index(self, name, val, asynchronous=True, **tags):
        """Index metric name with value val. You must include at least one tag as a kwarg"""
        if name in self.metric_name_set:
            return
        self.put(name, val, asynchronous=asynchronous, **tags)

    def put(self, name, val, asynchronous=True, **tags):
        """Send metric with value val and tags to the defined http_endpoint"""
        # do not allow .log after closing
        assert not self.done.is_set(), "worker thread has been closed"
        # check if valid metric name
        assert all(c in _valid_metric_chars for c in name), "invalid metric name " + name

        val = float(val)  # Duck type to float/int, if possible.
        if int(val) == val:
            val = int(val)

        if self.host_tag and 'host' not in tags:
            tags['host'] = self.host_tag

        # get timestamp from system time, unless it's supplied as a tag
        timestamp = int(tags.pop('timestamp', time.time()))

        assert not self.done.is_set(), "processing thread has been closed"
        assert tags != {}, "Need at least one tag"

        # Add the dictionary of data here
        line = {
            "metric": name,
            "timestamp": timestamp,
            "value": val,
            "tags": tags
        }
        self.metric_name_set.add(name)

        if asynchronous:
            try:
                self.q.put(line, False)
                self.queued += 1
            except queue.Full:
                logger.warning(
                    "http_client - Warning: dropping oldest metric because Queue is full. Size: {}".format(self.q.qsize())
                )
                self.q.get()  # Drop the oldest metric to make room
                self.q.put(line, False)
        else:
            send_request(self.end_point, line, self.test_mode)

    def close(self):
        """Close and clean up the connection"""
        self.done.set()

    def wait(self):
        """Close then block waiting for background thread to finish"""
        self.close()
        while self.t.is_alive():
            time.sleep(0.05)

    def stop(self):
        self._stop.set()

    def __del__(self):
        self.close()


class OpenTSDBClient(Client):
    def __init__(self, host, **kwargs):
        Client.__init__(self, host, port=4242, test_api='/api/version', put_api='/api/put', service='opentsdb', **kwargs)
