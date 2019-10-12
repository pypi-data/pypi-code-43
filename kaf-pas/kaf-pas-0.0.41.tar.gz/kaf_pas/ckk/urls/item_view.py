from django.urls import path

from kaf_pas.ckk.views import item_view

urlpatterns = [

    path('ItemView/Fetch/', item_view.Item_view_Fetch),
    path('ItemView/Add', item_view.Item_view_Add),
    path('ItemView/Update', item_view.Item_view_Update),
    path('ItemView/Remove', item_view.Item_view_Remove),
    path('ItemView/Lookup/', item_view.Item_view_Lookup),
    path('ItemView/Info/', item_view.Item_view_Info),
    path('ItemView/Copy', item_view.Item_view_Copy),
    path('CopyItems', item_view.copyItems),

]
