from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_COUNT

urlpatterns = [

    path('Document_attributes_SPC_CLM_COUNT/Fetch/', document_attributes_SPC_CLM_COUNT.Document_attributes_SPC_CLM_COUNT_Fetch),
    path('Document_attributes_SPC_CLM_COUNT/Add', document_attributes_SPC_CLM_COUNT.Document_attributes_SPC_CLM_COUNT_Add),
    path('Document_attributes_SPC_CLM_COUNT/Update', document_attributes_SPC_CLM_COUNT.Document_attributes_SPC_CLM_COUNT_Update),
    path('Document_attributes_SPC_CLM_COUNT/Remove', document_attributes_SPC_CLM_COUNT.Document_attributes_SPC_CLM_COUNT_Remove),
    path('Document_attributes_SPC_CLM_COUNT/Lookup/', document_attributes_SPC_CLM_COUNT.Document_attributes_SPC_CLM_COUNT_Lookup),
    path('Document_attributes_SPC_CLM_COUNT/Info/', document_attributes_SPC_CLM_COUNT.Document_attributes_SPC_CLM_COUNT_Info),
    path('Document_attributes_SPC_CLM_COUNT/Copy', document_attributes_SPC_CLM_COUNT.Document_attributes_SPC_CLM_COUNT_Copy),

]
