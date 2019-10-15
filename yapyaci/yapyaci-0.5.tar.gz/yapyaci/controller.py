from .object_set import AciSet, AciTree, ListOfAciTree, to_tree, to_ltree
from .exception import AuthFailure, InvalidLookupRequest, WsOpenFailure, InvalidToken, InvalidJsonPayload, AuthRefreshFailure, SubRefreshFailure
import logging
import json
import http.client
import threading
import time

logger1 = logging.getLogger(__name__)


class SharedContainer:
    def __init__(self):
        self.base_header = {
                'cache-control': 'no-cache',
                'Content-Type': 'test/plain'
        }

        self.ip = ''
        self.Cookie = ''
        self.token = ''
        self.urlToken = ''
        self.subscription_list = list()
        self.lock = threading.Lock()

        self.ws_status = "CLOSE"

        self.keep_running_thread = True


    def reset_token(self):
        self.Cookie = ''
        self.token = ''
        self.urlToken = ''

    @property
    def ws_url(self):
        return "ws://{0}/socket{1}?{2}".format(self.ip, self.token, self.urlToken)

    @property
    def http_header(self):
        header = self.base_header
        header['APIC-challenge'] = self.urlToken
        header['Cookie'] = self.Cookie

        return header

    @property
    def auth_token(self):
        if self.Cookie and self.urlToken:
            return True
        else:
            return False


global shared_obj
shared_obj=SharedContainer()


class HttpWrapper:
    def __init__(self, ip, user, password, shared=shared_obj):
        self._user = user
        self._password = password
        self._shared = shared
        self._shared.ip = ip
        self.__conn = http.client.HTTPConnection(ip, http.client.HTTP_PORT)

        if not self._shared.auth_token:
            logger1.warning('Proceeding with authentication')
            self._authenticate()

    def _authenticate(self):
        http_body = {
            'aaaUser' : {
                'attributes': {
                    'name': self._user,
                    'pwd': self._password
                }
            }
        }

        http_response_code, http_response_header, http_response_payload = self._send_post("/api/aaaLogin.json?gui-token-request=yes", http_body)

        if http_response_code == 200:
            logger1.warning('Authentication successful')

            ltree = ListOfAciTree(http_response_payload)
            aaaLogin = to_tree(ltree.search('aaaLogin'))
            self._shared.urlToken = aaaLogin.urlToken
            self._shared.token = aaaLogin.token
            self._shared.Cookie =  http_response_header('Set-Cookie')

        else:
            raise AuthFailure('Failed to login to {0}'.format(self._shared.ip))


    def _send_get(self, url):
        try:
            self.__conn.request('GET', url, '', self._shared.http_header)
            http_response = self.__conn.getresponse()
            http_response_payload = json.loads(http_response.read().decode('utf-8'))

        except json.decoder.JSONDecodeError as error:
            logger1.critical("Respond payload not in JSON format")
            raise

        except TimeoutError as error:
            logger1.critical("Connection Timeout")
            raise

        except Exception as error:
            logger1.critical(error)
            raise

        logger1.info('{0} - {1}'.format(url, http_response.code))
        return http_response.code, http_response.getheader, http_response_payload


    def _send_post(self, url, payload):
        try:
            self.__conn.request('POST', url, json.dumps(payload), self._shared.http_header)
            http_response = self.__conn.getresponse()
            http_response_payload = json.loads(http_response.read().decode('utf-8'))

        except json.decoder.JSONDecodeError as error:
            logger1.critical("Respond payload not in JSON format")
            raise

        except TimeoutError as error:
            logger1.critical("Connection Timeout")
            raise

        except Exception as error:
            logger1.critical(error)
            raise

        logger1.info('{0} - {1}'.format(url, http_response.code))
        return http_response.code, http_response.getheader, http_response_payload


    def disconnect(self):
        self.__conn.close()
        self._shared.reset_token()


class AuthRefreshTread(threading.Thread):
    def __init__(self, shared=shared_obj, *args, **kwargs):
        self._shared = shared
        super(AuthRefreshTread, self).__init__(*args, **kwargs)

    def run(self):
        while self._shared.keep_running_thread:
            time.sleep(60)

            logger1.warning('Refreshing auth token')

            self._shared.lock.acquire()
            conn = http.client.HTTPConnection(self._shared.ip, http.client.HTTP_PORT)
            conn.request('GET', "/api/aaaRefresh.json?gui-token-request=yes", '', self._shared.http_header)
            http_response = conn.getresponse()
            http_response_payload = json.loads(http_response.read())

            if http_response.code == 200:
                logger1.error('Token successfully refreshed')

                ltree = ListOfAciTree(http_response_payload)
                aaaLogin = to_tree(ltree.search('aaaLogin'))
                #shared.urlToken = aaaLogin.urlToken
                self._shared.token = aaaLogin.token
                self._shared.Cookie = http_response.getheader('Set-Cookie')

            else:
                logger1.error('Failed to refresh token with HTTP respond code {0}'.format(http_response.code))
                self._shared.reset_token()
                self._shared.keep_running_thread = False

            self._shared.lock.release()
            conn.close()

        logger1.error("The authentication loop was stopped")


