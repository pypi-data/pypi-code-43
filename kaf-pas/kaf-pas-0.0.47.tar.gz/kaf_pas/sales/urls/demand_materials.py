from django.urls import path

from kaf_pas.sales.views import demand_materials

urlpatterns = [

    path('Demand_materials/Fetch/', demand_materials.Demand_materials_Fetch),
    path('Demand_materials/Add', demand_materials.Demand_materials_Add),
    path('Demand_materials/Update', demand_materials.Demand_materials_Update),
    path('Demand_materials/Remove', demand_materials.Demand_materials_Remove),
    path('Demand_materials/Lookup/', demand_materials.Demand_materials_Lookup),
    path('Demand_materials/Info/', demand_materials.Demand_materials_Info),
    path('Demand_materials/Copy', demand_materials.Demand_materials_Copy),

]
