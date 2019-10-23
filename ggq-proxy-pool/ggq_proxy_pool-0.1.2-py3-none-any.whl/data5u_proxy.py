import json
import logging
from time import sleep

import requests

from proxy_pool import IpPool
import threading


class Data5UProxy(IpPool):
    def __init__(self, api_url):
        super().__init__(api_url)

    def start(self):
        # GetIpThread(self.api_url, self.ip_pool, self.cond).start()
        pass

    def _request_ip(self):
        logging.info("请求新的ip")
        res = requests.get(self.api_url).content.decode()
        res = json.loads(res)
        if res['success']:
            all_data = res['data']
            for dd in all_data:
                self.ip_pool.add(f"{dd['ip']}:{dd['port']}")
                with self.cond:
                    self.cond.notify_all()
                logging.info("请求成功")

    def get_ip(self):
        res = requests.get(self.api_url).content.decode()
        res = json.loads(res)
        all_data = res['data']
        dd = all_data[0]
        return f"{dd['ip']}:{dd['port']}"

    def report_baned_ip(self, ip):
        pass

    def report_bad_net_ip(self, ip):
        pass


class GetIpThread(threading.Thread):
    def __init__(self, api_url, ip_pool: set, cond: threading.Condition):
        super().__init__(daemon=True)
        self.url = api_url
        self.ip_pool = ip_pool
        self.cond = cond

    def run(self) -> None:
        while True:
            logging.debug("刷新新的ip")
            res = requests.get(self.url).content.decode()
            res = json.loads(res)
            if res['success']:
                all_data = res['data']
                for dd in all_data:
                    self.ip_pool.add(f"{dd['ip']}:{dd['port']}")
                    logging.debug("请求成功")
                    with self.cond:
                        self.cond.notify_all()
            sleep(5)
