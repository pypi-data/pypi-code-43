from mg_app_framework import get_logger

from .port_detect import is_port_open
from .weixin_alarm import send_alarm


async def detect_mongodb_cluster_ip_port(mongodb_cluster_name, mongodb_cluster_ip_port):
    for ip, port_list in mongodb_cluster_ip_port.items():
        for port in port_list:
            if await is_port_open(ip, port):
                alarm_message = '{}{}节点端口{}服务正常'.format(mongodb_cluster_name, ip, port)
            else:
                alarm_message = '{}{}节点端口{}服务异常'.format(mongodb_cluster_name, ip, port)
                await send_alarm(alarm_message)
            get_logger().info(alarm_message)
