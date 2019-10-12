from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_NOTE

urlpatterns = [

    path('Document_attributes_SPC_CLM_NOTE/Fetch/', document_attributes_SPC_CLM_NOTE.Document_attributes_SPC_CLM_NOTE_Fetch),
    path('Document_attributes_SPC_CLM_NOTE/Add', document_attributes_SPC_CLM_NOTE.Document_attributes_SPC_CLM_NOTE_Add),
    path('Document_attributes_SPC_CLM_NOTE/Update', document_attributes_SPC_CLM_NOTE.Document_attributes_SPC_CLM_NOTE_Update),
    path('Document_attributes_SPC_CLM_NOTE/Remove', document_attributes_SPC_CLM_NOTE.Document_attributes_SPC_CLM_NOTE_Remove),
    path('Document_attributes_SPC_CLM_NOTE/Lookup/', document_attributes_SPC_CLM_NOTE.Document_attributes_SPC_CLM_NOTE_Lookup),
    path('Document_attributes_SPC_CLM_NOTE/Info/', document_attributes_SPC_CLM_NOTE.Document_attributes_SPC_CLM_NOTE_Info),
    path('Document_attributes_SPC_CLM_NOTE/Copy', document_attributes_SPC_CLM_NOTE.Document_attributes_SPC_CLM_NOTE_Copy),

]
