import logging

from bitfield import BitHandler
from django.forms import model_to_dict

from isc_common import setAttr, getAttr, delAttr
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefManager, BaseRefQuerySet
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.ckk.models.material_type import Material_type
from one_c.models.document_1c import Document_1c

logger = logging.getLogger(__name__)


class MaterialsQuerySet(BaseRefQuerySet, CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class MaterialsManager(BaseRefManager, CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        from kaf_pas.k_one_c.models.nomenklatura import Nomenklatura_model

        nomenklatura = None
        if record.nomenklatura_model:
            nomenklatura = Nomenklatura_model.objects.get(pk=record.nomenklatura_model.ref)

        res = {
            'id': record.id,
            'code': record.code,
            'gost': record.gost,
            'name': record.name,
            'full_name': record.full_name,
            'description': record.description,
            'location_id': record.location.id,
            'location__name': record.location.name,
            'location__full_name': record.location.full_name,
            'materials_type_id': record.materials_type.id,
            'materials_type__code': record.materials_type.code,
            'materials_type__name': record.materials_type.name,
            'materials_type__description': record.materials_type.description,
            'materials_type__full_name': record.materials_type.full_name,
            'parent_id': record.parent.id if record.parent else None,
            'nomenklatura_model_ref': nomenklatura.ref if nomenklatura else None,
            'nomenklatura_model__code': nomenklatura.code if nomenklatura else None,
            'nomenklatura_model__full_name': nomenklatura.full_name if nomenklatura else None,
        }
        return res

    def get_queryset(self):
        return MaterialsQuerySet(self.model, using=self._db)

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        material_type = Material_type.objects.get(id=data.get('materials_type_id'))
        setAttr(_data, 'materials_type_id', material_type.id)

        if data.get('nomenklatura_model__full_name'):
            from kaf_pas.k_one_c.models.nomenklatura import Nomenklatura_model
            nomenklatura_model = Nomenklatura_model.objects.get(full_name=data.get('nomenklatura_model__full_name'))
            setAttr(_data, 'nomenklatura_model', Document_1c.objects.get(pk=nomenklatura_model.ref))

        delAttr(_data, 'ed_izm__code')
        delAttr(_data, 'location__full_name')
        delAttr(_data, 'materials_type__full_name')
        delAttr(_data, 'nomenklatura_model_id')
        delAttr(_data, 'nomenklatura_model_ref')
        delAttr(_data, 'nomenklatura_model__code')
        delAttr(_data, 'nomenklatura_model__full_name')

        res = super().create(**_data)
        res = model_to_dict(res)
        props = getAttr(res, 'props')
        if props and isinstance(props, BitHandler):
            props = getAttr(res, 'props')._value
            setAttr(res, 'props', props)
        data.update(res)
        return data

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        material_type = Material_type.objects.get(full_name=data.get('materials_type__full_name'))
        setAttr(_data, 'materials_type_id', material_type.id)

        if data.get('nomenklatura_model__full_name'):
            from kaf_pas.k_one_c.models.nomenklatura import Nomenklatura_model
            nomenklatura_model = Nomenklatura_model.objects.get(full_name=data.get('nomenklatura_model__full_name'))
            setAttr(_data, 'nomenklatura_model', Document_1c.objects.get(pk=nomenklatura_model.ref))

        delAttr(_data, 'ed_izm__code')
        delAttr(_data, 'location__full_name')
        delAttr(_data, 'materials_type__name')
        delAttr(_data, 'materials_type__code')
        delAttr(_data, 'materials_type__description')
        delAttr(_data, 'materials_type__full_name')
        delAttr(_data, 'nomenklatura_model_id')
        delAttr(_data, 'nomenklatura_model_ref')
        delAttr(_data, 'nomenklatura_model__code')
        delAttr(_data, 'nomenklatura_model__full_name')
        delAttr(_data, 'location')
        delAttr(_data, 'location__name')
        delAttr(_data, 'materials_type')
        delAttr(_data, 'full_name')
        delAttr(_data, 'isFolder')
        delAttr(_data, 'parent')
        delAttr(_data, 'id')

        res, created = super().update_or_create(id=data.get('id'), defaults=_data)
        res = model_to_dict(res)
        props = getAttr(res, 'props')
        if props and isinstance(props, BitHandler):
            props = getAttr(res, 'props')._value
            setAttr(res, 'props', props)
        data.update(res)
        return data


class Materials(BaseRefHierarcy):
    gost = CodeField()
    location = ForeignKeyProtect(Locations)
    materials_type = ForeignKeyProtect(Material_type)
    nomenklatura_model = ForeignKeyProtect(Document_1c, null=True, blank=True)
    objects = MaterialsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Материалы'
