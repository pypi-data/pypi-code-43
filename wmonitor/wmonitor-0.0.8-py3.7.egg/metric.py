import asyncio
import logging
import os
import time

import requests
from requests import adapters

from wmonitor import constant

url = constant.Config.domain + "/adapter/metrics"

requests_log = logging.getLogger("WMonitor")
handler = logging.FileHandler(os.path.join(constant.Config.log_dir, "wmonitor.log"))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
requests_log.addHandler(handler)
print(constant.Config.logging_level)
requests_log.setLevel(constant.Config.logging_level)

# 线程池配置
session = requests.session()
session.mount('http://', adapters.HTTPAdapter(pool_connections=1, pool_maxsize=20, max_retries=3))
session.post(url)


class MetricSender:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        requests_log.info("初始化 event_loop 失败。创新新的event_loop")
        loop = asyncio.new_event_loop()

    async def send(self):
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(url=url, data=self.__str__(), headers=headers)
            requests_log.info("发送成功, content: %s" % response.content)
            requests_log.debug("发送报文，data: %s" % self.__str__())
            response.close()
        except BaseException:
            requests_log.info("发送监控信息失败。data:%s" % self.__str__())


class Metric(MetricSender):

    @classmethod
    def gauge(cls, metric, value=1):
        entity = cls()
        entity.__counterType = "Gauge"
        entity.__metric = metric
        entity.__value = value
        entity.__tags = ''
        return entity

    @classmethod
    def counter(cls, metric, value=1):
        entity = cls()
        entity.__metric = metric
        entity.__counterType = "Counter"
        entity.__value = value
        entity.__tags = ''
        return entity

    @classmethod
    def state(cls, metric, value=1):
        entity = cls()
        entity.__metric = metric
        entity.__counterType = "State"
        entity.__value = value
        entity.__tags = ''
        return entity

    def tags(self, tags):
        self.__tags = tags
        return self

    def value(self, value):
        self.__value = value
        return self

    def __str__(self):
        result = {}
        all_attribute = self.__dict__
        for key in all_attribute:
            key = str(key)
            real_name = key.replace("_Metric__", "")
            result[real_name] = self.__getattribute__(key)

        return result.__str__()

    def send(self):
        self.__appName = constant.Config.app_code
        self.__timestamp = time.time()

        super().loop.run_until_complete(super().send())


if __name__ == '__main__':
    Metric.gauge("test").send()
