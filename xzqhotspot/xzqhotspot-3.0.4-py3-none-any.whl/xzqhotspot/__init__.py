import winrt .windows .networking .networkoperators as networkoperators #line:1
import winrt .windows .networking .connectivity as connectivity #line:2
import winrt .windows .devices .wifi as wifi #line:3
import winrt .windows .devices .enumeration as enumeration #line:4
import clr #line:5
import time #line:6
clr .AddReference ("System.Net.NetworkInformation")#line:7
clr .AddReference ("System.Management")#line:8
from System .Net .NetworkInformation import NetworkInterface #line:9
from System .Management import ManagementObject ,ManagementObjectSearcher ,ManagementObjectCollection #line:10
class manager :#line:12
    def init (OOOO0OO000OO0O000 ):#line:13
        OOOO0OO000OO0O000 .__OOO0OO0O0000O00O0 =connectivity .NetworkInformation .get_internet_connection_profile ()#line:14
        OOOO0OO000OO0O000 .__O00000OO0OOO0OOOO =networkoperators .NetworkOperatorTetheringManager .create_from_connection_profile (OOOO0OO000OO0O000 .__OOO0OO0O0000O00O0 )#line:15
    @staticmethod #line:17
    def block (O00O0OO00O0OOO0O0 ):#line:18
        try :#line:19
            while O00O0OO00O0OOO0O0 .status !=1 :#line:20
                if O00O0OO00O0OOO0O0 .status !=0 :#line:21
                    return None #line:22
                time .sleep (0.1 )#line:23
            return O00O0OO00O0OOO0O0 .get_results ()#line:24
        except :#line:25
            return None #line:26
    def start_hotspot (OOO0OO0OOO000OO0O ):#line:29
        OO0O0O00O0O0000OO =OOO0OO0OOO000OO0O .hotspot_status ()#line:30
        if OO0O0O00O0O0000OO ==1 or OO0O0O00O0O0000OO ==3 :#line:31
            return 0 #line:32
        try :#line:33
            OOO0OO0OOO000OO0O .init ()#line:34
            O000O00OO00OO0000 =OOO0OO0OOO000OO0O .block (OOO0OO0OOO000OO0O .__O00000OO0OOO0OOOO .start_tethering_async ())#line:35
            return O000O00OO00OO0000 .status #line:36
        except :#line:37
            return 1 #line:38
    def stop_hotspot (O0OOO000000O0O0O0 ):#line:40
        OO0OO0000O0O0OOO0 =O0OOO000000O0O0O0 .hotspot_status ()#line:41
        if OO0OO0000O0O0OOO0 ==2 or OO0OO0000O0O0OOO0 ==3 :#line:42
            return 0 #line:43
        try :#line:44
            O0OOO000000O0O0O0 .init ()#line:45
            O0OOOOOOOO0O00000 =O0OOO000000O0O0O0 .block (O0OOO000000O0O0O0 .__O00000OO0OOO0OOOO .stop_tethering_async ())#line:46
            return O0OOOOOOOO0O00000 .status #line:47
        except :#line:48
            return 1 #line:49
    def hotspot_status (O0O0OOO00OO0O00OO ):#line:51
        OOO0O0O00OO00OOOO =0 #line:52
        try :#line:53
            O0O0OOO00OO0O00OO .init ()#line:54
            OOO0O0O00OO00OOOO =O0O0OOO00OO0O00OO .__O00000OO0OOO0OOOO .tethering_operational_state #line:55
            return OOO0O0O00OO00OOOO #line:56
        except :#line:57
            return 0 #line:58
    def is_internet_available (OOO0O0O0O000O0O00 ):#line:62
        OOOO0OO0OO0O0O000 =False #line:63
        try :#line:64
            O0000O00O00O00O00 =connectivity .NetworkInformation .get_internet_connection_profile ()#line:65
            OOOO0OO0OO0O0O000 =O0000O00O00O00O00 .get_network_connectivity_level ()==connectivity .NetworkConnectivityLevel .INTERNET_ACCESS #line:66
            return OOOO0OO0OO0O0O000 #line:67
        except :#line:68
            return False #line:69
    def get_wifi_ssid (O00OO0O000OO0O000 ):#line:71
        O0OO0000O00OO0O00 =None #line:72
        try :#line:73
            OO0O000OO0OO00OOO =connectivity .NetworkInformation .get_internet_connection_profile ()#line:74
            O0OO0000O00OO0O00 =OO0O000OO0OO00OOO .wlan_connection_profile_details .get_connected_ssid ()#line:75
            return O0OO0000O00OO0O00 #line:76
        except :#line:77
            return None #line:78
    def disable_network_adapter (O00O0O0O000OO0000 ,O0O0OOOO0O0O00O0O ):#line:80
        try :#line:81
            OOOO0O00OO0O0O000 =ManagementObjectSearcher ("SELECT * From Win32_NetworkAdapter").Get ()#line:82
            for O0OOOOOOO00OO00OO in OOOO0O00OO0O0O000 :#line:83
                for OO0O0OO000OOO00OO in O0OOOOOOO00OO00OO .Properties :#line:84
                    if OO0O0OO000OOO00OO .Name =='Name':#line:85
                        if OO0O0OO000OOO00OO .get_Value ().find (O0O0OOOO0O0O00O0O )>=0 :#line:86
                            O0OOOOOOO00OO00OO .InvokeMethod ("Disable",None )#line:87
                            return True #line:88
            return False #line:89
        except :#line:90
            return False #line:91
    def enable_network_adapter (O0OOO0000OO0O0O00 ,OO0O00O0OOOOOO00O ):#line:93
        try :#line:94
            OO0000OOOO00OO0O0 =ManagementObjectSearcher ("SELECT * From Win32_NetworkAdapter").Get ()#line:95
            OOO0OOOOO00O00OOO =[]#line:96
            for O0O0O0OOO0OOO00O0 in OO0000OOOO00OO0O0 :#line:97
                for OOOOO0000O0O0000O in O0O0O0OOO0OOO00O0 .Properties :#line:98
                    if OOOOO0000O0O0000O .Name =='Name':#line:99
                        OO00OO0000OOO0OO0 =OOOOO0000O0O0000O .get_Value ()#line:100
                        OOO0OOOOO00O00OOO .append ({'mo':O0O0O0OOO0OOO00O0 ,'name':OO00OO0000OOO0OO0 })#line:101
                        break #line:102
            OOO0OOOOO00O00OOO .sort (key =lambda OO0OO00O0OOOOOO00 :OO0OO00O0OOOOOO00 ['name'])#line:103
            for O00OOOO0OO00OOO0O in OOO0OOOOO00O00OOO :#line:104
                O00OOOO0OO00OOO0O ['mo'].InvokeMethod ("Disable",None )#line:105
            for O00OOOO0OO00OOO0O in OOO0OOOOO00O00OOO :#line:106
                O00OOOO0OO00OOO0O ['mo'].InvokeMethod ("Enable",None )#line:107
        except :#line:108
            return False #line:109
