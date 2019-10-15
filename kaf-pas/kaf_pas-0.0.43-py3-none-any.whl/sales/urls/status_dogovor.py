from django.urls import path

from kaf_pas.sales.views import status_dogovor

urlpatterns = [

    path('StatusDogovor/Fetch/', status_dogovor.StatusDogovor_Fetch),
    path('StatusDogovor/Add', status_dogovor.StatusDogovor_Add),
    path('StatusDogovor/Update', status_dogovor.StatusDogovor_Update),
    path('StatusDogovor/Remove', status_dogovor.StatusDogovor_Remove),
    path('StatusDogovor/Lookup/', status_dogovor.StatusDogovor_Lookup),
    path('StatusDogovor/Info/', status_dogovor.StatusDogovor_Info),
    path('StatusDogovor/Copy', status_dogovor.StatusDogovor_Copy),

]
