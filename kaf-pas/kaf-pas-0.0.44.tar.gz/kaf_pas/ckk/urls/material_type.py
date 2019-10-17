from django.urls import path

from kaf_pas.ckk.views import material_type

urlpatterns = [

    path('Material_type/Fetch/', material_type.Material_type_Fetch),
    path('Material_type/Add', material_type.Material_type_Add),
    path('Material_type/Update', material_type.Material_type_Update),
    path('Material_type/Remove', material_type.Material_type_Remove),
    path('Material_type/Lookup/', material_type.Material_type_Lookup),
    path('Material_type/Info/', material_type.Material_type_Info),
    path('Material_type/Copy', material_type.Material_type_Copy),
    path('Material_type/CopyParams', material_type.Material_type_CopyParams),

]
