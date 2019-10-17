from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException, JsonWSResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.precent import Precent, PrecentManager
from kaf_pas.sales.models.precent_download_file import download_present_file
from kaf_pas.sales.models.precent_upload_file import DSResponse__Precent_UploadFile
from django.conf import settings


@JsonResponseWithException()
def Precent_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Precent.objects.
                select_related('status').
                get_range_rows1(
                request=request,
                function=PrecentManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_Add(request):
    return JsonResponse(DSResponseAdd(data=Precent.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_Update(request):
    return JsonResponse(DSResponseUpdate(data=Precent.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Precent.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Precent.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Precent_Info(request):
    return JsonResponse(DSResponse(request=request, data=Precent.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonWSResponseWithException()
def Precent_UploadFile(request):
    return JsonResponse(DSResponse__Precent_UploadFile(request).response)


@JsonWSResponseWithException(printing=False)
def Precent_DownloadFile(request):
    return download_present_file(request)
