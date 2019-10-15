from django.urls import path

from kaf_pas.ckk.views import item_image_refs

urlpatterns = [

    path('Item_image_refs/Fetch/', item_image_refs.Item_image_refs_Fetch),
    path('Item_image_refs/Add', item_image_refs.Item_image_refs_Add),
    path('Item_image_refs/Update', item_image_refs.Item_image_refs_Update),
    path('Item_image_refs/Remove', item_image_refs.Item_image_refs_Remove),
    path('Item_image_refs/Lookup/', item_image_refs.Item_image_refs_Lookup),
    path('Item_image_refs/Info/', item_image_refs.Item_image_refs_Info),
    path('Item_image_refs/Copy', item_image_refs.Item_image_refs_Copy),
]
