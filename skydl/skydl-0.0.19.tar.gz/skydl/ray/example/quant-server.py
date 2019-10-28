# -*- coding: utf-8 -*-
"""
https://github.com/ray-project/ray/blob/master/examples/newsreader/server.py
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
import ray
import traceback


@ray.remote
def f1():
    # import time
    def print_something():
        print("ray-123")
    print_something()
    return ray.services.get_node_ip_address()


@ray.remote
class QuantServer(object):

    def __init__(self):
        print("Quant Server init...")

    def rank(self, memberId, contentIds):
        return "ok..."

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)


@app.route("/api/quant/backtest", methods=["POST"])
# @csrf.exempt
def dispatcher():
    method_name = "rank"
    memberId = request.form['memberId']
    contentIds = request.form['contentIds']
    print("memberId", memberId)
    print("contentIds", contentIds)
    method_args = {"memberId": memberId, "contentIds": contentIds}
    if hasattr(dispatcher.server, method_name):
        method = getattr(dispatcher.server, method_name)
        try:
            result = ray.get(method.remote(**method_args))
        except:
            print(".........dispatcher error")
            ray.shutdown()
            ray.init(redis_address=dispatcher.server.redis_address, ignore_reinit_error=True)
            print(ray.nodes())
            new_redis_address = dispatcher.server.redis_address
            dispatcher.server = QuantServer.remote()
            dispatcher.server.redis_address = new_redis_address
            method = getattr(dispatcher.server, method_name)
            result = ray.get(method.remote(**method_args))
            print(".........dispatcher error ok")
        result_with_stauts = {"success": True, "code": 0, "msg": "", "result": str(result)}
        return jsonify(result_with_stauts)
    else:
        result_with_stauts = {"success": False, "code": -1, "msg": "", "result": ""}
        return jsonify(result_with_stauts)


if __name__ == "__main__":
    """
    $ps aux | grep plasma_store
    $ps aux | grep plasma_manager
    $ps aux | grep local_scheduler
    $ps aux | grep raylet
    $ps aux | grep ray
    $ps aux | grep plasma
    或启动webui $ray start --head --redis-port=6379 --redis-shard-ports=6380 --node-manager-port=12345 --object-manager-port=12346 --include-webui
    $ray start --head --redis-port=6379 --include-webui
    other node $ray start --redis-address="192.168.91.85:6379"
    或$ray start --redis-address=192.168.91.85:6379 --node-manager-port=12345 --object-manager-port=12346
    或者自动执行：$ray up /Users/tony/myfiles/spark/share/python-projects/deep_trading/contrib_lib/ray/ray-config.yaml
    https://ray.readthedocs.io/en/latest/using-ray-on-a-cluster.html
    https://github.com/ray-project/ray/issues/4393
    https://github.com/ray-project/ray/issues/4476
    当前python程序应该要运行在head node主机上，如果head node挂了，则在head节点先ray stop 再 ray start即可继续业务逻辑
    xxx当前程序要运行在head node主机上，如果head node挂了，程序连不上plasma，则需要1. kill server.py, 2. $ray stop, 3. head node挂了不需要这步：remove /tmp/ray目录，4. 然后$ray start，5.再重新执行server.py
    """
    try:
        redis_address = "192.168.95.27:6379"
        ray.init(redis_address=redis_address, ignore_reinit_error=True)
        print(ray.nodes())
        dispatcher.server = QuantServer.remote()
        dispatcher.server.redis_address = redis_address
        http_server = WSGIServer(('', 8093), app)
        http_server.serve_forever()
    except:
        print("ray error occured at ray.init()...")
        traceback.print_exc()



