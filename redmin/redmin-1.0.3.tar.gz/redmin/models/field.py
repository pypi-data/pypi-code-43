from collections import defaultdict

import django.apps
from django.db import models
from django.db.models import ForeignKey
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from redmin.utils import attr, cache, synchronized, clear_cache
from .base import RedminModel
from .domain import Domain
from .group import Group
from .user import User


@cache
@synchronized
def get_all_default_fields():
    result = defaultdict(dict)
    for field in Field.objects.all():
        model = field.base.get_model()
        result[model][field.attribute] = field
    return result


@cache
@synchronized
def get__all_user_fields():
    result = defaultdict(lambda: defaultdict(dict))
    for user_field in UserField.objects.all():
        field = user_field.field.clone()
        for f in CommonField._meta.fields:
            setattr(field, f.name, getattr(user_field, f.name))
        result[user_field.user][user_field.field.base.get_model()][field.attribute] = field
    return result


@cache
@synchronized
def get_all_group_fields():
    result = defaultdict(lambda: defaultdict(dict))
    for group_field in GroupField.objects.all():
        model = group_field.field.base.get_model()
        field = group_field.field.clone()
        for f in CommonField._meta.fields:
            setattr(field, f.name, getattr(group_field, f.name))
        result[group_field.group][model][field.attribute] = field
    return result


def get_model_fields(model, user=None):
    fields = get_all_default_fields().get(model, {}).copy()
    if user:
        group_fields = get_all_group_fields().get(user.group, {}).get(model, {})
        fields.update(group_fields)
        user_fields = get__all_user_fields().get(user, {}).get(model, {})
        fields.update(user_fields)
    return fields


class CommonField(RedminModel):
    class Meta:
        abstract = True

    title = models.CharField("显示名称", max_length=200)
    sequence = models.IntegerField("序号")
    listable = models.BooleanField("在列表中显示", default=True)
    formable = models.BooleanField("在表单中显示", default=True)
    sortable = models.BooleanField("可排序", default=True)
    exportable = models.BooleanField("可导出", default=True)
    nullable = models.BooleanField("可以为空", default=False)
    unique = models.BooleanField("是否唯一性", default=False)
    default = models.CharField("默认值", max_length=500, null=True, blank=True)
    form_editable = models.BooleanField("表单可编辑", default=True)
    list_editable = models.BooleanField("列表可编辑", default=False)
    searchable = models.BooleanField("可搜索", default=False, help_text="通过一个关键字搜索选中的每一列")
    filterable = models.BooleanField("可过滤", default=True, help_text="是否可在列表任务栏过滤")
    serializable = models.BooleanField("可序列化", default=True, help_text="RestAPI里是否可以序列化")
    help_text = models.TextField("帮助文本", null=True, blank=True)


DATA_TYPES = {
    'AutoField': 'integer',
    'BigAutoField': 'integer',
    'BooleanField': 'boolean',
    'CharField': 'string',
    'DateField': 'date',
    'DateTimeField': 'datetime',
    'DecimalField': 'float',
    'DurationField': 'integer',
    'FileField': 'string',
    'FilePathField': 'string',
    'FloatField': 'float',
    'IntegerField': 'integer',
    'BigIntegerField': 'integer',
    'IPAddressField': 'string',
    'GenericIPAddressField': 'string',
    'NullBooleanField': 'boolean',
    'OneToOneField': 'integer',
    'PositiveIntegerField': 'integer',
    'PositiveSmallIntegerField': 'integer',
    'SlugField': 'string',
    'SmallIntegerField': 'smallint',
    'TextField': 'text',
    'TimeField': 'time',
    'UUIDField': 'string',
}


