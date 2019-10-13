#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***
"""
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed


import gc
import time
import requests
import urllib
import urllib.request
import urllib.parse

from memory_profiler import profile
# from concurrent.futures import ThreadPoolExecutor, as_completed

class getsession(object):
    def __init__(self):
        pass

    #@staticmethod
    def getnew(self):
        sess = requests.session()
        return sess

    def closeone(self, sess):
        sess.close()

class runner(threading.Thread):

    def __init__(self, sess):
        threading.Thread.__init__(self)
        self.sess = sess.getnew()
        self.toclose = sess
        #self.http = urllib.PoolManager()

    @profile
    def work(self):
        for i in range(4):
            payload = {'reset': "1", 'terminal': "terminal"}
            #response = requests.get('http://127.0.0.1:8081/api/v1/inventory',
            #                         headers={'X-Auth-Token': 'b', 'Connection': 'Keep-Alive'},
            #                        params=payload, stream=True)
            #response = self.sess.get('http://127.0.0.1:8081/api/v1/inventory',
            #                          stream=False, params=payload,
            #                          headers={'X-Auth-Token': 'b'})
            params = urllib.parse.urlencode(payload)
            if len(params) > 0:
                params = "?" + params
            requestx = urllib.request.Request('http://127.0.0.1:8081/api/v1/hello' + params,
                                      headers={'X-Auth-Token': 'b', 'Connection': 'close'})

            r = urllib.request.urlopen(requestx)

            time.sleep(2)
            contents = r.read()

            a = contents.decode('utf-8')
            status = r.code  # 200 is OK
            #self.http.clear()
            r.fd.close()
            #del http
            #time.sleep(0.01)
        #self.toclose.closeone(self.sess)
        print("work done----")
        pass

    @profile
    def run(self):
        self.work()


# @profile
def run_thread_request(sess, run):

    # with sess.__class__.getnew() as s:
    # with sess.getnew() as s:
    with requests.session() as s:
        # s.headers.update({'Connection': 'close'})
        response = s.get('http://127.0.0.1:8081/api/v1/inventory')
        # response.close()
        # doomy = response.content
        # del s
    return


# @profile
def main():
#    sess = requests.session()
    # sessions = getsession()
    sessions = None

    with ThreadPoolExecutor(max_workers=1) as executor:
        print('Starting!')
        tasks = {executor.submit(run_thread_request, sessions, run):
                     run for run in range(1)}
        for _ in as_completed(tasks):
            pass
    print('Done!')
    return


@profile
def calling():
    sessinos = getsession()

    for i in range(5):
        new_client = runnerx(sessinos)

        new_client.start()
        time.sleep(8.2)
        #new_client.join()  # commenting this out -> multi-threaded processing

    gc.collect()
    print("done xxxx")
    time.sleep(30)

    return


if __name__ == '__main__':
    calling()
    #for i in range(10):
    #    main()
    print("main finished")
    time.sleep(10000)
