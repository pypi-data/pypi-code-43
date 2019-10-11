#reference_controller_proxy.py
#Proxy object for a generic controller
from iotile.core.hw.proxy.proxy import TileBusProxyObject
from typedargs.annotate import context, annotated
from .sensorgraph import SensorGraphPlugin
from .controllertest import ControllerTestPlugin
from .tilemanager import TileManagerPlugin
from .remotebridge import RemoteBridgePlugin
from .configmanager import ConfigDatabasePlugin

@context("ReferenceControllerProxy")
class ReferenceControllerProxy (TileBusProxyObject):
    def __init__(self, stream, addr):
        super(ReferenceControllerProxy, self).__init__(stream, addr)
        self.name = 'ReferenceControllerProxy'
        self._sensorgraph = SensorGraphPlugin(self)
        self._testinterface = ControllerTestPlugin(self)
        self._tileinterface = TileManagerPlugin(self)
        self._trub = RemoteBridgePlugin(self)
        self._configstore = ConfigDatabasePlugin(self)

    @classmethod
    def ModuleName(cls):
        return 'refcn1'

    @annotated
    def sensor_graph(self):
        return self._sensorgraph

    @annotated
    def test_interface(self):
        return self._testinterface

    @annotated
    def tile_manager(self):
        return self._tileinterface

    @annotated
    def remote_bridge(self):
        return self._trub

    @annotated
    def config_database(self):
        return self._configstore
