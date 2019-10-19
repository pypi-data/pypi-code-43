from lxml import html
from urllib.parse import urlparse
import requests


class HttpFormAuth(requests.auth.AuthBase):
    '''
    Form based Authentication Handler for Requests.
    '''

    def __init__(self, username, password):
        '''
        param:
            user: str
            password: str
        '''
        self.username = username
        self.password = password
        self.redirect_cnt = 0

    def __call__(self, r):
        '''
        The hook handler.
        '''
        r.register_hook('response', self._form_login)

        return r


    def _form_login(self, r, **kwargs):
        '''
        param:
            r: Response

        return:
            Response
        '''
        if not 300 <= r.status_code < 400 and self.redirect_cnt < 1:
            try:
                payload, url, method = self._prep_form_fields(r)
                prep = r.request.copy()
                prep.prepare(method = method, url = url, data = payload, cookies = r.cookies)
                _r = r.connection.send(prep, **kwargs)
            except:
                pass
            else:
                self.redirect_cnt += 1
                return _r
        return r


    def _prep_form_fields(self, r):
        '''
        Get the authentication form fields for sign in.
        '''
        parsed_url = urlparse(r.url)
        base_url = '{uri.scheme}://{uri.netloc}{uri.path}'.format(uri=parsed_url)

        doc = html.document_fromstring(r.text, base_url=base_url)
        form = doc.xpath('//form')[0]
        user, password = self._pick_fields(form)
        form.fields[user] = self.username
        form.fields[password] = self.password

        payload = dict(form.form_values())
        return payload, form.action or form.base_url, form.method


    def _pick_fields(self, form):
        '''
        idea from diango form authentication.
        '''
        userfield = passfield = emailfield = None
        for x in form.inputs:
            if not isinstance(x, html.InputElement):
                continue

            _type = x.type
            if _type == 'password' and passfield is None:
                passfield = x.name
            elif _type == 'email' and emailfield is None:
                emailfield = x.name
            elif _type == 'text' and userfield is None:
                userfield = x.name

        return emailfield or userfield, passfield
