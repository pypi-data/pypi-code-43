import json
try:
    from component import *
    from tools import *
except:
    from yoctools.component import *
    from yoctools.tools import *

class OCC:
    def __init__(self, host=None):
        if host:
            self.host = host
        else:
            self.host = 'occ.t-head.cn'

    def yocComponentListUpload(self):
        cmd = '/api/resource/cdk/yocComponent/common/upload'
        body = {
             "model": {
                 "name":"CH2201",
                 "version":"version"
                }
        }
        text = json.dumps(body)

        js = self.request(get_url(cmd, text), text)


    def yocGetInfo(self, name):
        cmd = '/api/resource/component/getInfo'
        body = {}
        js = self.request(get_url(cmd, body), body)


    def yocComponentList(self, chipId):
        cmd = '/api/resource/cdk/yocComponentList'
        body = {}
        text = json.dumps(body)


        js = self.request(get_url(cmd, text), text)

        packs = ComponentGroup()
        for p in js:
            pack = Component()
            pack.loader_json(p)
            packs.add(pack)
        return packs


    def request(self, url, body):
        connection = http.HTTPSConnection(self.host)

        try:
            connection.request('POST', url, body)
            response = connection.getresponse()
            if response.status == 200:
                text = response.read()
                js = json.loads(text)
                # print(js)

                if js['code'] == 0:
                    return js['result']['packages']
        except:
            print("network faild.")
            exit(0)

        return {}
