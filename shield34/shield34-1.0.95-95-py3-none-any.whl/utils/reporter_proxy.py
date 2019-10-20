import os
import platform

from browsermobproxy import Server

from shield34_reporter.auth.sdk_authentication import SdkAuthentication
from shield34_reporter.utils.network_utils import NetworkUtils


class ReporterProxy():

    @staticmethod
    def create_proxy():
        if SdkAuthentication.is_authorized():
            from shield34_reporter.container.run_report_container import RunReportContainer
            block_run_report_container = RunReportContainer.get_current_block_run_holder()
            if block_run_report_container.proxyServer is None:
                ReporterProxy.add_browsermob_to_path()
                browser_mob_server = Server('browsermob-proxy', options={'port': NetworkUtils.get_random_port()})
                #browser_mob_server.host = "127.0.0.1"
                browser_mob_server.start()
                proxy = browser_mob_server.create_proxy(params= {"trustAllServers": "true", "port": NetworkUtils.get_random_port(), "bindAddress": "127.0.0.1"})
                block_run_report_container.proxyServer = proxy
                return True
            else :
                # proxy already exists. !
                return True
        return False

    @staticmethod
    def add_browsermob_to_path():
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(ROOT_DIR, 'proxy', 'browsermob-proxy-2.1.4', 'bin')
        os.environ["PATH"] += os.pathsep + path