class BaseField(RedminModel):
    """
    These Fields cannot be changed
    """

    class Meta:
        abstract = True

    base = models.ForeignKey(Domain, on_delete=models.CASCADE, verbose_name="父模型", related_name="base")
    attribute = models.CharField("字段名称", max_length=100)
    attribute_domain = models.ForeignKey(Domain, verbose_name="字段模型", null=True, blank=True, on_delete=models.CASCADE, related_name="attribute_domain")
    group_sequence = models.IntegerField("分组序号")
    python_type = models.CharField("原生类型", max_length=200)
    data_type = models.CharField("数据类型", max_length=10)
    max_length = models.IntegerField("最大长度", default=0)


class Field(BaseField, CommonField):
    class Meta:
        ordering = ['base', 'group_sequence', 'sequence']
        verbose_name_plural = verbose_name = "字段"

    def __str__(self):
        return f"{self.base},{self.title}({self.attribute})"

    @classmethod
    def get_default_fields(cls, model):
        return get_all_default_fields().get(model, {}).copy()

    @classmethod
    def get_default_field(cls, model, attribute):
        field = cls.get_default_fields(model).get(attribute)
        return field and field.clone()

    @classmethod
    def get_search_attributes(cls, user, model):
        user_fields = cls.get_user_fields(user, model).copy()
        return [field.attribute for field in user_fields.values() if field.searchable]

    @classmethod
    def get_user_fields(cls, user, model):
        return get_model_fields(model, user=user).copy()

    @classmethod
    def get_field(cls, user, model, attribute):
        filed = cls.get_user_fields(user, model).get(attribute)
        return filed and filed.clone()

    @classmethod
    def get_fields(cls, user, model, has_domain=None):
        user_fields = cls.get_user_fields(user, model)
        result = {}
        for attribute, field in user_fields.items():
            if has_domain is None or (has_domain is True and field.attribute_domain) or (
                    has_domain is False and not field.attribute_domain):
                result[attribute] = field.clone()
        return result

    @property
    def model(self):
        if self.attribute_domain:
            return self.attribute_domain.get_model()

    @property
    def class_name(self):
        return attr(self.model, "__name__")

    @classmethod
    def get_group_fields(cls, user, model, has_domain=None, reverse=False):
        result = []
        group_sequence = -1
        fields = []
        for field in cls.get_fields(user, model, has_domain).values():
            if group_sequence != field.group_sequence:
                group_sequence = field.group_sequence
                if fields:
                    result.append(fields)
                fields = []
            fields.append(field)
        if fields:
            result.append(fields)

        for i in range(len(result)):
            fields = sorted(result[i], key=lambda f: (f.group_sequence, f.sequence))
            result[i] = list(reversed(fields)) if reverse else fields

        return result


class GroupField(CommonField):
    class Meta:
        ordering = ["group", 'field']
        verbose_name_plural = verbose_name = "字段(用户组)"
        unique_together = [("group", "field")]

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="默认字段")

    def __str__(self):
        return f"{self.group},{self.title}({self.field.attribute})"


class UserField(CommonField):
    class Meta:
        ordering = ["user", 'field']
        verbose_name_plural = verbose_name = "字段(用户)"
        unique_together = [("user", "field")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user},{self.title}({self.field.attribute})"


def get_attributes(cls, name=None):
    result = []
    foreign_fields = [(attr(f, "remote_field.model"), attr(f, "remote_field.field.name")) for f in
                      attr(cls, '_meta.fields') if issubclass(type(attr(f, "remote_field.field")), ForeignKey)]
    for foreign_model, foreign_attribute in foreign_fields:
        new_name = f"{name}.{foreign_attribute}" if name else foreign_attribute
        new_names = get_attributes(foreign_model, new_name)
        if new_names:
            result += new_names
        else:
            result.append(new_name)

    return result


