from django.urls import path

from kaf_pas.ckk.views import material_added_values

urlpatterns = [

    path('Material_added_values/Fetch/', material_added_values.Material_added_values_Fetch),
    path('Material_added_values/Add', material_added_values.Material_added_values_Add),
    path('Material_added_values/Update', material_added_values.Material_added_values_Update),
    path('Material_added_values/Remove', material_added_values.Material_added_values_Remove),
    path('Material_added_values/Lookup/', material_added_values.Material_added_values_Lookup),
    path('Material_added_values/Info/', material_added_values.Material_added_values_Info),
    path('Material_added_values/Copy', material_added_values.Material_added_values_Copy),

]
