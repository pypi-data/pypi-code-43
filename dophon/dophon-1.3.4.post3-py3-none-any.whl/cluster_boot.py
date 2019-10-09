# coding: utf-8
from multiprocessing import Process, freeze_support
from threading import Thread
import time, socket, random
from flask import request, make_response
from urllib3 import PoolManager
from dophon import properties
from dophon_logger import *

logger = get_logger(eval(properties.log_types))

logger.inject_logger(globals())

ports = []  # 记录监听端口

proxy_clusters = {}

pool = PoolManager()


def main_freeze():
    freeze_support()


def redirect_request():
    current_header = {}
    # 迁移当前请求头
    for k, v in request.headers.items():
        current_header[k] = v
    if not current_header.get('Outer'):
        choice_port = random.choice(ports)
        # 添加网关标识
        current_header['Outer'] = 'pass'
        logger.info(f'touch path: {request.path}, touch port: {choice_port} [success]')
        res = pool.request(
            request.method,
            f'127.0.0.1:{choice_port}{request.path}',
            fields=request.json if request.is_json else request.form,
            headers=current_header
        )
        # print(res.headers)
        cell_res = make_response(res.data)
        # 迁移转发的响应头
        for item in res.headers:
            # print(item)
            cell_res.headers[item] = res.headers[item]
        return cell_res


def outer_entity(boot):
    # 重写路由信息(修改为重定向路径)
    boot.get_app().before_request(redirect_request)
    boot.run()


def run_clusters(clusters: int, outer_port: bool = False, start_port: int = 8800, multi_static_fix: bool = False,
                 part_kwargs: dict = {}):
    """
    运行集群式服务器
    :param clusters: 集群个数
    :param outer_port: 是否开启外部端口映射(映射端口为用户配置文件中配置的端口)
    :param start_port: 集群起始监听端口
    :param multi_static_fix: 集群静态文件修复
    :param part_kwargs: 集群节点额外参数(会覆盖默认参数)
    :return:
    """
    from dophon import boot
    for i in range(clusters):
        current_port = start_port + i
        create_cluster_cell(boot=boot, port=current_port, part_kwargs=part_kwargs, cell_static_fix=multi_static_fix)
        ports.append(current_port)
    while len(ports) != clusters:
        time.sleep(5)

    logger.info('启动检测端口监听')
    for port in ports:
        if check_socket(int(port)):
            continue
    logger.info('集群端口: %s ' % ports)
    if outer_port:
        logger.info('启动外部端口监听[%s]' % (properties.port))
        outer_entity(boot)


def action_boot(boot, cell_static_fix: bool):
    boot.fix_static(enhance_power=cell_static_fix)
    boot.fix_template()
    return boot.BeanScan()(boot.run) if cell_static_fix else boot.run


def create_cluster_cell(boot, port, part_kwargs, cell_static_fix: bool):
    kwargs = {
        'host': '127.0.0.1',
        'port': port,
        'run_type': eval(f'boot.{part_kwargs["run_type"] if "run_type" in part_kwargs else "FLASK"}')
    }
    if part_kwargs:
        # 迁移参数
        for k, v in part_kwargs.items():
            if k not in kwargs:
                kwargs[k] = v
    cell_boot = action_boot(boot, cell_static_fix)
    # print(cell_boot)
    # http协议
    from dophon.tools import is_not_windows
    # Linux使用多进程
    # Windows使用多线程
    proc = Process(target=cell_boot, kwargs=kwargs) if is_not_windows() else Thread(target=cell_boot, kwargs=kwargs)
    proc.start()


def check_socket(port: int):
    s = socket.socket()
    flag = True
    while flag:
        try:
            ex_code = s.connect_ex(('127.0.0.1', port))
            flag = False
            return int(ex_code) == 0
        except Exception as e:
            time.sleep(3)
            continue
