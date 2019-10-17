from django.db import transaction

from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.item import Item
from kaf_pas.production.models.operation_material import Operation_material
from kaf_pas.production.models.operation_resources import Operation_resources
from kaf_pas.production.models.operations_item import Operations_item, Operations_itemManager


@JsonResponseWithException()
def Operations_item_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Operations_item.objects.
                filter().
                # select_related('item', 'operation').
                get_range_rows1(
                request=request,
                function=Operations_itemManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_item_Add(request):
    return JsonResponse(DSResponseAdd(data=Operations_item.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_item_Update(request):
    return JsonResponse(DSResponseUpdate(data=Operations_item.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_item_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Operations_item.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_item_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Operations_item.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_item_Info(request):
    return JsonResponse(DSResponse(request=request, data=Operations_item.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_item_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Operations_item.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Operations_item_CopyOpers(request):
    _request = DSRequest(request=request)
    source = _request.json.get('source')
    destination = _request.json.get('destination')
    res = False

    if source and destination:
        srecords = source.get('records')
        drecord = destination.get('record')
        item = Item.objects.get(id=drecord.get('id'))

        if isinstance(srecords, list) and isinstance(drecord, dict):
            with transaction.atomic():
                for srecord in srecords:
                    old_operations_item = Operations_item.objects.get(id=srecord.get('id'))
                    operations_item, created = Operations_item.objects.get_or_create(
                        item=item,
                        operation=old_operations_item.operation,
                        defaults=dict(
                            ed_izm=old_operations_item.ed_izm,
                            qty=old_operations_item.qty,
                            num=old_operations_item.num
                        ))

                    if created:
                        for operation_resources in Operation_resources.objects.filter(operationitem=old_operations_item):
                            Operation_resources.objects.get_or_create(
                                operationitem=operations_item,
                                resource=operation_resources.resource,
                                location=operation_resources.location
                            )

                        for operation_material in Operation_material.objects.filter(operationitem=old_operations_item):
                            Operation_material.objects.get_or_create(
                                operationitem=operations_item,
                                material=operation_material.material,
                                material_askon=operation_material.material_askon,
                                ed_izm=operation_material.ed_izm,
                                qty=operation_material.qty,
                            )

        return JsonResponse(DSResponse(request=request, status=RPCResponseConstant.statusSuccess).response)
    else:
        raise Exception(f'Копирование не выполнено.')
