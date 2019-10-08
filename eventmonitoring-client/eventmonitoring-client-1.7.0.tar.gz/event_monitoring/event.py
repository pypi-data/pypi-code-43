import time
import os
import datetime
from requests import post, ConnectionError
from pytz import timezone
from .utils import notify_telegram, ColorPrint


def push_view_data(method, path, uri, name, request_data,
                   response_data, status, headers, response_time):
    init_kwargs = {
        "system_name": os.environ.get("SYSTEM_EVENT_NAME", ""),
        "system_url": os.environ.get("SYSTEM_EVENT_URL", ""),
        "execute_token": os.environ.get("SYSTEM_EVENT_TOKEN", ""),
        "em_notifier": True if os.environ.get("SYSTEM_EM_NOTIFIER", "").lower() == 'true' else False,
        "debug": True if os.environ.get("SYSTEM_EM_NOTIFIER", "").lower() == 'true' else False,
    }
    event = Event(**init_kwargs)
    return event.push_endpoint_data(method, path, uri, name, request_data,
                                    response_data, status, headers, response_time)


def _request(url, data, headers):
    try:
        if data.get('finish'):
            time.sleep(1.5)
        r = post(url, json=data, headers=headers)
        if r.status_code != 200:
            return False
        return True
    except ConnectionError as e:
        print(ColorPrint.WARNING, f"=== Warning connection error, detail: {e}", ColorPrint.END)
        return False
    except Exception as e:
        print(ColorPrint.FAIL, f"=== Fail push report(Unknown exception), detail: {e}", ColorPrint.END)
        return False


class Event(object):
    def __init__(self, execute_token, system_name, system_url, em_notifier=False, debug=False):
        self.execute_token = execute_token
        self.system_name = system_name
        self.system_url = self._create_system_url(system_url)
        self.em_notifier = True if str(em_notifier).lower() == 'true' else False
        self.debug = True if debug.lower() == 'true' else False

    def _create_system_url(self, url):
        if not url.endswith("/api/event/"):
            if url.endswith("/"):
                url = f"{url}api/event/"
            else:
                url = f"{url}/api/event/"
        return url

    def push_endpoint_data(self, method, path, uri, name, request_data,
                           response_data, status, headers, response_time):
        endpoint_url = self.system_url.split("/api/event/")[0] + f"/api/endpoint_data/?system_name={self.system_name}"
        timestamp = datetime.datetime.fromtimestamp(int(time.time())) + datetime.timedelta(hours=3)
        request_headers = {"executetoken": self.execute_token}
        data = {
            "system_name": self.system_name,
            "path": path,
            "uri": uri,
            "method": method,
            "function_name": name,
            "request_data": request_data,
            "response_data": response_data,
            "response_time": response_time,
            "response_status": status,
            "headers": headers,
            "date_time": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "date": timestamp.strftime('%Y-%m-%d %H:%M:%S').split(" ")[0]
        }
        return _request(endpoint_url, data=data, headers=request_headers)

    def push_to_event(self, name, description=None, status=False):
        timestamp = datetime.datetime.fromtimestamp(int(time.time())) + datetime.timedelta(hours=3)
        headers = {"executetoken": self.execute_token}
        data = {
            "system_name": self.system_name,
            "event_name": name,
            "event_description": description,
            "finish": status
        }
        if status:
            data["event_end_time"] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time.sleep(0.6)
            data["event_start_time"] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            data["event_end_time"] = "..."
        return _request(self.system_url, data=data, headers=headers)

    def push_exception(self, name, description, trb):
        print(trb)
        exception_url = self.system_url.split("/api/event/")[0] + "/api/exception/"
        headers = {"executetoken": self.execute_token}
        data = {
            "system_name": self.system_name,
            "exc_name": name,
            "exc_description": description,
            "traceback": trb if trb else description
        }
        _request(exception_url, data=data, headers=headers)
        return True

    def log_exception(self, name, description, trb=None):
        self.push_to_event(name=name, description=description, status=True)
        if self.em_notifier:
            notify_telegram(self.system_name, name, description, trb)

        return self.push_exception(name, description, trb)
