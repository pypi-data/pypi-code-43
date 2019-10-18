from twisted.web import server, resource
from twisted.internet import reactor, endpoints
import json
from flutter_debugger.packager import *

class FlutterDebuggerServer(resource.Resource):
    isLeaf = True
    numberRequests = 0
    port = 8006
    _is_running = False

    def __init__(self, port=8006):
        self.port = port

    def render_GET(self, request):
        request.setHeader(b"content-type", b"application/json")
        if str(request.uri, 'utf8') == '/package':
            # flutter进行打包
            result, file_name, zip_file_path = package_flutter_assets()
            with open(zip_file_path, 'rb') as file:
                all_bytes = file.read()
                request.setHeader(b"content-type", b"application/zip")
                return all_bytes
        return json.dumps({
            "ret": 0,
            "message": "调用成功"
        }).encode("ascii")

    def run(self):
        endpoints.serverFromString(reactor, "tcp:" + str(self.port)).listen(server.Site(self))
        reactor.run()



if __name__ == '__main__':
    flt_server = FlutterDebuggerServer()
    flt_server.run()
