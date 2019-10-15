import logging

from django.db import connection, transaction
from django.db.models import PositiveIntegerField
from django.forms import model_to_dict

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.material_type import Material_type
from refs.models.type_param import Type_param

logger = logging.getLogger(__name__)


class Material_paramsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def remove_view(self, **kwargs):
        material_type = Material_type.objects.get(id=kwargs.get('materials_type'))
        sql = []
        sql.append(f'DROP VIEW IF EXISTS  public.ckk_{material_type.code}_view;')

        with connection.cursor() as cursor:
            sql_str = '\n'.join(sql)
            cursor.execute(sql_str)

    def recreate_view(self, **kwargs):
        try:
            material_type = Material_type.objects.get(id=kwargs.get('materials_type'))
        except Material_type.DoesNotExist:
            material_type = Material_params.objects.get(id=kwargs.get('id')).materials_type

        sql = []
        sql.append(f'DROP VIEW IF EXISTS  public.ckk_{material_type.code}_view;')

        sql.append(f'CREATE OR REPLACE VIEW ckk_{material_type.code}_view AS ')
        sql.append('select cm.id,')

        step = 0
        for param_type in Material_params.objects.filter(materials_type=material_type).order_by('order', ):
            if step > 0:
                sql.append(",");
            step += 1
            if param_type.param_type.type == 'Строковый':
                sql.append(f"(select value_str from refs_type_param_values rv ")
            elif param_type.param_type.type == 'Целое число':
                sql.append(f"(select value_int from refs_type_param_values rv ")
            elif param_type.param_type.type == 'Дробное число':
                sql.append(f"(select value_float from refs_type_param_values rv ")
            elif param_type.param_type.type == 'Дата без времени':
                sql.append(f"(select value_date from refs_type_param_values rv ")
            elif param_type.param_type.type == 'Дата со временем':
                sql.append(f"(select value_date from refs_type_param_values rv ")
            elif param_type.param_type.type == 'Выбор из списка':
                sql.append(f"(select value_str from refs_type_param_values rv ")
            else:
                raise Exception(f'Unknown type: {param_type.param_type.type}')

            sql.append(f"join refs_type_param rtp on rtp.id = rv.type_id "
                       f"join ckk_material_added_values ca on ca.material_id = cm.id "
                       f"where rv.id = ca.param_values_id and rtp.code = '{param_type.param_type.code}')  {param_type.param_type.code}")

        sql.append("from ckk_materials cm join ckk_material_type mt on mt.id = cm.materials_type_id")
        sql.append(f"where mt.code = '{material_type.code}'")

        with connection.cursor() as cursor:
            sql_str = '\n'.join(sql)
            cursor.execute(sql_str)

    def delete(self):
        with transaction.atomic():
            for_delete = model_to_dict(super().all()[0])
            res = super().delete()
            if Material_params.objects.filter(materials_type_id=for_delete.get('materials_type')).count() > 0:
                self.recreate_view(**for_delete)
            else:
                self.remove_view(**for_delete)
            return res

    def create(self, **kwargs):
        with transaction.atomic():
            res = super().create(**kwargs)
            self.recreate_view(**model_to_dict(res))
            return res

    def update(self, **kwargs):
        with transaction.atomic():
            res = super().update(**kwargs)
            self.recreate_view(**kwargs)
            return res


class Material_paramsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'materials_type_id': record.materials_type.id,
            'materials_type__code': record.materials_type.code,
            'materials_type__name': record.materials_type.name,
            'materials_type__description': record.materials_type.description,
            'param_type_id': record.param_type.id,
            'param_type__code': record.param_type.code,
            'param_type__name': record.param_type.name,
            'param_type__type': record.param_type.type,
            'param_type__description': record.param_type.description,
            'param_type__length': record.param_type.length,
            'param_type__required': record.param_type.required,
            'order': record.order,
        }
        return res

    def get_queryset(self):
        return Material_paramsQuerySet(self.model, using=self._db)


class Material_params(AuditModel):
    materials_type = ForeignKeyProtect(Material_type)
    param_type = ForeignKeyProtect(Type_param)
    order = PositiveIntegerField(default=0)

    objects = Material_paramsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Дополнительные параметры'
        unique_together = (('materials_type', 'param_type'),)
