
import time
import socket

from zeroconf import ServiceBrowser, Zeroconf, ServiceListener, ServiceInfo


class Listener(ServiceListener):

    def add_service(self, zeroconf, kind, name):
        service_info = zeroconf.get_service_info(kind, name)
        print(f"service add {name} :: {service_info}")

    def remove_service(self, zeroconf, kind, name):
        print(f"service rem {name} ::")


service_type = "_healer._tcp.local."

property_dict = {
    'healer-service': 'true',
    'path': 'service-location',
}

service_info = ServiceInfo(
    type_=service_type,
    name=f"healer-service.{service_type}",
    addresses=[socket.inet_aton("127.0.0.1")],
    port=18080,
    properties=property_dict,
)

empty = Zeroconf()

listener = Listener()

browser = ServiceBrowser(zc=empty, type_=service_type, listener=listener)

while True:
    empty.register_service(service_info)
    time.sleep(5)
    empty.unregister_service(service_info)
    time.sleep(5)

empty.close()
