from clndr.models.calendars import get_graph
from isc_common.http.DSResponse import DSResponse, JsonWSPostResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonWSPostResponseWithException()
def CalendarGraph_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=get_graph(request=request),
            status=RPCResponseConstant.statusSuccess).response)
