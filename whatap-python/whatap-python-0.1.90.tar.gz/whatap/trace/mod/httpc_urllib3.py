from whatap.trace.mod.application_wsgi import transfer, interceptor_httpc_request, \
    trace_handler


def instrument_urllib3(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            # set mtid header
            kwargs['headers'] = transfer(kwargs.get('headers', {}))
            
            # set httpc_url
            httpc_url = args[2]
            callback = interceptor_httpc_request(fn, httpc_url, *args, **kwargs)
            return callback
        
        return trace
    
    module.RequestMethods.request = wrapper(module.RequestMethods.request)
