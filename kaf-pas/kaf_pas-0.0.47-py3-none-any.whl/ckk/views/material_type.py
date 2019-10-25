from django.db.models import Max

from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.material_type import Material_type, Material_typeManager
from kaf_pas.ckk.models.material_type_view import Material_type_view, Material_type_viewManager


@JsonResponseWithException()
def Material_type_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Material_type_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Material_type_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_type_Add(request):
    return JsonResponse(DSResponseAdd(data=Material_type.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_type_Update(request):
    return JsonResponse(DSResponseUpdate(data=Material_type.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_type_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Material_type.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_type_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Material_type.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_type_Info(request):
    return JsonResponse(DSResponse(request=request, data=Material_type.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_type_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Material_type.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_type_CopyParams(request):
    _request = DSRequest(request=request)
    source = _request.json.get('source')
    destination = _request.json.get('destination')
    res = False

    if isinstance(source, dict) and isinstance(destination, dict):
        srecord = source.get('record')
        drecord = destination.get('record')

        if srecord and drecord:
            from kaf_pas.ckk.models.material_params import Material_params
            order = Material_params.objects.filter(materials_type=drecord.get(id))
            max_order = order.aggregate(Max('order'))
            max_order = max_order.get('max_order', 0)
            for params in Material_params.objects.filter(materials_type_id=srecord.get('id')):
                max_order += 1
                Material_params.objects.get_or_create(materials_type_id=drecord.get('id'), param_type=params.param_type, order=max_order)
                res = True

    if res:
        return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)
    else:
        raise Exception(f'Копирование не выполнено.')
