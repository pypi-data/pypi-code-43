from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.kd.models.document_attributes import Document_attributes, Document_attributesManager


@JsonResponseWithException()
def Document_attributes_SPC_CLM_NOTE_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Document_attributes.objects.
                select_related('attr_type').
                filter(attr_type__code='SPC_CLM_NOTE').
                get_range_rows1(
                request=request,
                function=Document_attributesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attributes_SPC_CLM_NOTE_Add(request):
    return JsonResponse(DSResponseAdd(data=Document_attributes.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attributes_SPC_CLM_NOTE_Update(request):
    return JsonResponse(DSResponseUpdate(data=Document_attributes.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attributes_SPC_CLM_NOTE_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Document_attributes.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attributes_SPC_CLM_NOTE_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Document_attributes.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attributes_SPC_CLM_NOTE_Info(request):
    return JsonResponse(DSResponse(request=request, data=Document_attributes.objects.
                                   select_related('attr_type').
                                   filter(attr_type__code='SPC_CLM_NOTE').
                                   get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_attributes_SPC_CLM_NOTE_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Document_attributes.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)            
