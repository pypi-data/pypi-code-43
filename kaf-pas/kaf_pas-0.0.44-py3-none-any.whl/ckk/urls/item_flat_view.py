from django.urls import path

from kaf_pas.ckk.views import item_flat_view

urlpatterns = [

    path('Item_flat_view/Fetch/', item_flat_view.Item_flat_view_Fetch),
    path('Item_flat_view/Add', item_flat_view.Item_flat_view_Add),
    path('Item_flat_view/Update', item_flat_view.Item_flat_view_Update),
    path('Item_flat_view/Remove', item_flat_view.Item_flat_view_Remove),
    path('Item_flat_view/Lookup/', item_flat_view.Item_flat_view_Lookup),
    path('Item_flat_view/Info/', item_flat_view.Item_flat_view_Info),
    path('Item_flat_view/Copy', item_flat_view.Item_flat_view_Copy),

]
