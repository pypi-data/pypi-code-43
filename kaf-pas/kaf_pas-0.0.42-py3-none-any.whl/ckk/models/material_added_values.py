import logging

from django.db import connection, transaction, ProgrammingError

from isc_common import setAttr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.ckk.models.material_params import Material_params
from kaf_pas.ckk.models.materials import Materials
from refs.models.type_param import Type_param
from refs.models.type_param_values import Type_param_values

logger = logging.getLogger(__name__)


class Material_added_valuesQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Material_added_valuesManager(AuditManager):

    def get_range_rows1(self, request, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        fields = []
        material = Materials.objects.get(id=data.get('id'))
        view_name = f'ckk_{material.materials_type.code}_view'

        for material_params in Material_params.objects.filter(materials_type_id=data.get('materials_type_id')).order_by('order', ):
            fields.append(material_params.param_type.code)

        sql_str = f'''select {",".join(fields)} from {view_name} where id = {data.get("id")}'''
        result = []
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_str)

                i = 0
                _row = dict()
                for row in cursor.fetchall():
                    for field in fields:
                        setAttr(_row, field, row[i])
                        i += 1
                result.append(_row)
        except ProgrammingError:
            ...

        return result

    def get_queryset(self):
        return Material_added_valuesQuerySet(self.model, using=self._db)

    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()

        material_id = data.get('id')
        materials_type_id = data.get('materials_type_id')

        with transaction.atomic():
            for material_params in Material_params.objects.filter(materials_type_id=materials_type_id).order_by('order', ):
                value = data.get(material_params.param_type.code)

                try:
                    material_added_value = self.get(material_id=material_id, param_values__type__code=material_params.param_type.code)
                    if material_params.param_type.type == Type_param.integer():
                        material_added_value.param_values.value_int = value
                        material_added_value.param_values.save()
                    elif material_params.param_type.type == Type_param.float():
                        material_added_value.param_values.value_float = value
                        material_added_value.param_values.save()
                    elif material_params.param_type.type == Type_param.date():
                        material_added_value.param_values.value_date = value
                        material_added_value.param_values.save()
                    elif material_params.param_type.type == Type_param.date_time():
                        material_added_value.param_values.value_date = value
                        material_added_value.param_values.save()
                    elif material_params.param_type.type == Type_param.string():
                        material_added_value.param_values.value_str = value
                        material_added_value.param_values.save()
                    elif material_params.param_type.type == Type_param.select():
                        material_added_value.param_values.value_str = value
                        material_added_value.param_values.save()
                    else:
                        raise Exception(f'{material_params.param_type.type}: unknown type.')

                except Material_added_values.DoesNotExist:
                    if material_params.param_type.type == Type_param.integer():
                        self.create(material_id=material_id, param_values=Type_param_values.objects.create(type=material_params.param_type, value_int=value))
                    elif material_params.param_type.type == Type_param.float():
                        self.create(material_id=material_id, param_values=Type_param_values.objects.create(type=material_params.param_type, value_float=value))
                    elif material_params.param_type.type == Type_param.date():
                        self.create(material_id=material_id, param_values=Type_param_values.objects.create(type=material_params.param_type, value_date=value))
                    elif material_params.param_type.type == Type_param.date_time():
                        self.create(material_id=material_id, param_values=Type_param_values.objects.create(type=material_params.param_type, value_date=value))
                    elif material_params.param_type.type == Type_param.string():
                        self.create(material_id=material_id, param_values=Type_param_values.objects.create(type=material_params.param_type, value_str=value))
                    elif material_params.param_type.type == Type_param.select():
                        self.create(material_id=material_id, param_values=Type_param_values.objects.create(type=material_params.param_type, value_str=value))
                    else:
                        raise Exception(f'{material_params.param_type.type}: unknown type.')
        return data


class Material_added_values(AuditModel):
    material = ForeignKeyProtect(Materials)
    param_values = ForeignKeyProtect(Type_param_values)

    objects = Material_added_valuesManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Значения дополнительных (настраиваимых) параметров'
