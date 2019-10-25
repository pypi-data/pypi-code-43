from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.ckk.models.material_params import Material_paramsManager, Material_params


@JsonResponseWithException()
def Material_params_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Material_params.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Material_paramsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_params_Add(request):
    return JsonResponse(DSResponseAdd(data=Material_params.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_params_Update(request):
    return JsonResponse(DSResponseUpdate(data=Material_params.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_params_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Material_params.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_params_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Material_params.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_params_Info(request):
    return JsonResponse(DSResponse(request=request, data=Material_params.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Material_params_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Material_params.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
