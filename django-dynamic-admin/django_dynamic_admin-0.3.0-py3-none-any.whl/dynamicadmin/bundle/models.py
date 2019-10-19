from django.db import models
from django.apps import apps
from polymorphic.models import PolymorphicModel
from dynamicadmin.apps import DynamicadminConfig
from django.contrib.contenttypes.models import ContentType


# @see https://code.djangoproject.com/wiki/DynamicModels
def dynamic_model_factory(model_name, attributes, fields, app_label, module=None, base=models.Model):
    if not module:
        module = base.__module__

    class Meta:
        pass

    setattr(Meta, 'app_label', app_label)
    if attributes:
        for key, val in attributes.items():
            setattr(Meta, key, val)

    attrs = {
        '__module__': module,
        'Meta': Meta,
    }

    if fields:
        attrs.update(fields)

    model = type(model_name, (base,), attrs)

    return model


# @todo
def dynamic_field_factory(field_type, content_type=None, module=None, weight=1, **attributes):
    base = getattr(models, field_type)

    class BundleFieldEntity(base):
        def __init__(self, *args):
            self.weight = weight
            super().__init__(*args, **attributes)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            kwargs['weight'] = self.weight
            return name, path, args, kwargs

    field = type(field_type, (BundleFieldEntity,), {})

    if content_type:
        return field(content_type, **attributes)
    return field(**attributes)


def get_bundle_model(app_label, model_name):
    return apps.get_app_config(app_label).get_model(model_name=model_name)


def get_bundle_object(bundle_model, object_name):
    return bundle_model.objects.get(name=object_name)


def get_bundle_objects(bundle_model, **kwargs):
    return bundle_model.objects.filter(**kwargs)


def get_dynamic_models(app_label):
    return apps.get_app_config(app_label).get_models()


def get_dynamic_model(app_label, model_name):
    return apps.get_app_config(app_label).get_model(model_name=model_name)


def get_dynamic_model_objects(dynamic_model, **kwargs):
    return dynamic_model.objects.filter(**kwargs)


class Bundle(models.Model):
    class Meta:
        app_label = DynamicadminConfig.name

    def __str__(self):
        return self._verbose_name

    objects = models.Manager()
    fields = None

    name = models.SlugField(max_length=255, unique=True)
    _verbose_name = models.CharField(max_length=255)

    def get_dynamic_model(self, app_label):
        return get_dynamic_model(app_label, model_name=self.name)

    def create_dynamic_model(self, **kwargs):
        fields = self.get_django_model_fields()
        # @todo cascade/warning/settings
        fields.append(('bundle',
                       models.ForeignKey(self, default=self.pk, editable=False, on_delete=models.DO_NOTHING,
                                         related_name='+')))
        return dynamic_model_factory(self.name, self.get_django_model_attributes(), dict(fields), **kwargs)

    def get_django_model_fields(self):
        return list((field.name, field.get_django_field()) for field in self.fields.all())

    def get_django_model_attributes(self):
        attributes = dict()
        for field in self._meta.get_fields():
            if str(field.name).startswith('_'):
                attributes[field.name[1:]] = getattr(self, field.name)
        return attributes


class Field(PolymorphicModel):
    class Meta:
        app_label = DynamicadminConfig.name
        unique_together = ('bundle', 'name',)

    def __str__(self):
        return self._verbose_name

    field_type = None
    name = models.SlugField(max_length=255)
    weight = models.IntegerField(null=True, blank=True)
    bundle = models.ForeignKey(Bundle, null=False, on_delete=models.CASCADE, related_name='fields')

    _verbose_name = models.CharField(max_length=255)
    _help_text = models.TextField(max_length=650, blank=True)
    _blank = models.BooleanField(default=True)

    def get_django_field(self):
        django_field = getattr(models, self.field_type, "CharField")
        attributes = self.get_django_field_attributes()
        if hasattr(self, 'content_type'):
            related_model = getattr(self, 'content_type').model_class()
            return django_field(related_model, **attributes)
        return django_field(**attributes)

    def get_django_field_attributes(self):
        print("NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print(models.DO_NOTHING)
        attributes = dict()
        for field in self._meta.get_fields():
            if str(field.name).startswith('_'):
                attributes[field.name[1:]] = getattr(self, field.name)
        return attributes


class CharField(Field):
    field_type = models.CharField(max_length=255, default="CharField", editable=False)
    _max_length = models.IntegerField(default=255)
    # default = models.CharField(max_length=255, blank=True)


class TextField(Field):
    field_type = models.CharField(max_length=255, default="TextField", editable=False)
    _max_length = models.IntegerField(default=65535)
    # default = models.TextField(max_length=65535, blank=True)


class DateTimeField(Field):
    field_type = models.CharField(max_length=255, default="DateTimeField", editable=False)
    # default = models.DateTimeField(null=True, blank=True)


class URLField(Field):
    field_type = models.CharField(max_length=255, default="URLField", editable=False)
    # default = models.URLField(max_length=255, blank=True)


class ForeignKeyField(Field):
    field_type = models.CharField(max_length=255, default="ForeignKey", editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    _related_name = models.CharField(max_length=255, default="+", editable=False)
    _null = models.BooleanField(default=True)
    _on_delete = models.CharField(max_length=255, default="DO_NOTHING", editable=True)


class ManyToManyField(Field):
    field_type = models.CharField(max_length=255, default="ManyToManyField", editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    _related_name = models.CharField(max_length=255, default="+", editable=False)
