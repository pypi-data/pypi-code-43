"""AnduinBridge enables remote processes to call Anduin injected DB routines by wrapping routines in REST API. """
#!/usr/bin/env python

from __future__ import print_function
import sys
import os
import json
import threading
import re
import time
try: # IronPython modules
    # pylint: disable=unused-import
    from System.Diagnostics import Process
    __ANDUIN_ENV__ = True
except ImportError: # Python 2/3 modules
    __ANDUIN_ENV__ = False
try:  # Python 3 modules
    from urllib.request import urlopen, Request
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:  # Python 2 modules
    from urllib2 import urlopen, Request
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

# Fix issues with decoding HTTP responses
reload(sys)
# pylint: disable=no-member
sys.setdefaultencoding('utf8')

def _isPrimitive(var):
    return isinstance(var, (int, float, bool, str))
def _net2dict(obj):
    attrs = (name for name in dir(obj) if not name.startswith('_') and _isPrimitive(obj.__getattribute__(name)))
    objDict = dict()
    for attribute in attrs:
        val = obj.__getattribute__(attribute)
        # IronPython json uses incorrect boolean so change to int
        val = int(val) if isinstance(val, bool) else val
        objDict[attribute] = val
    return objDict

def getAnduinData(anduinGlobals):
    """ Extracts Anduin configs (dut, station, specs) """
    configs = dict(dut={}, station={}, specs={})
    # On Anduin get real configs
    if __ANDUIN_ENV__:
        lclDut = _net2dict(anduinGlobals['slot'].Dut)
        configs['dut'].update(lclDut)
        lclStation = _net2dict(anduinGlobals['station'])
        kvKey = 'translateKeyValDictionary'
        stationConstants = anduinGlobals[kvKey](anduinGlobals['station'].Constants)
        lclStation.update(stationConstants)
        configs['station'].update(lclStation)
        for specName, specDict in anduinGlobals['TestSpecs'].iteritems():
            fullSpecDict = dict(lsl=None, usl=None, details='')
            fullSpecDict.update(specDict.copy())
            if "counts_in_result" in fullSpecDict:
                # IronPython json uses incorrect boolean so change to string
                fullSpecDict["counts"] = str(fullSpecDict["counts_in_result"])
                fullSpecDict["counts_in_result"] = fullSpecDict["counts"]
            configs['specs'][specName] = fullSpecDict
    # Get dummy configs
    else:
        configs['dut'] = anduinGlobals.get('dut', {})
        configs['specs'] = anduinGlobals.get('specs', {})
        configs['station'] = anduinGlobals.get('station', {})
    return configs

def addTestResults(anduinGlobals, results):
    error = None
    results = results if isinstance(results, list) else [results]
    for result in results:
        try:
            addTestResult(anduinGlobals, result)
        except Exception as err:  # pylint: disable=broad-except
            error = err
    return error

def addTestResult(anduinGlobals, result):
    rstName = result.get('name', None)
    rstArgs = result.get('args', [])
    # Special case for storing files (enables supplying src url)
    if rstName == 'AddResultFile':
        rstName = 'AddResultText'
        args = rstArgs
        if len(args) == 3:
            fname = args[0]
            srcURL = args[1]
            dstPath = args[2]
            dstFolder = os.path.dirname(dstPath)
            if not os.path.exists(dstFolder):
                os.makedirs(dstFolder)
            with open(dstPath, 'wb') as fp:
                fp.write(urlopen(srcURL).read())
            rstArgs = [fname, 'Link', str.format('{:s}', dstPath)]
        elif len(args) == 2:
            rstArgs = [args[0], 'Link', args[1]]
        else:
            raise Exception('AddResultFile: args must be [name, url, dst].')
    if rstName in anduinGlobals:
        anduinGlobals[rstName](*rstArgs)
    else:
        print('ADD DB RESULT:', rstName, rstArgs)

