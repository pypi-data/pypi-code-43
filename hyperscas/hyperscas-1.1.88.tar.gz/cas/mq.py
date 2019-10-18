import logging
import traceback
from datetime import datetime
from .utils import get_user_group_model
from django.conf import settings
from django.contrib.auth import get_user_model
from hyperstools.mq.lib import Queue
from .models import Domain

PUBLISH_QUEUE = settings.HAC_PUBLISH_MQ
User = get_user_model()
UserGroup = get_user_group_model()

logger = logging.getLogger('tools')

def callback(body):
    """
    监听到hac消息后的回调函数
    :param body: hac的消息体
    :return:
    """
    AuthMQ(body).run()


class AuthMQ(object):
    service = settings.SERVICE

    def __init__(self, body):
        self.body = body
        self.errField = None
        self.domain = Domain.objects.first()
        try:
            self.uuid = body["uuid"]
            self.method = body["method"]
            self.resource = body["resource"]
            self.data = body["body"]["data"]
            self.name = self.data.get("name", None)
            self.email = self.data.get("email", '')
            self.group = self.data.get("group", None)
            self.role = self.data.get("role", None)
            self.creator = self.data.get("creator", None)
            self.groupId = self.data.get("groupId", None)
            self.code = 200000
        except KeyError as e:
            self.code = 200002
            e = str(e).replace("'", "")
            self.errField = {e: {
                "code": 200002,
                "message": f"{e} is required"
            }}

    def run(self):
        try:
            self.resourceHandler()
        except AttributeError:
            self.code = 200002
            self.errField = self.errField or {"method": {"code": 200002, "message": f"{self.method} is unsupported"}}
        except Exception:
            logger.error(traceback.format_exc())
            self.code = 200001
        self.publish()

    def publish(self):
        body = self.body
        body.update(
            uuid=self.uuid,
            service=self.service,
            domain=self.domain.host,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        if self.code == 200000:
            #  监听到的body没有出现字段错误, 去掉body["body"]中data, 加上code和result
            body["body"].pop("data")
            body["body"].update({
                "code": self.code,
                "result": self.data,
            })
        with Queue(PUBLISH_QUEUE) as queue:
            queue.publish(body)

    def resourceHandler(self):
        if self.resource.startswith("/users"):
            self.code = getattr(UserResource(), self.method.lower())(self)
        elif self.resource.startswith("/groups"):
            self.code = getattr(UserGroupResource(), self.method.lower())(self)


class UserResource(object):

    def __init__(self):
        self.resultCode = 200000

    def get(self):
        pass

    def post(self, hac):
        queryset = User.objects.filter(email=hac.email)
        user = queryset.exists() and queryset.first() or User()
        user.email = hac.email
        user.username = hac.name
        user.role = hac.role
        user.is_active = 1
        if hac.group:
            group, created = UserGroup.objects.get_or_create(name=hac.group)
            user.usergroup = group

        setParamsExceptHac = getattr(user, "setParamsExceptHac", None)
        if setParamsExceptHac:
            setParamsExceptHac()  # 如果app的User model有除hac消息之外的字段，app须实现此接口
        user.save()
        return self.resultCode

    def put(self, hac):
        return self.patch(hac)

    def patch(self, hac):
        userInstance = User.objects.filter(email=hac.email)
        if userInstance.exists():
            userInstance = userInstance.first()
            userInstance.username = hac.name
            userInstance.role = hac.role
            userInstance.save()
        else:
            pass  # 用户不存在不报错，认为任务成功
        return self.resultCode

    def delete(self, hac):
        userInstance = User.objects.filter(email=hac.email)
        if userInstance.exists():
            userInstance = userInstance.first()
            userInstance.is_active = 0
            userInstance.save()
        else:
            pass
        return self.resultCode


class UserGroupResource(object):
    def __init__(self):
        self.resultCode = 200000

    def get(self):
        pass

    def post(self, hac):
        creator = User.objects.filter(email=hac.creator)
        group = UserGroup.objects.filter(name=hac.name)
        group = group and group[0] or UserGroup(name=hac.name)
        group.group_id = hac.groupId
        if creator:
            group.creator_id = creator[0].id
        group.status = "ACTIVE"
        setParamsExceptHac = getattr(group, "setParamsExceptHac", None)
        if setParamsExceptHac:
            setParamsExceptHac()  # 如果app的UserGroup model有除hac消息之外的字段，app须实现此接口
        group.save()
        return self.resultCode

    def put(self, hac):
        return self.patch(hac)

    def patch(self, hac):
        try:
            group = UserGroup.objects.get(group_id=hac.groupId)
            hac.name and setattr(group, "name", hac.name)
            group.save()
        except UserGroup.DoesNotExist:
            self.resultCode = 200404
        finally:
            return self.resultCode

    def delete(self, hac):
        try:
            group = UserGroup.objects.get(name=hac.name)
            group.status = "PAUSED"
            group.save()
        except UserGroup.DoesNotExist:
            self.resultCode = 200404
        finally:
            return self.resultCode
