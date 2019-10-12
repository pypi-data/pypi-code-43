import queue
import contextlib
import queue
import threading
import time
import traceback
from io import StringIO
from queue import Queue

import slack
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from func_timeout import func_timeout, FunctionTimedOut

from django.conf import settings

SLACK_GLOBALS = {}


assert hasattr(settings, 'SLACK_OAUTH_SECRET'), "SLACK_OAUTH_SECRET not found in settings.py"
CLIENT = slack.WebClient(token=settings.SLACK_OAUTH_SECRET)


def broadcast_buffered_lines(line_queue: Queue, execution_finished: threading.Event, channel_id,
                             timed_out: threading.Event):
    """
    post together lines that are within a time interval of 0.01 seconds
    """
    buffer = Queue()
    line_count = 0
    while not execution_finished.is_set() or not buffer.empty():
        try:
            line = line_queue.get(timeout=0.01)
        except queue.Empty:
            lines = []
            while not buffer.empty():
                lines.append(buffer.get())
            if lines:
                CLIENT.chat_postMessage(channel=channel_id, text='\n'.join(lines))
        else:
            buffer.put(line)
            line_count += 1

    if line_count == 0 and not timed_out.is_set():
        CLIENT.chat_postMessage(channel=channel_id, text="Code ran")


def execute_and_broadcast(code, channel_id):
    line_queue = Queue()

    execution_finished = threading.Event()

    s_stream = SplitStringIO(line_queue)

    timed_out = threading.Event()
    threading.Thread(
        target=lambda: broadcast_buffered_lines(line_queue, execution_finished, channel_id, timed_out)).start()

    with contextlib.redirect_stdout(s_stream):
        try:
            func_timeout(10, exec, args=(code, SLACK_GLOBALS))
        except FunctionTimedOut:
            timed_out.set()
            CLIENT.chat_postMessage(channel=channel_id, text='Code timed out after 10 seconds')
        except Exception:
            traceback.print_exc(file=s_stream)

    while not s_stream.all_transferred:
        time.sleep(0.01)
    execution_finished.set()


@require_http_methods(["POST"])
@csrf_exempt
def index(request):
    global SLACK_GLOBALS
    # naive filter
    # {'token': ['f1YirFic7PJn1i9PXWsayRVW'], 'team_id': ['TJ5FCV2AF'], 'team_domain': ['ualbertaaltlab'],
    #  'channel_id': ['DJK49P338'], 'channel_name': ['directmessage'], 'user_id': ['UJGUWTUHE'], 'user_name': ['syan4'],
    #  'command': ['/r'], 'text': ['print(1)'],
    #  'response_url': ['https://hooks.slack.com/commands/TJ5FCV2AF/791217491556/FA91ZndPg9Vn7xQqEvqoJfYh'],
    #  'trigger_id': ['791688910944.617522988355.1a960905c25a8cb65c5fa30a37a4f533']}
    if not request.POST or 'channel_id' not in request.POST:
        raise Http404()

    if request.POST.get('command', None) == '/r':
        text = request.POST.get('text', '')
        channel_id = request.POST.get('channel_id', "")
        threading.Thread(target=lambda: execute_and_broadcast(text, channel_id)).start()

        # slack wont show anything
        response_data = {
            "response_type": "in_channel", "text": ""
        }
        return JsonResponse(response_data)

    else:
        raise Http404()


class SplitStringIO(StringIO):
    _queue: Queue

    def __init__(self, queue: Queue):
        """writable string io that broadcasts received lines in real time"""
        super().__init__()
        self._cursor = 0
        self._queue = queue
        self._all_transferred = threading.Event()

    @property
    def all_transferred(self):
        return self._queue.empty()

    def write(self, *args, **kwargs):
        super().write(*args, **kwargs)
        self.seek(self._cursor)
        for line in self.readlines():
            self._queue.put(line)
        self._cursor = self.tell()
