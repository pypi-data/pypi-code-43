from django.urls import path

from kaf_pas.ckk.views import item, material_type

urlpatterns = [

    path('Item/Fetch/', item.Item_Fetch),
    path('Item/Add', item.Item_Add),
    path('Item/Update', item.Item_Update),
    path('Item/Remove', item.Item_Remove),
    path('Item/Lookup/', item.Item_Lookup),
    path('Item/Info/', item.Item_Info),
]
