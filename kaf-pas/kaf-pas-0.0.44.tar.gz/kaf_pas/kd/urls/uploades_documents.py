from django.urls import path

from kaf_pas.kd.views import uploades_documents

urlpatterns = [

    path('Uploades_documents/Fetch/', uploades_documents.Uploades_documents_Fetch),
    path('Uploades_documents/Add', uploades_documents.Uploades_documents_Add),
    path('Uploades_documents/Update', uploades_documents.Uploades_documents_Update),
    path('Uploades_documents/Remove', uploades_documents.Uploades_documents_Remove),
    path('Uploades_documents/Lookup/', uploades_documents.Uploades_documents_Lookup),
    path('Uploades_documents/Info/', uploades_documents.Uploades_documents_Info),
    path('Uploades_documents/Copy', uploades_documents.Uploades_documents_Copy),

]
