from django.urls import path

from kaf_pas.sales.views import dogovor_types

urlpatterns = [

    path('Dogovor_types/Fetch/', dogovor_types.Dogovor_types_Fetch),
    path('Dogovor_types/Add', dogovor_types.Dogovor_types_Add),
    path('Dogovor_types/Update', dogovor_types.Dogovor_types_Update),
    path('Dogovor_types/Remove', dogovor_types.Dogovor_types_Remove),
    path('Dogovor_types/Lookup/', dogovor_types.Dogovor_types_Lookup),
    path('Dogovor_types/Info/', dogovor_types.Dogovor_types_Info),
    path('Dogovor_types/Copy', dogovor_types.Dogovor_types_Copy),

]
