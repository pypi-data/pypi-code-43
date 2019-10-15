from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_MASSA

urlpatterns = [

    path('Document_attributes_SPC_CLM_MASSA/Fetch/', document_attributes_SPC_CLM_MASSA.Document_attributes_SPC_CLM_MASSA_Fetch),
    path('Document_attributes_SPC_CLM_MASSA/Add', document_attributes_SPC_CLM_MASSA.Document_attributes_SPC_CLM_MASSA_Add),
    path('Document_attributes_SPC_CLM_MASSA/Update', document_attributes_SPC_CLM_MASSA.Document_attributes_SPC_CLM_MASSA_Update),
    path('Document_attributes_SPC_CLM_MASSA/Remove', document_attributes_SPC_CLM_MASSA.Document_attributes_SPC_CLM_MASSA_Remove),
    path('Document_attributes_SPC_CLM_MASSA/Lookup/', document_attributes_SPC_CLM_MASSA.Document_attributes_SPC_CLM_MASSA_Lookup),
    path('Document_attributes_SPC_CLM_MASSA/Info/', document_attributes_SPC_CLM_MASSA.Document_attributes_SPC_CLM_MASSA_Info),
    path('Document_attributes_SPC_CLM_MASSA/Copy', document_attributes_SPC_CLM_MASSA.Document_attributes_SPC_CLM_MASSA_Copy),

]