def runToCompletion(proxy, timeout=30):
    try:
        startTimeout = timeout
        while proxy.is_alive() and startTimeout > 1:
            time.sleep(2)
            if os.getenv('DEBUG', False):
                print(proxy.testStatus)
            if startTimeout <= 0:
                raise Exception('Start test request timeout occurred.')
            if proxy.testStatus['state'] in ['IDLE']:
                startTimeout -= 0.5
            elif proxy.testStatus['state'] in ['EXCEPTION', 'FAILED', 'PASSED']:
                proxy.shutdown()
                proxy.join()
        # Verify test results
        testStatus = proxy.testStatus
        if testStatus.get('state') == 'EXCEPTION':
            raise Exception('Test failed due to exception {0}.'.format(proxy.testStatus.get('error')))
        elif testStatus.get('state') == ['FAILED', 'PASSED']:
            return testStatus
        else:
            err = testStatus.get('error', 'N/A')
            raise Exception('Test failed due to premature exit (Details: {0}).'.format(err))
    except KeyboardInterrupt:
        if proxy:
            proxy.shutdown()
            proxy.join()
        raise Exception('Test failed due to being killed.')
    except Exception as err:
        raise err

class AnduinRestClient(object):
    """ Acts as Anduin DB proxy via REST client. """
    def __init__(self, anduinGlobals, address, port, pollDelay=2):
        self.anduinGlobals = anduinGlobals
        self.address = address
        self.port = port
        self.pollDelay = pollDelay

    def performRequest(self, uri, payload=None, attempts=3):
        numAttempts = 0
        while True:
            try:
                req = Request(uri, payload) if payload else Request(uri)
                response = urlopen(req)
                if response.code > 299:
                    raise Exception('Response {0} ({1})'.format(response.msg, response.code))
                return response
            except Exception as err:
                time.sleep(0.1)
                numAttempts += 1
                if os.getenv('DEBUG'):
                    print('request failed w/ error', err, numAttempts)
                if numAttempts >= attempts:
                    raise err

    def startTestRequest(self, test):
        try:
            self.performRequest('http://{0}:{1}/api/v1/test/start'.format(self.address, self.port), json.dumps(test))
        except Exception as err:
            raise Exception('Start test request failed w/ error: {0}'.format(err))

    def getTestResults(self, offset=0):
        try:
            response = self.performRequest('http://{0}:{1}/api/v1/test/results?offset={2}'.format(
                self.address, self.port, offset
            ))
            return json.loads(response.read())
        except Exception as err:
            raise Exception('Failed getting test results w/ error: {0}'.format(err))

    def getTestStatus(self):
        try:
            response = self.performRequest('http://{0}:{1}/api/v1/test/status'.format(self.address, self.port))
            return json.loads(response.read())
        except Exception as err:
            raise Exception('Failed getting test status w/ error: {0}'.format(err))

    def stopTestRequest(self):
        try:
            self.performRequest('http://{0}:{1}/api/v1/test/stop'.format(self.address, self.port), json.dumps(dict()), 2)
        except Exception as err:
            raise Exception('Stop test request failed w/ error: {0}'.format(err))

    def runToCompletion(self, test, timeout=15):
        # Request test start
        self.startTestRequest(test)

        # Wait until test finishes or timeout occurs
        isRunning = True
        startTimeout = 15
        status = dict(state='IDLE')
        results = []
        while isRunning:
            time.sleep(self.pollDelay)
            status = self.getTestStatus()
            if os.getenv('DEBUG'):
                print(status)
            if startTimeout <= 0:
                raise Exception('Test start request timeout')
            if status is None or status.get('state') in [None, 'IDLE']:
                startTimeout -= 1
            elif status and status.get('state') in ['EXCEPTION', 'FAILED', 'PASSED']:
                isRunning = False
            else:
                startTimeout = 15
                isRunning = True
            # Retreive and save any new results (DB routines are VERY slow - hide as much latency)
            nResults = self.getTestResults(offset=len(results))
            nResults = nResults.get('results', []) if nResults else []
            # addTestResults(self.anduinGlobals, nResults[len(results):])
            # results = nResults
            addTestResults(self.anduinGlobals, nResults)
            results += nResults
        if status.get('error'):
            raise Exception('Test raised following error: {0}'.format(status['error']))
        return status, results

