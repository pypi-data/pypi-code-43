
NAME = 'pansy'

CMD_CLIENT_REQ              = 10  # 透传client请求
CMD_CLIENT_CLOSED           = 20  # 客户端连接被关闭

CMD_WRITE_TO_WORKER         = 100 # 给worker发送消息

CMD_WORKER_ASK_FOR_TASK     = 210 # 请求任务

CMD_WRITE_TO_USERS          = 230 # 主动下发
CMD_CLOSE_USERS             = 250 # 关闭多个客户端

# 重连等待时间
RECONNECT_INTERVAL = 1


DEFAULT_CONFIG = {
    'HOST': '127.0.0.1',
    'PORT': 9700,

    # 启动的room id 列表，闭区间
    'ROOM_ID_BEGIN': None,
    'ROOM_ID_END': None,

    'DEBUG': False,

    'BOX_CLASS': 'netkit.box.Box',

    'LISTENER_CLASS': None,

    'NAME': NAME,

    'CONN_TIMEOUT': 3,

    'STOP_TIMEOUT': None,

    'FPS': 10,

    # recv chunk大小
    'RECV_CHUNK_SIZE': 4096,
}
