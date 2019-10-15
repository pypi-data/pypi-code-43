from django.urls import path

from kaf_pas.ckk.views import material_type
from kaf_pas.production.views import operations_item

urlpatterns = [

    path('Operations_item/Fetch/', operations_item.Operations_item_Fetch),
    path('Operations_item/Add', operations_item.Operations_item_Add),
    path('Operations_item/Update', operations_item.Operations_item_Update),
    path('Operations_item/Remove', operations_item.Operations_item_Remove),
    path('Operations_item/Lookup/', operations_item.Operations_item_Lookup),
    path('Operations_item/Info/', operations_item.Operations_item_Info),
    path('Operations_item/Copy', operations_item.Operations_item_Copy),
    path('Operations_item/CopyOpers', operations_item.Operations_item_CopyOpers),

]
