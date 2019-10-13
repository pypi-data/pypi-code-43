import logging

from django.db.models import Model
from transliterate import translit

from isc_common import setAttr
from isc_common.fields.code_field import CodeField
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class BaseRefQuerySet(AuditQuerySet):

    def get_full_name_id(self, parent_id, name):
        end = False
        if name.find('/') != -1:
            _name = name[:name.find('/')]
        else:
            end = True
            _name = name

        if parent_id:
            res = super().get(parent_id=parent_id, name=_name)
        else:
            res = super().get(parent__isnull=True, name=_name)

        if end:
            return res
        else:
            return self.get_full_name_id(res.id, name[name.find('/') + 1:])

    def get(self, *args, **kwargs):
        key = [key for key in kwargs.keys() if key == 'full_name']
        if len(key) == 0:
            res = super().get(*args, **kwargs)
        else:
            full_name = kwargs.get('full_name')
            if full_name == None:
               full_name = ''
            res = self.get_full_name_id(None, full_name[1:])


        return res

    def update(self, **kwargs):
        if kwargs.get('code') == None:
            setAttr(kwargs, 'code', AuditModel.uncapitalize(translit(kwargs.get('name'), reversed=True).replace("'", '').replace(' ', '_')))
        res = super().update(**kwargs)
        return res

    def create(self, **kwargs):
        if kwargs.get('code') == None:
            setAttr(kwargs, 'code', AuditModel.uncapitalize(translit(kwargs.get('name'), reversed=True).replace("'", '').replace(' ', '_')))
        res = super().create(**kwargs)
        return res


class BaseRefManager(AuditManager):
    def get_queryset(self):
        if self.alive_only:
            return BaseRefQuerySet(model=self.model, alive_only=self.alive_only, enabledAll=self.enabledAll).filter(deleted_at=None)
        return BaseRefQuerySet(model=self.model, alive_only=self.alive_only, enabledAll=self.enabledAll)


class BaseRef(AuditModel):
    code = CodeField()
    name = NameField()
    description = DescriptionField()

    def save(self, *args, **kwargs):
        if self.code == None:
            self.code = AuditModel.uncapitalize(translit(self.name, reversed=True).replace("'", '').replace(' ', '_').replace('-', '_'))
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseHierarcy(Model):
    code = None
    name = None

    parent = ForeignKeyProtect("self", null=True, blank=True)

    def get_parent_name(self, parent, name):
        if not self.name:
            raise Exception('Name not Exists')

        if not parent:
            return name

        item = parent
        name = f'/{item.name}{name}'
        if item.parent:
            return self.get_parent_name(item.parent, name)
        return name

    @property
    def full_name(self):
        if not self.name:
            if self.code:
               self.name = self.code
            else:
                raise Exception('Name and Code not Exists')


        name = f'/{self.name}'
        return self.get_parent_name(self.parent, name)

    @property
    def full_name_id(self):
        if not self.name:
            return None

        return self.objects.get(full_name=self.full_name)

    objects = BaseRefManager()
    all_objects = BaseRefManager(alive_only=False)

    class Meta:
        abstract = True


class Hierarcy(AuditModel, BaseHierarcy):
    class Meta:
        abstract = True


class BaseRefHierarcy(Hierarcy):
    code = CodeField()
    name = NameField()
    description = DescriptionField()

    def save(self, *args, **kwargs):
        if self.code == None:
            self.code = AuditModel.uncapitalize(translit(self.name, reversed=True).replace("'", '').replace(' ', '_'))
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
