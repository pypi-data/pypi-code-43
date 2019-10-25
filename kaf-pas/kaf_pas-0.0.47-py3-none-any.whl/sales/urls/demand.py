from django.urls import path

from kaf_pas.sales.views import demand

urlpatterns = [

    path('Demand/Fetch/', demand.Demand_Fetch),
    path('Demand/Add', demand.Demand_Add),
    path('Demand/Update', demand.Demand_Update),
    path('Demand/Remove', demand.Demand_Remove),
    path('Demand/Lookup/', demand.Demand_Lookup),
    path('Demand/Info/', demand.Demand_Info),
    path('Demand/Copy', demand.Demand_Copy),

]
