"""
from winney import Winney
from .laka_service import LakaService
from .errors import RegisterServiceFailed


class Consul(object):

    def __init__(self, host, port):
        self.winney = Winney(host=host, port=port, headers={"content-type":"application/json"})
        self.init_functions()

    def init_functions(self):
        self.winney.add_url(method="GET", uri="/v1/agent/services", function_name="list_service")
        self.winney.add_url(method="GET", uri="/v1/agent/service/{NAME}", function_name="get_service")
        self.winney.add_url(method="PUT", uri="/v1/agent/service/register", function_name="register_service")

    def list_service(self, name):
        rs = self.winney.list_service()
        service_list = []
        for _, value in rs.get_json().items():
            if value["Service"] != name:
                continue
            service_list.append(LakaService.load_from_json(value))
        return service_list
    
    def get_service(self, name):
        r = self.winney.get_service(NAME=name)
        if not r.ok():
            return None
        return LakaService.load_from_json(r.get_json())
    
    def register_service(self, service):
        r = self.winney.register_service(json=service.json())
        if not r.ok():
            raise RegisterServiceFailed("failed to register service {}. http status_code = {}".format(service.name, r.status_code))
        service = self.get_service(service.name)
        if not service:
            raise RegisterServiceFailed("failed to register service: {}".format(service.name))
"""