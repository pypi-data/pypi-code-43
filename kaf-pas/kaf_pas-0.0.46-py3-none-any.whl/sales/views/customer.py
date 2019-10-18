from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from kaf_pas.sales.models.customer import Customer, CustomerManager


@JsonResponseWithException()
def Customer_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Customer.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=CustomerManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Customer_Add(request):
    return JsonResponse(DSResponseAdd(data=Customer.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Customer_Update(request):
    return JsonResponse(DSResponseUpdate(data=Customer.objects.updateFromRequest(request,removed=['isFolder']), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Customer_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Customer.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Customer_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Customer.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Customer_Info(request):
    return JsonResponse(DSResponse(request=request, data=Customer.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
