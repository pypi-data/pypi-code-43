from .import handlers #line:1
try :#line:3
    from django .utils .deprecation import MiddlewareMixin #line:5
except ImportError :#line:6
    MiddlewareMixin =object #line:7
from simplepro .group import view #line:9
class SimpleMiddleware (MiddlewareMixin ):#line:12
    def process_request (self ,request ):#line:14
        O00000OO00O0O0O0O =request .path #line:16
        if not O00000OO00O0O0O0O .endswith ('/'):#line:17
            O00000OO00O0O0O0O =O00000OO00O0O0O0O +'/'#line:18
        if O00000OO00O0O0O0O .endswith ('group/action/'):#line:20
            return view .action (request )#line:21
        else :#line:22
            return handlers .process_request (request ,O00000OO00O0O0O0O )#line:23
    def process_view (self ,request ,view_func ,view_args ,view_kwargs ):#line:25
        return handlers .process_view (request ,view_func )#line:26
    def process_exception (self ,request ,exception ):#line:31
        pass #line:32
