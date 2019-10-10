from ...share.log import logger


class Request:
    """
    请求
    """

    app = None
    task = None
    box = None
    is_valid = False
    route_rule = None

    def __init__(self, app, task):
        self.app = app
        self.task = task
        self.is_valid = self._parse_raw_data()

        self.write_to_users = self.app.write_to_users
        self.close_users = self.app.close_users

    def _parse_raw_data(self):
        if not self.task.body:
            return True

        try:
            self.box = self.app.box_class()
        except Exception as e:
            logger.error('parse raw_data fail. e: %s, request: %s', e, self)
            return False

        if self.box.unpack(self.task.body) > 0:
            self._parse_route_rule()
            return True
        else:
            logger.error('unpack fail. request: %s', self)
            return False

    def _parse_route_rule(self):
        if self.cmd is None:
            return

        route_rule = self.app.router.get_route_rule(self.cmd)
        if route_rule:
            # 在app层，直接返回
            self.route_rule = route_rule
            return

    @property
    def cmd(self):
        try:
            return self.box.cmd
        except:
            return None

    @property
    def view_func(self):
        return self.route_rule['view_func'] if self.route_rule else None

    @property
    def endpoint(self):
        if not self.route_rule:
            return None

        return self.route_rule['endpoint']

    def write_to_client(self, data):
        """
        写回响应
        :param data:
        :return:
        """
        data = data or dict()

        if isinstance(data, dict):
            data.update(
                cmd=self.box.cmd,
                sn=self.box.sn,
            )

        self.app.write_to_users([
            ([self.task.uid], data)
        ])

    def __repr__(self):
        return '<%s cmd: %r, endpoint: %s, task: %r>' % (
            type(self).__name__, self.cmd, self.endpoint, self.task
        )