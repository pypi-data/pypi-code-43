from django.urls import path
from isc_common.views import params

urlpatterns = [

    path('Params/Fetch/', params.Params_Fetch),
    path('Params/Add', params.Params_Add),
    path('Params/Update', params.Params_Update),
    path('Params/Update1', params.Params_Update1),
    path('Params/Remove', params.Params_Remove),
    path('Params/Remove1', params.Params_Remove1),
    path('Params/Lookup', params.Params_Lookup),
    path('Params/Info/', params.Params_Info),
    path('Params/Get/', params.Params_Get),

]
