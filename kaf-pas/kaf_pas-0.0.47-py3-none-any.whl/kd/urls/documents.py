from django.urls import path

from kaf_pas.kd.views import documents

urlpatterns = [

    path('Documents/Fetch/', documents.Documents_Fetch),
    path('Documents/Add', documents.Documents_Add),
    path('Documents/Update', documents.Documents_Update),
    path('Documents/Remove', documents.Documents_Remove),
    path('Documents/Lookup/', documents.Documents_Lookup),
    path('Documents/Info/', documents.Documents_Info),
    path('Documents/MakeItem', documents.Documents_MakeItem),
    path('Documents/Documents_Treat', documents.Documents_Treat),
    path('Documents/ReloadDoc', documents.Documents_ReloadDoc),
]
