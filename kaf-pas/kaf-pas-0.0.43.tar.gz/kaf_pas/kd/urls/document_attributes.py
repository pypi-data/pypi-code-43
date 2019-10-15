from django.urls import path

from kaf_pas.kd.views import document_attributes

urlpatterns = [
    path('Document_attributes/Fetch/', document_attributes.Document_attributes_Fetch),
    path('Document_attributes/Add', document_attributes.Document_attributes_Add),
    path('Document_attributes/Update', document_attributes.Document_attributes_Update),
    path('Document_attributes/Remove', document_attributes.Document_attributes_Remove),
    path('Document_attributes/Lookup/', document_attributes.Document_attributes_Lookup),
    path('Document_attributes/Info/', document_attributes.Document_attributes_Info),
]
