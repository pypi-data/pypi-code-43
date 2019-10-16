import argparse

from requests import RequestException

from xml.etree import ElementTree
import json
from datetime import datetime
from events import Events  ## https://github.com/pyeve/events

import time


# parser.add_argument('-s','--server', help='host with port default: http://sandbox-hdp.hortonworks.com:8088', default="http://sandbox-hdp.hortonworks.com:8088")
# parser.add_argument('-p','--path', help='API-Endpoint default: /ws/v1/cluster/apps', default="/ws/v1/cluster/apps")
# parser.add_argument('-i','--intervall', help='how often should be sent a request to the server (in seconds), default is 1 ', default=1, type=int)
# parser.add_argument('-l','--log', help='show the running Apps/Jobs on the cluster in your console ', default="t", type=str2bool)


class HadoopYarnClusterChecker(Events):
    __events__ = ('on_empty_cluster',)

    def __init__(self, server="http://sandbox-hdp.hortonworks.com:8088", path="/ws/v1/cluster/apps", intervall=1,
                 log=True, excludes="[{\"name\":\"Zeppelin\"},{\"name\":\"Zeppelin1\"}]"):
        super().__init__()
        self.server = server
        self.path = path
        self.intervall_time = intervall
        self.excludes = json.loads(excludes)
        self.log = log

    @staticmethod
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    def __removeExcludesFromRunningAppsList(self, running_apps, xmlData):
        if self.excludes is None:
            return
        for i in self.excludes:
            key = list(i.keys())[0]
            value = i.get(key)
            excluding_apps = list(filter(lambda app: app[key] == value and app["state"] == "RUNNING", xmlData))

            for exclude in excluding_apps:
                if exclude in running_apps:
                    running_apps.remove(exclude)
                    print("excluded: \n" + str(exclude))

    def run(self, requests):
        isClusterFull = True  # we just assume that
        while (isClusterFull):
            try:
                response = requests.get(self.server + self.path)
                isClusterFull = self.areJobsRunning(response.text)
                time.sleep(self.intervall_time)
            except BaseException as be:
                raise be
                break

        self.on_empty_cluster()

    def areJobsRunning(self, xmlResponseText):
        try:
            # json_data = bf.data(ElementTree.fromstring(xmlResponseText))
            apps = json.loads(xmlResponseText)["apps"]["app"]
            running_apps = list(filter(lambda app: app["state"] == "RUNNING", apps))
            self.__removeExcludesFromRunningAppsList(running_apps, apps)
            if (len(running_apps) == 0):
                return False  # cluster is empty / no jobs running in the cluster
            else:
                if (self.log == True):
                    print(
                        datetime.now().strftime("%d.%m.%Y, %H:%M:%S") + "; These Apps/Jobs are running on the cluster:")
                    print(str(map(lambda app: {"name": app["name"]}, running_apps)))
                return True
        except BaseException as be:
            raise be
