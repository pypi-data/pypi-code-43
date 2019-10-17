from django.urls import path

from kaf_pas.production.views import operation_material

urlpatterns = [

    path('Operation_material/Fetch/', operation_material.Operation_material_Fetch),
    path('Operation_material/Add', operation_material.Operation_material_Add),
    path('Operation_material/Update', operation_material.Operation_material_Update),
    path('Operation_material/Remove', operation_material.Operation_material_Remove),
    path('Operation_material/Lookup/', operation_material.Operation_material_Lookup),
    path('Operation_material/Info/', operation_material.Operation_material_Info),

]
