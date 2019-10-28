import time
import os
import datetime
from requests import post, ConnectionError
from pytz import timezone
from .utils import notify_telegram, ColorPrint


def push_view_data(method: str, path: str, uri: str, name: str, request_data: dict,
                   response_data: dict, status: int, headers: dict, response_time: float) -> bool:
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


def _request(url: str, data: dict, headers: dict) -> bool:
    """
    :param url: str
    :param data: dict
    :param headers: str
    :return: bool
    """
    try:
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
    def __init__(self, execute_token: str, system_name: str, system_url: str,
                 em_notifier: bool = False, debug: bool = False) -> None:
        """
        :param execute_token: str
        :param system_name: str
        :param system_url: str
        :param em_notifier: bool
        :param debug: bool
        """
        self.execute_token = execute_token
        self.system_name = system_name
        self.system_url = self._create_system_url(system_url)
        self.em_notifier = True if str(em_notifier).lower() == 'true' else False
        self.debug = True if str(debug).lower() == 'true' else False

    def _create_system_url(self, url: str) -> str:
        if not url.endswith("/api/event/"):
            if url.endswith("/"):
                url = f"{url}api/event/"
            else:
                url = f"{url}/api/event/"
        return url

    def push_endpoint_data(self, method: str, path: str, uri: str, name: str, request_data: dict,
                           response_data: dict, status: int, headers: dict, response_time: float) -> bool:
        """
        :param method: str
        :param path: str
        :param uri: str
        :param name: str
        :param request_data: dict
        :param response_data: dict
        :param status: int
        :param headers: dict
        :param response_time: float
        :return: bool
        """
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

    def push_to_event(self, name: str, description: any = None, status: bool = False) -> bool:
        """
        :param name: str
        :param description: any
        :param status: bool
        :return: bool
        """
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
            time.sleep(0.1)
            data["event_start_time"] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            data["event_end_time"] = "..."
        return _request(self.system_url, data=data, headers=headers)

    def push_exception(self, name: str, description: str, trb: str) -> bool:
        """
        :param name: str
        :param description: dict
        :param trb: str
        :return: bool
        """
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

    def log_exception(self, name: str, description: str, trb: any = None) -> bool:
        """
        :param name: str
        :param description: str
        :param trb: any
        :return: bool
        """
        self.push_to_event(name=name, description=description, status=True)
        if self.em_notifier:
            notify_telegram(self.system_name, name, description, trb)

        return self.push_exception(name, description, trb)
