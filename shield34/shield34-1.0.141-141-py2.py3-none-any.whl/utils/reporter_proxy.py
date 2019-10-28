import json
import os
import pickle
import platform
import stat
import sys
import tempfile

from browsermobproxy import Server

from shield34_reporter.auth.sdk_authentication import SdkAuthentication
from shield34_reporter.utils.network_utils import NetworkUtils
import urllib

class ReporterProxy():

    @staticmethod
    def create_proxy():
        if SdkAuthentication.is_authorized():
            from shield34_reporter.container.run_report_container import RunReportContainer
            block_run_report_container = RunReportContainer.get_current_block_run_holder()
            if block_run_report_container.proxyServer is None:
                browser_mob_server = None
                ReporterProxy.add_browsermob_to_path()
                proxy_file_path = ReporterProxy.get_shield34_proxy_file_name()
                brwoser_mob_server_config = {}
                if os.path.exists(proxy_file_path):
                    try:
                        brwoser_mob_server_config = ReporterProxy.read_json_from_file(proxy_file_path)
                        browser_mob_server = Server('browsermob-proxy',
                                                    options={'port': brwoser_mob_server_config['port']})

                        browser_mob_server.pid = brwoser_mob_server_config['pid']
                    except Exception as e:
                        browser_mob_server = None

                if browser_mob_server is None or not browser_mob_server._is_listening():
                    proxy_server_port = NetworkUtils.get_random_port()

                    browser_mob_server = Server('browsermob-proxy',
                                                    options={'port': proxy_server_port})
                    browser_mob_server.start()
                    brwoser_mob_server_config['port'] = proxy_server_port
                    brwoser_mob_server_config['pid'] = browser_mob_server.process.pid
                    browser_mob_server.pid = browser_mob_server.process.pid
                    try:
                        ReporterProxy.write_json_to_file(proxy_file_path, brwoser_mob_server_config)
                    except Exception as e:
                        pass

                chained_proxy = ReporterProxy.get_os_proxies()
                if chained_proxy is not None:
                    proxy = browser_mob_server.create_proxy(
                        params={"trustAllServers": "true", "port": NetworkUtils.get_random_port(),
                                "bindAddress": "127.0.0.1", 'httpProxy': chained_proxy})
                else:
                    proxy = browser_mob_server.create_proxy(
                        params={"trustAllServers": "true", "port": NetworkUtils.get_random_port(),
                                "bindAddress": "127.0.0.1"})
                proxy.base_server = browser_mob_server
                block_run_report_container.proxyServer = proxy

                return True
            else :
                # proxy already exists. !
                return True
        return False



    @staticmethod
    def write_object_to_file(file_path, obj):
        pickle_out = open(file_path, "wb")
        pickle.dump(obj, pickle_out)
        pickle_out.close()

    @staticmethod
    def load_object_from_file(file_path):
        pickle_in = open(file_path, "rb")
        return pickle.load(pickle_in)


    @staticmethod
    def get_shield34_proxy_file_name():
        temp_dir = tempfile.gettempdir()
        shield34_temp_file_name = os.path.join(temp_dir, 'shield34_proxy.lck')
        return shield34_temp_file_name

    @staticmethod
    def write_json_to_file(file_path, dictjson):
        with open(file_path, 'w') as file:
            file.write(json.dumps(dictjson))
        file.close()

    @staticmethod
    def read_json_from_file(file_path):
        with open(file_path, 'r') as file:
            dictjsonstr = file.read()
        file.close()
        return json.loads(dictjsonstr)

    # @staticmethod
    # def close_proxy_if_idle():
    #     from shield34_reporter.container.run_report_container import RunReportContainer
    #     block_run_report_container = RunReportContainer.get_current_block_run_holder()
    #     proxy_ports = block_run_report_container.proxyServer.proxy_ports()
    #     if len(proxy_ports) == 1:
    #         port = proxy_ports[0]
    #         if port == block_run_report_container.proxyServer.port:
    #             try:
    #                 import psutil
    #                 p = psutil.Process(block_run_report_container.proxyServer.base_server.pid)
    #                 p.kill()
    #             except NoSuchProcess as e:
    #                 pass

    @staticmethod
    def get_os_proxies():
        if sys.version_info > (3, 0):
            proxies = urllib.request.getproxies()
        else:
            proxies = urllib2.getproxies()
        if hasattr(proxies, 'http') or hasattr(proxies, 'https'):
            proxy = getattr(proxies, 'http')
            proxy = proxy.replace("http://", "")
            proxy = proxy.replace("www.", "")
            return proxy
        else:
            return None

    @staticmethod
    def add_browsermob_to_path():
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(ROOT_DIR, 'proxy', 'browsermob-proxy-2.1.4', 'bin')
        os.environ["PATH"] += os.pathsep + path

        try:
            if platform.system() != 'Windows':
                file = os.path.join(path, "browsermob-proxy")
                st = os.stat(file)
                os.chmod(file, st.st_mode | stat.S_IEXEC)
        except Exception as e:
            pass

