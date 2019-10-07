class BaseListener:
    worker = None

    def __init__(self, worker):
        self.worker = worker

    def on_update(self, dt, task_list):
        """
        必须继承实现
        :param dt: 等待时间
        :param task_list: 消息列表
        :return:
        """
        pass

    def on_start(self):
        """
        当worker启动后
        可继承实现
        :return:
        """
        pass

    def on_stop(self):
        """
        当worker停止前
        可继承实现
        :return:
        """
        pass
