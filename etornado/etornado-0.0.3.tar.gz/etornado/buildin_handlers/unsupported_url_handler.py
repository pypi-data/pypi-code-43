from etornado.buildin_handlers.base_handler import BaseHandler
from etornado.error_code_manager import HTTP_OK, ErrorCode


class UnsupportedUrlHandler(BaseHandler):

    def process(self, *args, **kwargs):
        self.send_error(HTTP_OK, ec=ErrorCode.UNSUPPORTED_URL, url=self.request.uri)
