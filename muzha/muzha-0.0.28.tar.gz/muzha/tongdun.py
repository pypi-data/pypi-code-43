import requests


class TongDunBase:
    """
    ip白名单限制.
    """

    def __init__(self, partner_code, partner_key, app_name, url, request_type="POST"):
        self.partner_code = partner_code
        self.partner_key = partner_key
        self.app_name = app_name
        self._url = url
        self.request_type = request_type

    @property
    def url(self):
        return "{}?partner_code={}&partner_key={}&app_name={}".format(self._url, self.partner_code, self.partner_key,
                                                                      self.app_name)

    def request_cache_first(self, send_data, cache_resp=True, dbware_persisted=True):
        raise NotImplementedError

    def get_class(self):
        return self.__class__.__name__

    def request(self, send_data, *args, **kwargs):
        response = requests.post(self.url, data=send_data, *args, **kwargs)
        if not response.ok:
            raise SystemError(u'{} response.status_code is {}'.format(self.get_class(), response.status_code))
        try:
            resp = response.json()
            if not isinstance(resp, dict):
                raise SystemError("resp {} type {} not dict".format(resp, type(resp)))
            return resp
        except Exception as e:
            print(e)
