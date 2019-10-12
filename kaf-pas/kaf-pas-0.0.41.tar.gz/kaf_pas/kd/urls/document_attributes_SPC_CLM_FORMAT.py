from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_FORMAT

urlpatterns = [

    path('Document_attributes_SPC_CLM_FORMAT/Fetch/', document_attributes_SPC_CLM_FORMAT.Document_attributes_SPC_CLM_FORMAT_Fetch),
    path('Document_attributes_SPC_CLM_FORMAT/Add', document_attributes_SPC_CLM_FORMAT.Document_attributes_SPC_CLM_FORMAT_Add),
    path('Document_attributes_SPC_CLM_FORMAT/Update', document_attributes_SPC_CLM_FORMAT.Document_attributes_SPC_CLM_FORMAT_Update),
    path('Document_attributes_SPC_CLM_FORMAT/Remove', document_attributes_SPC_CLM_FORMAT.Document_attributes_SPC_CLM_FORMAT_Remove),
    path('Document_attributes_SPC_CLM_FORMAT/Lookup/', document_attributes_SPC_CLM_FORMAT.Document_attributes_SPC_CLM_FORMAT_Lookup),
    path('Document_attributes_SPC_CLM_FORMAT/Info/', document_attributes_SPC_CLM_FORMAT.Document_attributes_SPC_CLM_FORMAT_Info),
    path('Document_attributes_SPC_CLM_FORMAT/Copy', document_attributes_SPC_CLM_FORMAT.Document_attributes_SPC_CLM_FORMAT_Copy),

]
