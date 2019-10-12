from django.urls import path

from kaf_pas.kd.views import documents_thumb10

urlpatterns = [

    path('Documents_thumb10/Fetch/', documents_thumb10.Documents_thumb10_Fetch),
    path('Documents_thumb10/Add', documents_thumb10.Documents_thumb10_Add),
    path('Documents_thumb10/Update', documents_thumb10.Documents_thumb10_Update),
    path('Documents_thumb10/Remove', documents_thumb10.Documents_thumb10_Remove),
    path('Documents_thumb10/Lookup/', documents_thumb10.Documents_thumb10_Lookup),
    path('Documents_thumb10/Info/', documents_thumb10.Documents_thumb10_Info),

]
