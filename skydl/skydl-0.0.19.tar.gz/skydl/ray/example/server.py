# -*- coding: utf-8 -*-
"""
https://github.com/ray-project/ray/blob/master/examples/newsreader/server.py
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
import ray
import requests
import traceback
from skydl_experience.main.recommend_ranking_task import predict_with_load_model


@ray.remote
def f1():
    # import time
    def print_something():
        print("ray-123")
    print_something()
    return ray.services.get_node_ip_address()


@ray.remote
class NewsServer(object):

    def __init__(self):
        print("Server init...")

    def retrieve_feed(self, url):
        response = requests.get(url)
        print(response)
        return {"channel": {"title": "title122",
                            "link": "linke11",
                            "url": "url12"},
                "items": "[123,22]"}

    def like_item(self, url, aa):
        print("NewsServer like_item...")
        print("url=", url, "===", aa)
        return url

    def remote_exec(self, url, aa):
        results = ray.get([f1.remote() for i in range(100)])
        print("remote_exec=", results)
        return results

    def rank(self, memberId, contentIds):
        return predict_with_load_model(member_id=memberId,
                                       content_ids=contentIds,
                                       model_dir="/tmp/super_model_file_saved_dir",
                                       model_version=33)

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)


@app.route("/api/recommend/rank", methods=["POST"])
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
            result_join = ",".join([str(i) for i in result])
        except:
            print(".........dispatcher error")
            ray.shutdown()
            ray.init(redis_address=dispatcher.server.redis_address, ignore_reinit_error=True)
            print(ray.nodes())
            new_redis_address = dispatcher.server.redis_address
            dispatcher.server = NewsServer.remote()
            dispatcher.server.redis_address = new_redis_address
            method = getattr(dispatcher.server, method_name)
            result = ray.get(method.remote(**method_args))
            result_join = ",".join([str(i) for i in result])
            print(".........dispatcher error ok")
        result_with_stauts = {"success": True, "code": 0, "msg": "", "result": result_join}
        return jsonify(result_with_stauts)
    else:
        result_with_stauts = {"success": False, "code": -1, "msg": "", "result": ""}
        return jsonify(result_with_stauts)


@app.route("/api/demo", methods=["POST"])
def dispatcher1():
    req = request.get_json()
    method_name = req["method_name"]
    method_args = req["method_args"]
    print("method_name", method_name)
    print("method_args", method_args)
    print("dispatcher.server.redis_address=", dispatcher.server.redis_address)
    if hasattr(dispatcher.server, method_name):
        method = getattr(dispatcher.server, method_name)
        # Doing a blocking ray.get right after submitting the task
        # might be bad for performance if the task is expensive.
        try:
            result = ray.get(method.remote(**method_args))
        except:
            print(".........dispatcher error")
            ray.shutdown()
            ray.init(redis_address=dispatcher.server.redis_address, ignore_reinit_error=True)
            print(ray.nodes())
            dispatcher.server = NewsServer.remote()
            method = getattr(dispatcher.server, method_name)
            result = ray.get(method.remote(**method_args))
            print(".........dispatcher error ok")
        print("result=" + str(result))
        return jsonify(result)
    else:
        return jsonify({"error": "method_name '" + method_name + "' not found"})


if __name__ == "__main__":
    """
    $ps aux | grep plasma_store
    $ps aux | grep plasma_manager
    $ps aux | grep local_scheduler
    $ps aux | grep raylet
    $ps aux | grep ray
    $ps aux | grep plasma
    $远程同步文件 rsync -avH /xxx/xx-xx.jar  www@xx.xx.xx.xx:/xxx/
    $unzip /xxx/xx-xx.jar -d /xxx/xx-xx/spark-python/
    $ps -ef | grep 'ray_worker' | grep -v grep | awk '{print $2}' | xargs -r kill -9
    mac单机调试
    $ray stop;rm -rf /tmp/ray;ps -ef | grep 'ray' | grep -v grep | awk '{print $2}' | xargs kill -9;ray start --head --redis-port=6379 --redis-shard-ports=6380 --node-manager-port=12345 --object-manager-port=12346 --object-store-memory=1000000000 --redis-max-memory=2000000000 --include-webui
    mac head:
    $ray stop;rm -rf /tmp/ray;ps -ef | grep 'ray' | grep -v grep | awk '{print $2}' | xargs kill -9;ray start --head --redis-port=6379 --redis-shard-ports=6380 --node-manager-port=12345 --object-manager-port=12346 --object-store-memory=1000000000 --redis-max-memory=2000000000 --include-webui
    linux head(daily):
    $ray stop;rm -rf /tmp/ray;ps -ef | grep 'ray' | grep -v grep | awk '{print $2}' | xargs -r kill -9;ray start --head --redis-port=6379 --redis-shard-ports=6380 --node-manager-port=12345 --object-manager-port=12346 --object-store-memory=4000000000 --redis-max-memory=2000000000 --include-webui
    linux node:
    $ray stop;rm -rf /tmp/ray;ps -ef | grep 'ray' | grep -v grep | awk '{print $2}' | xargs -r kill -9;ray start --redis-address=192.168.xx.27:6379 --node-manager-port=12345 --object-manager-port=12346
    或启动webui $ray start --head --redis-port=6379 --redis-shard-ports=6380 --node-manager-port=12345 --object-manager-port=12346 --include-webui
    $ray start --head --redis-port=6379 --include-webui
    other node $ray start --redis-address="192.168.xx.86:6379"
    或$ray start --redis-address=192.168.xx.89:6379 --node-manager-port=12345 --object-manager-port=12346
    或者自动执行：$ray up /Users/tony/myfiles/spark/share/python-projects/deep_trading/contrib_lib/ray/ray-config.yaml
    https://ray.readthedocs.io/en/latest/using-ray-on-a-cluster.html
    https://github.com/ray-project/ray/issues/4393
    https://github.com/ray-project/ray/issues/4476
    https://github.com/ray-project/ray/issues/4295
    https://github.com/ray-project/ray/issues/2456
    https://github.com/ray-project/ray/issues/2419
    https://github.com/ray-project/ray/issues/3644
    当前python程序应该要运行在head node主机上，如果head node挂了，则在head节点先ray stop 再 ray start即可继续业务逻辑
    注意：当前程序main方法要运行在head node主机上，如果head node挂了，程序连不上plasma，则需要1. $ps -ef | grep ray, kill server.py, kill 僵尸ray_worker进程 2. $ray stop, 3. head node挂了不需要这步：remove /tmp/ray目录，4. 然后$ray start，5.再重新执行server.py
    """
    try:
        redis_address = "localhost:6379"
        ray.init(redis_address=redis_address, ignore_reinit_error=True)
        print(ray.nodes())
        dispatcher.server = NewsServer.remote()
        dispatcher.server.redis_address = redis_address
        http_server = WSGIServer(('', 8093), app)
        http_server.serve_forever()
    except:
        print("ray error occured at ray.init()...")
        traceback.print_exc()



