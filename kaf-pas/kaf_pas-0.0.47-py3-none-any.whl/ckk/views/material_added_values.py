
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.material_added_values import Material_added_values, Material_added_valuesManager


@JsonResponseWithException()
def Material_added_values_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Material_added_values.objects.
                get_range_rows1(
                request=request,
                # function=Material_added_valuesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_added_values_Add(request):
    return JsonResponse(DSResponseAdd(data=Material_added_values.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_added_values_Update(request):
    return JsonResponse(DSResponseUpdate(data=Material_added_values.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_added_values_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Material_added_values.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_added_values_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Material_added_values.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_added_values_Info(request):
    return JsonResponse(DSResponse(request=request, data=Material_added_values.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_added_values_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Material_added_values.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
