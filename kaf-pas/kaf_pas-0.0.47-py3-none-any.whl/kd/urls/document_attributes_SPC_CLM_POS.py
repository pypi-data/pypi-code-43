from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_POS

urlpatterns = [

    path('Document_attributes_SPC_CLM_POS/Fetch/', document_attributes_SPC_CLM_POS.Document_attributes_SPC_CLM_POS_Fetch),
    path('Document_attributes_SPC_CLM_POS/Add', document_attributes_SPC_CLM_POS.Document_attributes_SPC_CLM_POS_Add),
    path('Document_attributes_SPC_CLM_POS/Update', document_attributes_SPC_CLM_POS.Document_attributes_SPC_CLM_POS_Update),
    path('Document_attributes_SPC_CLM_POS/Remove', document_attributes_SPC_CLM_POS.Document_attributes_SPC_CLM_POS_Remove),
    path('Document_attributes_SPC_CLM_POS/Lookup/', document_attributes_SPC_CLM_POS.Document_attributes_SPC_CLM_POS_Lookup),
    path('Document_attributes_SPC_CLM_POS/Info/', document_attributes_SPC_CLM_POS.Document_attributes_SPC_CLM_POS_Info),
    path('Document_attributes_SPC_CLM_POS/Copy', document_attributes_SPC_CLM_POS.Document_attributes_SPC_CLM_POS_Copy),

]
