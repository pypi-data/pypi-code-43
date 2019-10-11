import logging
import re
import socket
import sys

socket.setdefaulttimeout(20.0)

#logging.basicConfig(level=logging.DEBUG)

import mechanize

from functools import wraps

class cas_simulation():
    def handle_http_request(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except mechanize.HTTPError as e:
               logging.error("Received %s %s for %s" % (e.code, e.reason, e.geturl()))
               logging.error("%s", repr(e.read(1024*2)))
               e.seek(0)
               logging.error("%s", repr(str(e.info())))
               raise e
            except mechanize.URLError as e:
               logging.error("Exception during %s: %s" % (f.func_name, e.reason))
               raise e
        return decorated

    def __init__(self, sp_url,
                       cas_user, cas_pass,
                       success_pattern,
                       post_auth_checks=[],skip_form_id=None):
        self.logger = logging.getLogger('cas_simulation')
        self.useragent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
        self._init_browser()

        self.sp_url = sp_url
        if not self.sp_url.startswith( ("http://", "https://") ):
            raise ValueError("sp_url is not a url")

        self.cas_user = cas_user
        self.cas_pass = cas_pass
        self.success_pattern = success_pattern

        self.post_auth_checks = post_auth_checks
        self.skip_form_id = skip_form_id

    def run(self):
        self._fetch_sp()
        self._verify_login_form()
        response = self._authenticate()
        #raise runtimeerror if no match
        self._check_response(response,self.success_pattern)
        self._do_post_auth_checks()
        #if we made it this far with no exceptions, things must be ok
        return True

    def _init_browser(self):
        self.br = mechanize.Browser()
        # Ignore robots.txt.  Required for Peoplesoft POST
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-Agent', self.useragent)]

    @handle_http_request
    def _fetch_sp(self):
        self.logger.debug("Fetching service-provider %s", self.sp_url)
        self.br.open(self.sp_url)

        #should end up on a cas logon page
        landing_page = self.br.geturl()
        self.logger.debug("Request for %s landed on %s",
                          self.sp_url, landing_page)

    def _verify_login_form(self):
        landing_page = self.br.geturl()
        if "/login?" not in landing_page:
            raise RuntimeError("%s redirected to %s, which doesn't look like a CAS logon page" % (self.sp_url, landing_page))
        if not ("service=" in landing_page or "TARGET=" in landing_page):
            raise RuntimeError("%s redirected to %s, which doesn't contain service or TARGET params" % (self.sp_url, landing_page))

    @handle_http_request
    def _second_post(self):
        #sometimes you need to post to the form given by
        #SP after authentication
        try:
            for form in self.br.forms():
                if form.attrs.get('id') == 'csusb-base-ft-fn-hdft-search-form':
                    raise ValueError('form posts back to self at / and breaks simulation')
                if self.skip_form_id is not None:
                    #self.logger.debug("Considering submitting form %s", repr(form.attrs))
                    if form.attrs.get('id') == self.skip_form_id:
                        raise ValueError('stopping simulation at form with id %s' % self.skip_form_id)
                    if form.attrs.get('action') == self.skip_form_id:
                        raise ValueError('stopping simulation at form action %s' % self.skip_form_id)
            self.br.select_form(nr=0)
        except mechanize.FormNotFoundError:
            return None #no secondary post, that's fine
        except ValueError:
            return None
        #except mechanize.BrowserStateError:
            #return None #302 redirects land here?
        #form found, time to post
        self.logger.debug("Post-auth POSTing to page: %s",
                          self.br.form)
        response = self.br.submit()
        return response

    @handle_http_request
    def _authenticate(self):
        try:
           response = None
           for form in self.br.forms():
               self.logger.debug("found form %s", form.attrs['id'])
               if form.attrs['id'] == 'fm1':
                   self.br.form = form
                   break
           if self.br.form is None:
               raise RuntimeError('CAS logon - no form with id "fm1"')
           self.br['username'] = self.cas_user
           self.br['password'] = self.cas_pass
           self.logger.debug("%s-ing credentials to %s",
                              self.br.form.method.upper(), self.br.form.action)
           response = self.br.submit()
           self.logger.debug("Redirect after submit() %s", response.geturl())
        except RuntimeError as e:
           self.logger.error("Failed Login (runtime): %s", e )
           raise

        for i in range(2):
            second_response = self._second_post()
            if second_response:
                response = second_response

        self.logger.debug("Authentication post-redirect url: %s",
                          response.geturl())
        self.logger.debug("Authentication response headers: %s",
                          repr(str(response.info())))
        return response

    def _check_response(self,response,pattern):
        page = response.read()
        if not re.search(pattern,page):
            self.logger.debug("----- BEGIN %s -----\n", response.geturl())
            self.logger.debug(repr(page))
            self.logger.debug("----- END %s -----", response.geturl())
            raise RuntimeError("pattern %s not found on: %s" % \
                                (repr(pattern), response.geturl()))
        self.logger.debug("OK: Pattern %s matches content of: %s", repr(pattern), response.geturl())
        return True

    @handle_http_request
    def _do_post_auth_checks(self):
       for check in self.post_auth_checks:
           self.logger.debug("Fetching post-authentication url %s for %s",
                              check['url'], self.cas_user)
           response = self.br.open(check['url'])
           if self._check_response(response,check['pattern']):
               logging.info("Success - pattern found on %s",
                   response.geturl())


if __name__ == '__main__':
    import getpass
    user = '000226420'
    password = getpass.getpass()
    logging.basicConfig(level=logging.DEBUG)
    for logger in "http_redirects", "http_responses", "http_requests", "equiv":
        l = logging.getLogger("mechanize." + logger)
        l.addHandler(logging.StreamHandler(sys.stderr))
        l.setLevel(logging.DEBUG)

    import sys
    #sp_login('https://weblogon.csusb.edu/cas/login?service=', user, password, '')
    #sp_login('https://csusb.blackboard.com/', user ,password, r"<title>Welcome, .* &ndash; Blackboard Learn</title>")

    s1 = cas_simulation('https://outlook.com/csusb.edu',
                       user ,password,
                       r"<title>Sign in to your account")
    #supposed to send stuff to "mechanize.http_redirects" logger
    s1.br.set_debug_http(True)
    s1.br.set_debug_responses(True)
    s1.br.set_debug_redirects(True)
    s1.run()

    #s2 = cas_simulation('https://cmshr.cms.csusb.edu/HSBPRD/signon.html',
    #                   user, password,
    #                   r"<title>Employee-facing registry content</title>")
    #s2.run()
    #https://weblogon.csusb.edu/cas/login?method=POST&service=https://cmshr.cms.csusb.edu/psp/HSBPRD/?cmd=login%26languageCd=ENG%26userid=PS%26pwd=z
    #https://weblogon.csusb.edu/cas/login?method=post&service=https://cmshr.cms.csusb.edu/psp/hsbprd/?cmd=login%26languagecd=eng%26userid=ps%26pwd=z
    #sp_login('https://weblogon.csusb.edu/cas/login?method=POST&service=https://cmsweb.cms.csusb.edu/psp/HSBPRD/EMPLOYEE/HRMS/h/?tab=DEFAULT%26?cmd=login%26languageCd=ENG%26userid=PS%26pwd=z',
    #                   user ,password, r"<title>Employee-facing registry content</title>")
