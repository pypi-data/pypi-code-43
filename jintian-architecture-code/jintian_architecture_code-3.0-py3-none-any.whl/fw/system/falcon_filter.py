from com.fw.base.base_log import logger
from com.fw.utils.id_util import IDUtils
import json

class FalconFilter(object):

    def process_request(self, req, resp):
        '''
        所有请求之前调用此方法
        :param req:
        :param resp:
        :param resource:
        :param req_succeeded:
        :return:
        '''
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        resp.set_header('Access-Control-Allow-Headers', 'x-requested-with,content-type')

        logger.info("HTTP:{},{}".format(req.forwarded_uri,json.dumps(req.params)))

        if "" in req.params.keys():
            req.params.pop("")

        if "_" in req.params.keys():
            req.params.pop("_")

        if req.env["REQUEST_METHOD"] == "GET":
            keys = []
            for key, val in req.params.items():
                if not val or val == "":
                    keys.append(key)
            for key in keys:
                req.params.pop(key)


falconFilter = FalconFilter()