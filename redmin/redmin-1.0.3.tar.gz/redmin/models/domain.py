import django.apps
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from filelock import FileLock

from redmin.utils import attr
from .base import RedminModel
from .group import Group
from .user import User

lock = FileLock("redmin_domain.lock")
lock.release(force=True)

cache = dict()


@receiver([post_save, post_delete])
def handle_model_change(sender, **kwargs):
    if sender in [Domain, GroupDomain, UserDomain]:
        with lock:
            cache.clear()


def init_domain():
    from redmin.models import Domain, RedminModel
    domains = {}
    for domain in Domain.objects.all():
        domains[domain.app + "-" + domain.name] = domain
    all_models = {}
    for model in [model for model in django.apps.apps.get_models() if issubclass(model, RedminModel)]:
        app = model.__module__.split(".")[0]
        name = model.__name__
        all_models[app + "-" + name] = model

    type_map = {}
    for flag, model in all_models.items():
        domain = domains.get(flag)
        title = model._meta.verbose_name
        if domain:
            if domain.title != title:
                domain.title = title
                domain.save()
        else:
            app, name = flag.split("-")
            domain = Domain.objects.create(app=app, name=name, title=title)
        type_map[model] = domain
    for flag, domain in domains.items():
        if flag not in all_models:
            domain.delete()

    return type_map


def get_map():
    from collections import defaultdict
    if not cache:
        with lock:
            domains = {domain.get_key(): domain for domain in Domain.objects.all()}
            cache['domains'] = domains
            cache['models'] = {model.get_domain_key(): model for model in django.apps.apps.get_models() if
                               issubclass(model, RedminModel)}

            group_domains = defaultdict(dict)
            for c in GroupDomain.objects.all():
                group_domains[str(c.group.id)][c.get_key()] = c
            cache['group_domains'] = group_domains

            user_domains = defaultdict(dict)
            for c in UserDomain.objects.all():
                user_domains[str(c.user.id)][c.get_key()] = c
            cache['user_domains'] = group_domains

    return cache


@receiver(post_save)
@receiver(post_delete)
def clear_map(sender, **kwargs):
    if sender in [Group, User] or issubclass(sender, BaseDomain):
        with lock:
            cache.clear()


class BaseDomain(RedminModel):
    class Meta:
        abstract = True

    title = models.CharField("描述", max_length=100)
    sequence = models.IntegerField("排序", default=99999)
    app = models.CharField("应用", max_length=100)
    name = models.CharField("名称", max_length=100)

    def __str__(self):
        return self.title

    @classmethod
    def get(cls, app, name):
        return cls.get_by_key(f"{app}.{name}")

    @classmethod
    def get_by_user_and_model(cls, user, model):
        cache = get_map()
        key = model.get_domain_key()
        return attr(cache, f'user_domains.{user.id}.{key}') or attr(cache, f'group_domains.{user.group_id}.{key}') or attr(cache, f'domains.{key}')

    @classmethod
    def get_by_model(cls, model):
        return get_map()['domains'][model.get_domain_key()]

    def get_model(self):
        return get_map()['models'][self.get_key()]

    def get_key(self):
        return self.app + "_" + self.name

    @classmethod
    def get_by_key(cls, key):
        return get_map()['domains'][key]

    @classmethod
    def get_model_by_key(cls, key):
        return get_map()['models'][key]


class Domain(BaseDomain):
    class Meta:
        ordering = ['sequence', "id"]
        verbose_name_plural = verbose_name = "模型"
        unique_together = [("app", "name")]


class GroupDomain(BaseDomain):
    class Meta:
        ordering = ['group', 'sequence']
        verbose_name_plural = verbose_name = "用户组模型"
        unique_together = ("group", "app", "name")

    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class UserDomain(BaseDomain):
    class Meta:
        ordering = ['user', 'sequence']
        verbose_name_plural = verbose_name = "用户模型"
        unique_together = ("user", "app", "name")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
