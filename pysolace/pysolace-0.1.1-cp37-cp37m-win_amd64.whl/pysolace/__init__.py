def inject_lib_path():
    import os
    from pathlib import Path
    dir_path = Path(__file__).parent
    libs_path = dir_path.joinpath('.libs')
    os.environ['PATH'] = os.environ['PATH'] + ';' + libs_path.as_posix()
    os.environ['LD_LIBRARY_PATH'] = libs_path.as_posix()


inject_lib_path()
del inject_lib_path

from pysolace import solclient
from pysolace.solclient import SolLogLevel
import os
import typing

class SolClient:

    def __init__(self, log_level: SolLogLevel = SolLogLevel.SOLCLIENT_LOG_NOTICE, debug: bool = False):
        self.sol = solclient.client(log_level, debug)
        self.msg_callback = lambda topic, msg: print(topic, msg)
        self.event_callback = lambda resp_code, event, info, event_str: print("Response Code: {} | Event Code: {} | Info: {} | Event: {}".format(
        resp_code, event, info, event_str))
        self.onreply_callback = lambda topic, corrid, reply: print(topic, corrid, reply)
        self.set_msg_callback(self.msg_callback)
        self.set_event_callback(self.event_callback)
        self.set_onreply_callback(self.onreply_callback)
        self._token: str = ''
        self.req_rep_map: typing.Dict[str, dict] = {}
        self.rep_callback_map: typing.Dict[str, typing.Callable] = {}
        self._counter: int = 0
        
    def _gen_reqid(self):
        self._counter += 1
        return "c{}".format(self._counter)

    def msg_callback_wrap(self, topic: str, msg: dict):
        self.msg_callback(topic, msg)
        return 0

    def event_callback_wrap(self, resp_code: int, event: str, info: str, event_str: str):
        self.event_callback(resp_code, event, info, event_str)
    
    def onreply_callback_wrap(self, topic: str, corrid: str, reply: dict):
        for k, v in reply.items():
            self.req_rep_map[corrid][k] = v
        self.rep_callback_map.get(corrid, self.onreply_callback)(topic, corrid, reply)
        self.req_rep_map.pop(corrid)
        if corrid in self.rep_callback_map:
            self.rep_callback_map.pop(corrid)
        return 0

    def connect(self,
                host: str,
                vpn: str,
                user: str,
                password: str,
                clientname: str = ''):
        """
        connect(host: str, vpn: str, user: str, pass: str, clientname: str='') -> int


        Connect to Solace  

        Args:
            host (str): the host of solace to connect
            vpn (str): the vpn of solace
            user (str): the username of solace
            pass (str): the password of solace
            clientname (str) optional: the client name of solace 

        Returns:
            CSol Object
        """
        return solclient.connect(self.sol, host, vpn, user, password,
                                 clientname)

    def subscribe(self, topic: str):
        """
        subscribe(arg0: str) -> None


        Subscribe topic

        Args:
            topic (str): the topic to subscribe
        """
        solclient.subscribe(self.sol, topic)

    def unsubscribe(self, topic: str):
        """
        unsubscribe(arg0: str) -> None


        UnSubscribe topic

        Args:
            topic (str): the topic to unsubscribe
        """
        solclient.unsubscribe(self.sol, topic)

    def publish(self, topic: str, msg: dict) -> int:
        """
        publish(topic: str, msg: dict) -> int


        Publish Message to topic

        Args:
            sol (obj::Csol): the object of solclient return 
            topic (str): the topic to subscribe
            msg_dict (dict): message to publish 
        """
        return solclient.publish(self.sol, topic, msg)

    def request(self, topic: str, payload: dict, 
                corrid: str = '' , timeout: int = 5000, 
                cb: typing.Callable[[str, str, dict], int] = None
        ) -> dict:
        if self._token:
            payload = dict(token=self._token, **payload)
        if not corrid and not timeout:
            corrid = self._gen_reqid()
            self.req_rep_map[corrid] = solclient.request(self.sol, topic, corrid, payload, timeout)
            if cb:
                self.rep_callback_map[corrid] = cb
            return self.req_rep_map[corrid]
        return solclient.request(self.sol, topic, corrid, payload, timeout)
    
    def reply(self, topic: str, header: dict, body: dict):
        return solclient.reply(self.sol, topic, header, body)

    def get_msg_queue_size(self):
        return solclient.get_msg_queue_size(self.sol)

    def set_session(self, token: str):
        self._token = token

    def set_msg_callback(self, callback_func: callable):
        """
        set_callback(arg0: Callable[[str, dict], int]) -> None

        Set subscribe using callback function

        Args:
            func (py::func): the python callable function the func first arg is topic
                            second arg is message and return int

        Examples:
            Examples with Doctest format
            >>> def sol_callback(topic, msg):
            >>>     print(topic, msg)
        """
        self.msg_callback = callback_func
        solclient.set_callback(self.sol, self.msg_callback_wrap)

    def set_event_callback(self, callback_func: callable):
        """
        set_event_callback(arg0: Callable[[int, int, str, str], None]) -> None

        Set subscribe using callback function

        Args:
            func (py::func): the python callable function the func with
                            arg0: response code
                            arg1: session event code
                            arg2: info string
                            arg3: session event string

        Examples:
            Examples with Doctest format
            >>> def event_callback(response_code, event_code, info, event):
            >>>     print(response_code, event_code, info, event)
        """
        self.event_callback = callback_func
        solclient.set_event_callback(self.sol, self.event_callback)

    def set_reply_callback(self, callable_func: callable):
        self.reply_callback = callable_func
        solclient.set_reply_callback(self.sol, self.reply_callback)
    
    def set_onreply_callback(self, callable_func: callable):
        self.onreply_callback = callable_func
        solclient.set_onreply_callback(self.sol, self.onreply_callback_wrap)

    def disconnect(self):
        return solclient.disconnect(self.sol)

    def __del__(self):
        solclient._del(self.sol)