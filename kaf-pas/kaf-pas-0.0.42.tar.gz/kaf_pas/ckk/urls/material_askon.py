from django.urls import path

from kaf_pas.ckk.views import material_askon

urlpatterns = [

    path('MaterialAskon/Fetch/', material_askon.Material_askon_Fetch),
    path('MaterialAskon/Add', material_askon.Material_askon_Add),
    path('MaterialAskon/Update', material_askon.Material_askon_Update),
    path('MaterialAskon/Remove', material_askon.Material_askon_Remove),
    path('MaterialAskon/Lookup/', material_askon.Material_askon_Lookup),
    path('MaterialAskon/Info/', material_askon.Material_askon_Info),
    path('MaterialAskon/Copy', material_askon.Material_askon_Copy),

]
