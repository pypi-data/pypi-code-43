#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .response import HTTPResponse

class HTTPException(HTTPResponse):
    status_int = 500
    use_etags = False

HTTPServerError = HTTPException

class HTTPNotFound(HTTPException):
    """HTTP 404 (Not Found)"""
    status_int = 404
HTTPNotFoundResponse = HTTPNotFound    

class HTTPNotModified(HTTPNotFound):
    status_int = 304
class HTTPClientError(HTTPException):
    status_int = 400 # bad request
class HTTPUnauthorized(HTTPClientError):
    status_int = 401
class HTTPForbidden(HTTPClientError):
    status_int = 403
class HTTPFoundResponse(HTTPResponse):
    """HTTP 302 (Found)
    
    Requires one param: 
    * location: a URI string.
    """
    status_int = 302
    
    def __init__(self, location, **kwargs):
        #kwargs['status'] = str(self.status_int)
        # Displays a short message to the user with a link to
        # the given resource URI
        # TODO: Use a template for this.
        kwargs['content'] = '''\
        <html>
        <p>Click here to follow this redirect: <a href=\"%s\">Link</a></p>
        </html>'''%location
        kwargs['mimetype'] = 'text/html'
        super(HTTPFoundResponse, self).__init__(**kwargs)
        
        #self.location = location     # location to redirect to

        #self.initial_kwargs = kwargs 
        self.http_headers.append(('Location', location)) #.split('?next=')[1]
        self.http_headers.append(('Cache-Control', 'no-cache')) # Prevent caching redirects

    def __call__(self, env, start_response):
        start_response(self.status_code, self.headers)
        return self.app_iter

HTTPRedirectResponse = HTTPFoundResponse # alias

class HTTPSeeOtherResponse(HTTPFoundResponse):
    """HTTP 303 (See Other)"""
    status_int = 303

class HTTPNotModifiedResponse(HTTPResponse):
    """HTTP 304 (Not Modified)"""
    status_int = 304

    def __init__(self, *args, **kwargs):
        super(HTTPNotModifiedResponse, self).__init__(*args, **kwargs)
        
        self.http_headers['Date'] = datetime.now().ctime()
            

        del self.http_headers['Content-Type']
    
        self.content = '';


class HTTPUnauthorizedResponse(HTTPResponse):
    """HTTP 401 (Unauthorized)"""
    status_int = 401

class HTTPForbiddenResponse(HTTPResponse):
    """HTTP 403 (Forbidden)"""
    status_int = 403

HTTPForbidden = HTTPForbiddenResponse


