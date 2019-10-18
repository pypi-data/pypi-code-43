from .import backends #line:1
try :#line:3
    from django .utils .deprecation import MiddlewareMixin #line:5
except ImportError :#line:6
    MiddlewareMixin =object #line:7
from simplepro .group import view #line:9
class SimpleMiddleware (MiddlewareMixin ):#line:12
    def process_request (self ,request ):#line:14
        O0O00O000000OOO00 =request .path #line:16
        if not O0O00O000000OOO00 .endswith ('/'):#line:17
            O0O00O000000OOO00 =O0O00O000000OOO00 +'/'#line:18
        if O0O00O000000OOO00 .endswith ('group/action/'):#line:20
            return view .action (request )#line:21
        elif O0O00O000000OOO00 .endswith ('simplepro/active/'):#line:22
            return backends .process_lic (request )#line:23
        elif O0O00O000000OOO00 .endswith ('simplepro/info/'):#line:24
            return backends .process_info (request )#line:25
    def process_view (self ,request ,view_func ,view_args ,view_kwargs ):#line:27
        return backends .pre_process (request ,view_func )#line:28
    def process_exception (self ,request ,exception ):#line:33
        pass #line:34
