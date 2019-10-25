from django.urls import path

from kaf_pas.sales.views import precent_item_types

urlpatterns = [

    path('Precent_item_types/Fetch/', precent_item_types.Precent_item_types_Fetch),
    path('Precent_item_types/Add', precent_item_types.Precent_item_types_Add),
    path('Precent_item_types/Update', precent_item_types.Precent_item_types_Update),
    path('Precent_item_types/Remove', precent_item_types.Precent_item_types_Remove),
    path('Precent_item_types/Lookup/', precent_item_types.Precent_item_types_Lookup),
    path('Precent_item_types/Info/', precent_item_types.Precent_item_types_Info),
    path('Precent_item_types/Copy', precent_item_types.Precent_item_types_Copy),

]