class AnduinRestServer(threading.Thread):
    """ Acts as Anduin DB proxy via REST server. """
    def __init__(self, anduinGlobals, port):
        super(AnduinRestServer, self).__init__()
        self.anduinGlobals = anduinGlobals
        self.port = port
        self.eventLock = threading.Lock()
        self.testStatus = dict(
            id=None,
            name=None,
            state='IDLE',
            progress=0,
            message=None,
            error=None,
            timestamp=None
        )
        self.testResults = []
        self.server = None
        return

    def getTestStatus(self, handler=None):
        return self.testStatus

    def setTestStatus(self, handler):
        data = handler if isinstance(handler, dict) else handler.get_payload()
        with self.eventLock:
            self.testStatus.update(data)
            self.testStatus['timestamp'] = int(time.time())
            return {}

    def getTestResults(self, handler):
        return {}

    def addTestResultsRequest(self, handler):
        results = handler.get_payload()
        results = results if isinstance(results, list) else [results]
        self.testResults += results
        self.addTestResults(self.anduinGlobals, results)
        return {}

    def addTestResults(self, anduinGlobals, results):
        error = None
        results = results if isinstance(results, list) else [results]
        for result in results:
            try:
                self.addTestResult(anduinGlobals, result)
            except Exception as err:  # pylint: disable=broad-except
                error = err
        return error

    def addTestResult(self, anduinGlobals, result):
        rstName = result.get('name', None)
        rstArgs = result.get('args', [])
        # Special case for storing files (enables supplying src url)
        if rstName == 'AddResultFile':
            rstName = 'AddResultText'
            args = rstArgs
            if len(args) == 3:
                fname = args[0]
                srcURL = args[1]
                dstPath = args[2]
                dstFolder = os.path.dirname(dstPath)
                if not os.path.exists(dstFolder):
                    os.makedirs(dstFolder)
                with open(dstPath, 'wb') as fp:
                    fp.write(urlopen(srcURL).read())
                rstArgs = [fname, 'Link', str.format('{:s}', dstPath)]
            elif len(args) == 2:
                rstArgs = [args[0], 'Link', args[1]]
            else:
                raise Exception('AddResultFile: args must be [name, ].')
        if rstName in anduinGlobals:
            anduinGlobals[rstName](*rstArgs)
        else:
            print('ADD DB RESULT:', rstName, rstArgs)


    def shutdown(self):
        """ Shutdown proxy"""
        if self.server:
            with self.eventLock:
                self.server.shutdown()
                self.server.socket.close()
                self.server = None
                self.testResults = []

    def run(self):
        delegate = self
        class RESTRequestHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                # pylint: disable=return-in-init
                self.routes = {
                    r'^/$': {'file': 'web/index.html', 'media_type': 'text/html'},
                    r'^/api/v1/test/results$': {'GET': delegate.getTestResults, 'POST': delegate.addTestResultsRequest, 'media_type': 'application/json'},
                    r'^/api/v1/test/status$': {'GET': delegate.getTestStatus, 'POST': delegate.setTestStatus, 'media_type': 'application/json'}
                }
                return BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
            def do_HEAD(self):
                self.handle_method('HEAD')
            def do_GET(self):
                self.handle_method('GET')
            def do_POST(self):
                self.handle_method('POST')
            def do_PUT(self):
                self.handle_method('PUT')
            def do_DELETE(self):
                self.handle_method('DELETE')
            def get_payload(self):
                payload_len = int(self.headers.getheader('content-length', 0))
                payload = self.rfile.read(payload_len)
                payload = json.loads(payload)
                return payload
            def handle_method(self, method):
                route = self.get_route()
                if route is None:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write('Route not found\n')
                    return
                if method == 'HEAD':
                    self.send_response(200)
                    if 'media_type' in route:
                        self.send_header('Content-type', route['media_type'])
                    self.end_headers()
                    return
                if method in route:
                    content = route[method](self)
                    if content is not None:
                        self.send_response(200)
                        if 'media_type' in route:
                            self.send_header('Content-type', route['media_type'])
                        self.end_headers()
                        if method != 'DELETE':
                            self.wfile.write(json.dumps(content))
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write('Not found\n')
                else:
                    self.send_resesponse(405)
                    self.end_headers()
                    self.wfile.write(method + ' is not supported\n')
            def get_route(self):
                for path, route in self.routes.iteritems():
                    if re.match(path, self.path):
                        return route
                return None
        self.setTestStatus(dict(
            id=None,
            name=None,
            state='IDLE',
            progress=0,
            passed=None,
            error=None
        ))
        self.server = HTTPServer(('0.0.0.0', self.port), RESTRequestHandler)
        self.testResults = []
        print('Serving from port', self.port)
        self.server.serve_forever()
