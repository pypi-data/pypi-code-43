import collections

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from filelock import FileLock

from redmin.utils import attr
from .base import RedminModel
from .domain import Domain
from .group import Group
from .user import User

cache = collections.defaultdict(dict)

lock = FileLock("redmin_permission.lock")
lock.release(force=True)


@receiver([post_delete, post_save])
def clear_permissions(sender, **kwargs):
    if sender in [Group, User] or issubclass(sender, Permission):
        with lock:
            cache.clear()


def _get_permissions():
    if not cache:
        with lock:
            domains = Domain.objects.all()
            for permission in GroupPermission.objects.all():
                for user in User.objects.filter(group=permission.group):
                    cache[user][permission.domain.get_model()] = permission
            for permission in UserPermission.objects.all():
                cache[permission.user][permission.domain.get_model()] = permission

            for permission in GroupPermission.objects.filter(domain__name=SuperPermissionModel.__name__):
                for user in User.objects.filter(group=permission.group):
                    for domain in domains:
                        model = domain.get_model()
                        if model not in cache[user]:
                            cache[user][model] = permission

            for permission in UserPermission.objects.filter(domain__name=SuperPermissionModel.__name__):
                for domain in domains:
                    model = domain.get_model()
                    if model not in cache[permission.user]:
                        cache[permission.user][model] = permission

            for user in User.objects.all():
                for domain in domains:
                    model = domain.get_model()
                    if model not in cache[user]:
                        cache[user][model] = UserPermission(user=user, domain=domain)

    return cache


class ModelPermission:
    def __init__(self, **kwargs):
        self.removable = kwargs.get("removable")
        self.cloneable = kwargs.get("cloneable")
        self.viewable = kwargs.get("viewable")
        self.savable = kwargs.get("savable")

    @property
    def operable(self):
        return self.viewable or self.removable or self.cloneable


class PermissionItem:
    creatable = "creatable"
    savable = "savable"
    removable = "removable"
    cloneable = "cloneable"
    exportable = "exportable"
    viewable = "viewable"
    listable = "listable"
    selectable = 'selectable'


VALID_ITEMS = set([key for key, _ in vars(PermissionItem).items() if not key.startswith("_")])


class Permission(RedminModel):
    class Meta:
        abstract = True

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    creatable = models.BooleanField("可创建", default=False)
    savable = models.BooleanField("可保存", default=False)
    removable = models.BooleanField("可删除", default=False)
    cloneable = models.BooleanField("可复制", default=False)
    exportable = models.BooleanField("可导出", default=False)
    viewable = models.BooleanField("可查看", default=False)
    listable = models.BooleanField("可列表", default=False)
    selectable = models.BooleanField("可选择", default=True)

    def to_instance_permission(self):
        return ModelPermission(
            removable=self.removable,
            cloneable=self.cloneable,
            viewable=self.viewable,
            savable=self.savable
        )

    @property
    def operable(self):
        return self.viewable or self.removable or self.cloneable

    @classmethod
    def get_permission(cls, user, model):
        if not user or not model:
            return None
        return _get_permissions()[user][model]

    @classmethod
    def has_permission(cls, user, model, item):
        if item in VALID_ITEMS:
            return attr(cls.get_permission(user, model), item)


class GroupPermission(Permission):
    class Meta:
        verbose_name_plural = verbose_name = "权限(用户组)"
        unique_together = (('group', 'domain'),)

    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class UserPermission(Permission):
    class Meta:
        verbose_name_plural = verbose_name = "权限(用户)"
        unique_together = (('user', 'domain'),)

    user = models.ForeignKey(User, on_delete=models.CASCADE)


class SuperPermissionModel(RedminModel):
    """
    代表所有模型，一般用在admin用户组/用户下
    """

    class Meta:
        verbose_name_plural = verbose_name = "超級模型"
