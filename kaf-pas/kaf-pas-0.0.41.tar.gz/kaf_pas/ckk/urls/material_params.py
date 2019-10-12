from django.urls import path

from kaf_pas.ckk.views import material_params

urlpatterns = [

    path('Material_params/Fetch/', material_params.Material_params_Fetch),
    path('Material_params/Add', material_params.Material_params_Add),
    path('Material_params/Update', material_params.Material_params_Update),
    path('Material_params/Remove', material_params.Material_params_Remove),
    path('Material_params/Lookup/', material_params.Material_params_Lookup),
    path('Material_params/Info/', material_params.Material_params_Info),
    path('Material_params/Copy', material_params.Material_params_Copy),

]
