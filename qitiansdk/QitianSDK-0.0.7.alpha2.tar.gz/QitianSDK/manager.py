import requests
from SmartDjango import Excp, ErrorJar, E, BaseError, Analyse, P


@ErrorJar.pour
class QitianError:
    QITIAN_GET_USER_INFO_FAIL = E("齐天簿获取用户信息失败", hc=500)
    QITIAN_AUTH_FAIL = E("齐天簿身份认证失败", hc=500)


class QitianManager:
    QITIAN_HOST = 'https://ssoapi.6-79.cn'
    GET_TOKEN_URL = '%s/api/oauth/token' % QITIAN_HOST
    GET_USER_INFO_URL = '%s/api/user/' % QITIAN_HOST

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    @Excp.pack
    @Analyse.p(P('res').as_dict('code', 'msg', P('body').set_null()))
    def _res_checker(self, res, error: E):
        if res['code'] != BaseError.OK.eid:
            return error(res['msg'])
        return res['body']

    @Excp.pack
    def _req_extractor(self, req: requests.Response, error: E):
        if req.status_code != requests.codes.ok:
            return error
        try:
            res = req.json()
        except Exception:
            return error

        return self._res_checker(res, error)

    @Excp.pack
    def get_token(self, code):
        req = requests.post(self.GET_TOKEN_URL, json=dict(
            code=code,
            app_secret=self.app_secret,
        ), timeout=3)

        return self._req_extractor(req, QitianError.QITIAN_AUTH_FAIL)

    @Excp.pack
    def get_user_info(self, token):
        req = requests.get(self.GET_USER_INFO_URL, headers=dict(
            token=token,
        ), timeout=3)

        return self._req_extractor(req, QitianError.QITIAN_GET_USER_INFO_FAIL)
