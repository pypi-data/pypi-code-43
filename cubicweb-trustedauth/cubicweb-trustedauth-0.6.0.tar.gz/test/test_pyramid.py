import webtest

from cubicweb.pyramid.test import PyramidCWTest
from cubicweb_trustedauth import includeme
from cubicweb.web.controller import Controller


class TestController(Controller):
    __regid__ = 'testauth'

    def publish(self, rset):
        if self._cw.user.login == self._cw.form.get('expected', 'admin'):
            return b'VALID'
        else:
            return b'INVALID'


class PyramidTrustedAuthRequestTC(PyramidCWTest):
    test_db_id = 'trustedauth'
    settings = {'cubicweb.bwcompat': True}

    def includeme(self, config):
        includeme(config)

    def _assert_auth_failed(self, req, result):
        self.assertEqual(b'INVALID', result)

    def _assert_auth(self, req, result):
        self.assertEqual(200, req.status_int)
        self.assertEqual(b'VALID', result)

    def _test_header_format(self, hkey, login, http_method='GET',
                            headers=None, content=None, url='/testauth', **params):
        if headers is None:
            headers = {}
        headers[hkey] = login
        req = webtest.TestRequest.blank(url, base_url=self.config['base-url'].rstrip('/'),
                                        method=http_method,
                                        headers=headers, **params)
        if http_method == 'POST':
            if content is None:
                content = "rql=Any+X+WHERE+X+is+Player"
        if content:
            req.body = content
        with self.temporary_appobjects(TestController):
            resp = self.webapp.do_request(req)
        return resp.body, resp

    def test_login(self):
        result, req = self._test_header_format(hkey='X-Remote-User',
                                               login='admin',
                                               )
        self._assert_auth(req, result)

    def test_bad_login(self):
        result, req = self._test_header_format(hkey='X-Remote-User',
                                               login='admin2',
                                               )
        self._assert_auth_failed(req, result)

    def test_bad_key(self):
        result, req = self._test_header_format(hkey='X-Remote-User2',
                                               login='admin',
                                               )
        self._assert_auth_failed(req, result)


if __name__ == "__main__":
    import unittest
    unittest.main()
