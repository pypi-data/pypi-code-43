# -*- coding: UTF-8 -*-

import warnings
import logging
from app.base.route import base
# from app.main.route import main
# from app.log.route import log
from app.test_mysql.route import test_mysql
from configs.com_config import com_config
from configs.db_config import db, db_config
from configs.aps_config import scheduler, aps_config
from configs.application import app
from common.model_helper import CacheSave


# gunicorn -b 0.0.0.0:12334 -k gthread -w 2 --timeout 60 entry:app --log-level=info --reload
# gunicorn -b 0.0.0.0:12334 -k gevent -w 2 --timeout 60 entry:app --log-level=info --reload
# wrk -t10 -c100 -d60s -T30s --latency http://192.168.199.249:12335/db/

# 过滤一切警告
warnings.filterwarnings(action='ignore')


def create_app(app):
    app.config.from_object(com_config)
    app.config.from_object(db_config)
    app.config.from_object(aps_config)
    """ zone结构，设备增删改查地址 """
    app.register_blueprint(base, url_prefix='/base')
    # """ 客流，顾客数查询 """
    # app.register_blueprint(main, url_prefix='/main')
    # """ 处理探针数据，存入日志 """
    # app.register_blueprint(log, url_prefix='/log')
    """ 测试数据库的性能 """
    app.register_blueprint(test_mysql, url_prefix='/db')
    db.init_app(app)
    scheduler.init_app(app)
    return app



app = create_app(app)
logging.basicConfig()


@app.before_first_request
def init_db():
    db.create_all()
    scheduler.start()



# @app.before_request
# def before_request():
#     request.cache_triggers = [] # 压根没用上

# @app.after_request              # 如果没有异常，则执行这个
# def after_request(response):
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = (
#         'PUT,GET,POST,DELETE,VIEW')
#     response.headers['Access-Control-Allow-Headers'] = (
#         'Content-Type,Authorization,StoreToken')
#     return response
#
@app.teardown_request           # 不管怎么样（就算产生异常），也执行这个
def shutdown_session(exception=None):
    """每次请求后, 移除session"""
    db.session.remove()

# @app.errorhandler(DataBaseCommitError)  # 错误处理
# def database_commit_error(e):
#     """捕获数据库提交异常, 并统一格式返回"""
#     return sx_json(404, msg=str(e))
"""
gunicorn3 -b 0.0.0.0:12334 -k gevent -w 4 --timeout 60 entry:app --log-level=info --reload --max-requests 100000 --max_requests_jitter 5000
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12334)



