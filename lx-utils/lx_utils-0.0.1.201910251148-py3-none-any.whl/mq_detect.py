import requests, json
from mg_app_framework import get_logger
from .port_detect import is_port_open
from .weixin_alarm import send_alarm


def get_rabbitmq_url(ip, port):
    return "http://" + ip + ":" + port


async def start_detect_rabbitmq_cluster(cluster_name, cluster_ip_port, rabbitmq_user, rabbitmq_password,
                                        max_msg_num):
    await detect_rabbitmq_cluster_port_status(cluster_name, cluster_ip_port)
    await get_rabbitmq_cluster_overview_info(cluster_name, cluster_ip_port, rabbitmq_user, rabbitmq_password,
                                             max_msg_num)


async def detect_rabbitmq_cluster_port_status(cluster_name, cluster_ip_port):
    # 检测集群端口状态
    for ip, port_list in cluster_ip_port.items():
        for port in port_list:
            if await is_port_open(ip, port):
                alarm_message = '{}{}节点端口{}服务正常'.format(cluster_name, ip, port)
            else:
                alarm_message = '{}{}节点端口{}服务异常'.format(cluster_name, ip, port)
                await send_alarm(alarm_message)
            get_logger().info(alarm_message)


async def get_rabbitmq_cluster_overview_info(cluster_name, cluster_ip_port, rabbitmq_user, rabbitmq_password,
                                             max_msg_num):
    for ip, port_list in cluster_ip_port.items():
        url = get_rabbitmq_url(ip, '15672') + "/api/overview"
        get_logger().info('url:%s', url)
        res = requests.get(url, auth=(rabbitmq_user, rabbitmq_password))
        overview = json.loads(res.text)
        messages_ready = overview['queue_totals']['messages_ready']

        if int(messages_ready) > max_msg_num:
            alarm_message = '{}{}节点未消费消息数大于{}'.format(cluster_name, ip, max_msg_num)
            await send_alarm(alarm_message)
