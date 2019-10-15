import winrt.windows.networking.networkoperators as networkoperators
import winrt.windows.networking.connectivity as connectivity
import winrt.windows.devices.wifi as wifi
import winrt.windows.devices.enumeration as enumeration
import clr
import time
clr.AddReference("System.Net.NetworkInformation")
clr.AddReference("System.Management")
from System.Net.NetworkInformation import NetworkInterface
from System.Management import ManagementObject,ManagementObjectSearcher,ManagementObjectCollection

class manager:
    def init(self):
        self.__profile = connectivity.NetworkInformation.get_internet_connection_profile()
        self.__mg = networkoperators.NetworkOperatorTetheringManager.create_from_connection_profile(self.__profile)
    
    @staticmethod
    def block(iasync):
        try:
            while iasync.status != 1:
                if iasync.status != 0:
                    return None
                time.sleep(0.1)
            return iasync.get_results()
        except:
            return None


    def start_hotspot(self):
        s = self.hotspot_status()
        if s==1 or s==3:
            return 0
        try:
            self.init()
            res=self.block(self.__mg.start_tethering_async())
            return res.status
        except:
            return 1

    def stop_hotspot(self):
        s = self.hotspot_status()
        if s==2 or s==3:
            return 0
        try:
            self.init()
            res=self.block(self.__mg.stop_tethering_async())
            return res.status
        except:
            return 1

    def hotspot_status(self):
        res = 0
        try:
            self.init()
            res = self.__mg.tethering_operational_state
            return res
        except:
            return 0


    # 是否连接上Internet
    def is_internet_available(self):
        res = False
        try:
            p = connectivity.NetworkInformation.get_internet_connection_profile()
            res = p.get_network_connectivity_level() == connectivity.NetworkConnectivityLevel.INTERNET_ACCESS
            return res
        except:
            return False

    def get_wifi_ssid(self):
        ssid = None
        try:
            p = connectivity.NetworkInformation.get_internet_connection_profile()
            ssid = p.wlan_connection_profile_details.get_connected_ssid()
            return ssid
        except:
            return None

    def disable_network_adapter(self,keyword):
        try:
            collction = ManagementObjectSearcher("SELECT * From Win32_NetworkAdapter").Get()
            for mo in collction:
                for pd in mo.Properties:
                    if pd.Name == 'Name':
                        if pd.get_Value().find(keyword)>=0:
                            mo.InvokeMethod("Disable",None)
                            return True
            return False
        except:
            return False

    def enable_network_adapter(self,keyword):
        try:
            collction = ManagementObjectSearcher("SELECT * From Win32_NetworkAdapter").Get()
            for mo in collction:
                for pd in mo.Properties:
                    if pd.Name == 'Name':
                        if pd.get_Value().find(keyword)>=0:
                            mo.InvokeMethod("Enable",None)
                            return True
            return False
        except:
            return False