def contains_chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def init_fields(type_map):
    basic_fields = [f.name for f in attr(BaseField, '_meta.fields')]
    new = []
    updates = []
    for model in django.apps.apps.get_models():
        if issubclass(model, RedminModel):
            group_sequence = 100
            base = type_map.get(model)
            attributes = []
            exists = {f.attribute: f for f in Field.objects.filter(base=base).all()}

            def check(field):
                exists_field = exists.get(field.attribute)
                if exists_field:
                    need_update = False
                    for key in basic_fields:
                        if attr(field, key) != attr(exists_field, key):
                            setattr(exists_field, key, attr(field, key))
                            need_update = True
                    if need_update:
                        updates.append(exists_field)
                        if len(updates) > 50:
                            Field.objects.bulk_update(updates, fields=basic_fields)
                            updates.clear()
                else:
                    new.append(field)
                    if len(new) > 50:
                        Field.objects.bulk_create(new)
                        new.clear()

            fields = [field for field in attr(model, '_meta.fields') if not attr(field, "remote_field")]
            for sequence, field in enumerate(fields, start=1):
                attribute = attr(field, "name")
                title = attr(field, '_verbose_name') or attribute
                attributes.append(attribute)
                field_type = type(field)
                python_type = f"{field_type.__module__}.{field_type.__name__}"
                form_editable = formable = attr(field, "form_editable", True) and attribute != "id"
                list_editable = attr(field, "list_editable", False) and attribute != "id"
                check(Field(
                    base=base,
                    attribute=attribute,
                    attribute_domain=None,
                    group_sequence=group_sequence,
                    python_type=python_type,
                    data_type=DATA_TYPES.get(python_type.split(".")[-1], "string"),
                    max_length=attr(field, "max_length") or 0,
                    serializable=True,
                    sequence=sequence * 5,
                    title=title,
                    nullable=attr(field, "null"),
                    form_editable=form_editable is not False,
                    list_editable=list_editable is not False,
                    formable=formable is not False,
                    help_text=attr(field, "help_text"),
                ))

            last_attribute, group_sequence = None, 0
            for attribute in get_attributes(model):
                names = attribute.split(".")
                for sequence in range(1, len(names) + 1):
                    sub_attribute, cls, title, field = ".".join(names[0:sequence]), model, None, None
                    if last_attribute and not sub_attribute.startswith(last_attribute):
                        group_sequence += 1
                    for name in sub_attribute.split("."):
                        field = attr(cls, f"{name}.field")
                        title = attr(field, "verbose_name")
                        cls = attr(field, f"remote_field.model")
                    form_editable = formable = attr(field, "form_editable", True) and sub_attribute != "id"
                    list_editable = attr(field, "list_editable", False) and sub_attribute != "id"
                    python_type = ForeignKey.__module__ + "." + ForeignKey.__name__
                    if not contains_chinese(title):
                        cls_verbose_name = attr(cls, "_meta.verbose_name")
                        if contains_chinese(cls_verbose_name):
                            title = cls_verbose_name
                    check(Field(
                        base=base,
                        group_sequence=group_sequence,
                        sequence=len(names) - sequence,
                        attribute=sub_attribute,
                        attribute_domain=type_map[cls],
                        title=title,
                        nullable=attr(field, "null"),
                        form_editable=form_editable is not False,
                        list_editable=list_editable is not False,
                        formable=formable is not False,
                        python_type=python_type,
                        data_type=DATA_TYPES.get(python_type.split(".")[-1], "string"),
                        max_length=attr(field, "max_length") or 0,
                        serializable=True,
                        help_text=attr(field, "help_text"),
                    ))
                    attributes.append(sub_attribute)
                    last_attribute = sub_attribute

            Field.objects.filter(base=base).exclude(attribute__in=attributes).delete()
    Field.objects.bulk_create(new)
    Field.objects.bulk_update(updates, fields=basic_fields)


@receiver([post_save, post_delete])
def handle_model_change(sender, **kwargs):
    if sender in [Group, User, Field, UserField, GroupField]:
        clear_cache(get__all_user_fields)
        clear_cache(get_all_default_fields)
        clear_cache(get_all_group_fields)
