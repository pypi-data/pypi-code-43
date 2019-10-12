import json
import os
import pickle
import random
from getpass import getpass
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union
from urllib.request import getproxies

import requests

from robinhood.lib.errors import MissingCredentialError
from robinhood.lib.errors import URLNotFoundError

if TYPE_CHECKING:
    from robinhood.lib.account.accountobj import AccountObj

    URL_OBJS = Union[AccountObj, str]
    URL_CALLBACK_FUNC = Callable[[Any], Any]


class RobinhoodClient(object):

    ROBINHOOD_CLIENT_ID = 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS'
    REQUEST_TIMEOUT = 15

    def __init__(self) -> None:
        self._header = self._get_session_header()
        self._session = self._init_session()
        self._initialize_credential()
        self._test_connection()

    def _initialize_credential(self) -> None:
        token_file = self._get_token_file_location()
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                credential = pickle.load(token)
        else:
            credential = self._login()
            with open(token_file, 'wb') as token:
                pickle.dump(credential, token)

        self._unpack_credential(credential=credential)

    def _get_session_header(self) -> Dict[str, str]:
        return {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5',
            'Connection': 'keep-alive',
            'User-Agent': 'Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)',
            'X-Robinhood-API-Version': '1.0.0',
        }

    def _init_session(self) -> requests.sessions.Session:
        session = requests.session()
        session.proxies = getproxies()
        session.headers = self._header
        return session

    def _get_token_file_location(self) -> str:
        user_home = os.path.expanduser('~')
        file_name = '.r.pickle'
        return os.path.join(user_home, file_name)

    def _unpack_credential(self, credential: Dict[str, str]) -> None:
        os.environ['R_DEVICE_TOKEN'] = credential['device_token']
        os.environ['R_ACCESS_TOKEN'] = credential['access_token']
        os.environ['R_REFRESH_TOKEN'] = credential['refresh_token']

    def _login(self) -> Dict[str, str]:
        username = input('User ID: ')
        if username == '':
            username = 'thomas@zh-wang.me'
        password = getpass(prompt='Password: ')
        mfa_code = getpass(prompt='MFA Code: ')
        device_token = self._get_device_token()
        res = self._post_url(
            url='https://api.robinhood.com/oauth2/token/',
            data={
                'username': username,
                'password': password,
                'mfa_code': mfa_code,
                'device_token': device_token,
                'grant_type': 'password',
                'client_id': self.ROBINHOOD_CLIENT_ID,
                'expires_in': '86400',
                'scope': 'internal',
            },
        )
        res.raise_for_status()
        data = res.json()
        credential = {
            'device_token': device_token,
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
        }
        return credential

    def _relogin(self) -> None:
        self._header = self._get_session_header()
        self._session = self._init_session()
        credential = self._login()
        token_file = self._get_token_file_location()
        with open(token_file, 'wb') as token:
            pickle.dump(credential, token)

        self._unpack_credential(credential=credential)

    def _get_device_token(self) -> str:
        rands = []
        for i in range(0, 16):
            r = random.random()
            rand = 4294967296.0 * r
            rands.append((int(rand) >> ((3 & i) << 3)) & 255)

        hexa = []
        for i in range(0, 256):
            hexa.append(str(hex(i + 256)).lstrip('0x').rstrip('L')[1:])

        device_token = ''
        for i in range(0, 16):
            device_token += hexa[rands[i]]

            if (i == 3) or (i == 5) or (i == 7) or (i == 9):
                device_token += '-'

        return device_token

    def _test_connection(self) -> None:
        endpoint = 'https://api.robinhood.com/accounts/'
        self.get_url(url=endpoint)

    def get_url(
        self,
        url: str,
        return_none_if_404: bool = False,
        return_raw_response: bool = False,
    ) -> Any:
        self._set_authorization_header()
        self._header['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        response = self._session.get(url, timeout=self.REQUEST_TIMEOUT)
        if response.status_code == 401:
            self._relogin()
            return self.get_url(
                url=url,
                return_none_if_404=return_none_if_404,
                return_raw_response=return_raw_response,
            )

        if response.status_code == 404:
            raise URLNotFoundError()

        response.raise_for_status()

        if return_raw_response:
            return response.content
        else:
            return response.json()

    def get_object(
        self,
        url: str,
        callback: Callable[..., Any],
        callback_params: Optional[Dict[str, Any]] = None,
        result_key: Optional[str] = None,
    ) -> Any:
        return self.get_objects(
            url=url,
            callback=callback,
            callback_params=callback_params,
            result_key=result_key,
        )[0]

    def get_objects(
        self,
        url: str,
        callback: Callable[..., Any],
        callback_params: Optional[Dict[str, Any]] = None,
        result_key: Optional[str] = None,
    ) -> List[Any]:
        if callback_params is None:
            callback_params = {}

        results: List[Any] = []
        data: Dict[str, Any] = {'next': url}
        while data.get('next') is not None:
            current_url = data['next']
            data = self.get_url(current_url)
            result = data if result_key is None else data[result_key]
            if isinstance(result, list):
                results.extend([
                    callback(row, **callback_params)
                    for row in result
                    if row is not None
                ])
            else:
                results.append(callback(result, **callback_params))

            if data.get('next') == current_url:
                break

        return results

    def post_url(self, url: str, data: Any) -> requests.models.Response:
        self._set_authorization_header()
        return self._post_url(url=url, data=data)

    def _post_url(self, url: str, data: Any) -> requests.models.Response:
        self._header['Content-Type'] = 'application/json; charset=utf-8'
        str_encoded_data = str.encode(json.dumps(data))
        return self._session.post(url, data=str_encoded_data, timeout=self.REQUEST_TIMEOUT)

    def _set_authorization_header(self) -> None:
        access_token = os.environ.get('R_ACCESS_TOKEN')
        if access_token is None:
            raise MissingCredentialError()

        self._header['Authorization'] = f'Bearer {access_token}'


rhc = RobinhoodClient()
