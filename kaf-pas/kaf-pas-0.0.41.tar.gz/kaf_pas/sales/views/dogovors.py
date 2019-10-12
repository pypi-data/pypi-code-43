from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException, JsonWSResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.dogovor_download_file import download_dogovor_file
from kaf_pas.sales.models.dogovor_upload_file import DSResponse__Dogovor_UploadFile
from kaf_pas.sales.models.dogovors import Dogovors, DogovorsManager
from kaf_pas.sales.models.precent_download_file import download_present_file
from kaf_pas.sales.models.precent_upload_file import DSResponse__Precent_UploadFile


@JsonResponseWithException()
def Dogovors_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Dogovors.objects.
                select_related('status').
                get_range_rows1(
                request=request,
                function=DogovorsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovors_Add(request):
    return JsonResponse(DSResponseAdd(data=Dogovors.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovors_Update(request):
    return JsonResponse(DSResponseUpdate(data=Dogovors.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovors_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Dogovors.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovors_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Dogovors.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovors_Info(request):
    return JsonResponse(DSResponse(request=request, data=Dogovors.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Dogovors_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Dogovors.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)

@JsonWSResponseWithException()
def Dogovor_UploadFile(request):
    return JsonResponse(DSResponse__Dogovor_UploadFile(request).response)


@JsonWSResponseWithException(printing=False)
def Dogovort_DownloadFile(request):
    return download_dogovor_file(request)
