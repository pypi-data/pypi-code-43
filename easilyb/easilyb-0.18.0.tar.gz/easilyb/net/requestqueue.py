import requests
import subprocess

from easilyb.queueworker import QueueWorker


import logging
logger = logging.getLogger(__name__)


USERAGENT = "Firefox"

def _request(callback, index, method, url, arg1, arg2, kwargs):
    logger.debug("requesting %s(%s) for %s"%(method, url, str(callback)))
    if method=='get':
        resp = requests.get(url,arg1,**kwargs)
    elif method=='post':
        resp = requests.post(url, arg1, arg2, **kwargs)
    callback(resp, index)

def _wget_wraper(url, fileoutput, referer=None, useragent=USERAGENT):
    cmd = ['wget', url, '-O', fileoutput, '-U', useragent]
    if referer: cmd+= ['--referer', referer]
    try: return subprocess.Popen(cmd).wait() #return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    except:
        return 999

def _wget(url, fileoutput, callback=None, index=None, referer=None, useragent=USERAGENT):
    logger.debug("wgeting %s(%s) for %s"%(url, str(callback)))
    resp = _wget_wraper(url, fileoutput, referer, useragent)
    callback(resp, index)

class Requester:
    def __init__(self, threads=10, queue=None):
        self.queue = QueueWorker(_request, threads=threads, log_progress=False, queue=queue)

    def get(self, callback, url, index=None, params=None, **kwargs):
        self.queue.put((callback, index, 'get', url, params,None,kwargs))

    def post(self, callback, url, index=None, data=None, json=None, **kwargs):
        self.queue.put((callback, index, 'post', url, data, json, kwargs))
    def join(self):
        return self.queue.join()

class Wgeter:
    def __init__(self, threads=10, queue=None):
        self.queue = QueueWorker(_wget, threads=threads, log_progress=False, queue=queue)

    def wget(self, url, fileoutput, callback=None, index=None, referer=None, useragent=USERAGENT):
        self.queue.put((url, fileoutput, callback, index, referer, useragent))

    def join(self):
        return self.queue.join()