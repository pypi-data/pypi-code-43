import json
import requests
import dk_api_helpers

class DKConnection():
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        payload = {'username': username, 'password': password}
        r = requests.post('https://%s/v2/login' % hostname, data=payload)
        if r.text == 'Credentials are invalid':
            raise Exception
        self.token = r.text

    def createOrder(self, kitchen, recipe, variation):
        headers = {'content-type': 'application/json', 'authorization': 'bearer ' + self.token}
        url = 'https://%s/v2/order/create/%s/%s/%s' % (self.hostname, kitchen, recipe, variation)
        return requests.put(url, headers=headers)

    def OrderRunInfo(self, kitchen, order_run_id):
        url = "https://%s/v2/order/details/%s" % ( self.hostname, kitchen)
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = {'serving_hid' : order_run_id, 'testresults': True}
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if "does not exist." in r.text:
            raise Exception("Order run id %s not found." % order_run_id )
        return json.loads(r.text)

    def TestsFromOrderRun(self, kitchen, order_run_id):
        order = self.OrderRunInfo(kitchen, order_run_id)
        try:
            testStr = order['servings'][0]['testresults']
        except KeyError:
            print "Error: No tests in OrderRun Object"
        return dk_api_helpers.parseTestString(testStr)
