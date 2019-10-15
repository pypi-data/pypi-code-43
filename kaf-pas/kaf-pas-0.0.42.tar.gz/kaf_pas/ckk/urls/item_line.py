from django.urls import path

from kaf_pas.ckk.views import item_line

urlpatterns = [

    path('Item_line/Fetch/', item_line.Item_line_Fetch),
    path('Item_line/Add', item_line.Item_line_Add),
    path('Item_line/Update', item_line.Item_line_Update),
    path('Item_line/Remove', item_line.Item_line_Remove),
    path('Item_line/Lookup/', item_line.Item_line_Lookup),
    path('Item_line/Info/', item_line.Item_line_Info),
    # path('Item_line/Copy', item_line.Item_line_Copy),

]
