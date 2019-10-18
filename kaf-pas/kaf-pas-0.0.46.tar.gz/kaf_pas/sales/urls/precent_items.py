from django.urls import path

from kaf_pas.sales.views import precent_items

urlpatterns = [

    path('Precent_items/Fetch/', precent_items.Precent_items_Fetch),
    path('Precent_items/Add', precent_items.Precent_items_Add),
    path('Precent_items/Update', precent_items.Precent_items_Update),
    path('Precent_items/Remove', precent_items.Precent_items_Remove),
    path('Precent_items/Lookup/', precent_items.Precent_items_Lookup),
    path('Precent_items/Info/', precent_items.Precent_items_Info),

]