class Api(HttpWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def lookup_by_class(self, cls, **kwarg) -> ListOfAciTree:
        base_url = "/api/node/class/"
        url = base_url + cls + ".json?"

        for key, value in kwarg.items():
            url += "&" + key.replace('_', '-') + '=' + value

        http_response_code, http_response_header, http_response_payload = self._send_get(url)
        return ListOfAciTree(http_response_payload)

    def lookup_by_dn(self, dn, **kwarg) -> AciTree:
        base_url = "/api/mo/"
        url = base_url + dn + ".json?"

        for key, value in kwarg.items():
            url += "&" + key.replace('_', '-') + '=' + value

        http_response_code, http_response_header, http_response_payload = self._send_get(url)
        return AciTree(http_response_payload)

    def lookup(self, **kwarg) -> AciSet:
        if 'cls' in kwarg.keys():
            base_url = "/api/node/class/"
            url = base_url + kwarg.pop('cls') + ".json?"

        elif 'dn' in kwarg.keys():
            base_url = "/api/mo/"
            url = base_url + kwarg.pop('dn') + ".json?"

        else:
            raise InvalidLookupRequest("Failed to lookup. Neither a class or dn was provided")

        for key, value in kwarg.items():
            url += "&" + key.replace('_', '-') + '=' + value

        http_response_code, http_response_header, http_response_payload = self._send_get(url)
        return AciSet(http_response_payload)

    def mqapi2(self, tool, **kwarg):
        base_url = "/mqapi2/"
        url = base_url + tool + ".json?"

        for key, value in kwarg.items():
            url += "&" + key.replace('_', '-') + '=' + value

        http_response_code, http_response_header, http_response_payload = self._send_get(url)
        return ListOfAciTree(http_response_payload)

class SubscriptionRefreshTread(threading.Thread):
    def __init__(self, shared=shared_obj, *args, **kwargs):
        self._shared=shared
        super(SubscriptionRefreshTread, self).__init__(*args, **kwargs)

    def run(self):
        while self._shared.keep_running_thread:
            time.sleep(60)

            self._shared.lock.acquire()
            conn = http.client.HTTPConnection(self._shared.ip, http.client.HTTP_PORT)

            for sub in self._shared.subscription_list:
                conn.request('GET', '/api/subscriptionRefresh.json?id={0}'.format(sub), '', self._shared.http_header)
                http_response = conn.getresponse()
                http_response_payload = json.loads(http_response.read())

                if http_response.code == 200:
                    logger1.error('Sub {0} successfully refresh'.format(sub))

                else:
                    logger1.error('Sub {0} failed to be refresh'.format(sub))
                    self._shared.reset_token()
                    self._shared.keep_running_thread = False

            self._shared.lock.release()
            conn.close()

        logger1.error("The subscription loop was stopped")


class EApi(Api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._shared.keep_running_thread = True
        self._aaa_refresh_tread = AuthRefreshTread(shared=self._shared, name='aaaRefresh')
        self._sub_refresh_thread = None
        self._stream_handler_thread = None
        self._aaa_refresh_tread.start()

    def lookup_by_class(self, *args, **kwarg) -> ListOfAciTree:
        ltree = super().lookup_by_class(*args, **kwarg)
        self._watch_subscription(ltree)

        return ltree

    def lookup_by_dn(self, *args, **kwarg) -> AciTree:
        tree = super().lookup_by_dn(*args, **kwarg)
        self._watch_subscription(tree)

        return tree

    def setup_stream(self, stream_handler_class, *args, **kwargs):
        self._stream_handler_thread = stream_handler_class(shared=self._shared, *args, **kwargs)
        self._stream_handler_thread.daemon = True
        self._stream_handler_thread.start()

        for c in range(5):
            if self._shared.ws_status == "OPEN":
                break

            logger1.warning('Waiting for WebSocket to be opened...')
            time.sleep(1)

        if self._shared.ws_status != "OPEN":
            raise WsOpenFailure('Failed to opened WebSocket within 5 sec')

    def _watch_subscription(self, aci_set : AciSet):

        if aci_set.subscription_id and not self._shared.subscription_list:
            logger1.info('First subscription received {0}'.format(aci_set.subscription_id))
            self._shared.subscription_list.append(aci_set.subscription_id)

            logger1.warning('Starting subscription loop')
            self._sub_refresh_thread = SubscriptionRefreshTread()
            self._sub_refresh_thread.start()

        if aci_set.subscription_id and aci_set.subscription_id not in self._shared.subscription_list:
            logger1.info('New subscription id {0}'.format(aci_set.subscription_id))
            self._shared.subscription_list.append(aci_set.subscription_id)

    def hold(self):
        self._aaa_refresh_tread.join()
        self._stream_handler_thread.kill_thread()





