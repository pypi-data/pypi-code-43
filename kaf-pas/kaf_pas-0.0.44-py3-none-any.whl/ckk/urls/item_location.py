from django.urls import path

from kaf_pas.ckk.views import item_location

urlpatterns = [

    path('Item_location/Fetch/', item_location.Item_location_Fetch),
    path('Item_location/Add', item_location.Item_location_Add),
    path('Item_location/Update', item_location.Item_location_Update),
    path('Item_location/Remove', item_location.Item_location_Remove),
    path('Item_location/Lookup/', item_location.Item_location_Lookup),
    path('Item_location/Info/', item_location.Item_location_Info),

]
