from django.urls import path

from kaf_pas.sales.views import status_demand

urlpatterns = [

    path('Status_demand/Fetch/', status_demand.Status_demand_Fetch),
    path('Status_demand/Add', status_demand.Status_demand_Add),
    path('Status_demand/Update', status_demand.Status_demand_Update),
    path('Status_demand/Remove', status_demand.Status_demand_Remove),
    path('Status_demand/Lookup/', status_demand.Status_demand_Lookup),
    path('Status_demand/Info/', status_demand.Status_demand_Info),
    path('Status_demand/Copy', status_demand.Status_demand_Copy),

]
