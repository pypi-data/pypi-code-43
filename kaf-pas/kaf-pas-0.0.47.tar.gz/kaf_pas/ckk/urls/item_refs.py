from django.urls import path

from kaf_pas.ckk.views import item_refs

urlpatterns = [

    path('Item_refs/Fetch/', item_refs.Item_refs_Fetch),
    path('Item_refs/Add', item_refs.Item_refs_Add),
    path('Item_refs/Update', item_refs.Item_refs_Update),
    path('Item_refs/Remove', item_refs.Item_refs_Remove),
    path('Item_refs/Lookup/', item_refs.Item_refs_Lookup),
    path('Item_refs/Info/', item_refs.Item_refs_Info),

]
