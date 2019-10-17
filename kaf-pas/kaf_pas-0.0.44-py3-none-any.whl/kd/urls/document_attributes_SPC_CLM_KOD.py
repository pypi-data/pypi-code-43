from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_KOD

urlpatterns = [

    path('Document_attributes_SPC_CLM_KOD/Fetch/', document_attributes_SPC_CLM_KOD.Document_attributes_SPC_CLM_KOD_Fetch),
    path('Document_attributes_SPC_CLM_KOD/Add', document_attributes_SPC_CLM_KOD.Document_attributes_SPC_CLM_KOD_Add),
    path('Document_attributes_SPC_CLM_KOD/Update', document_attributes_SPC_CLM_KOD.Document_attributes_SPC_CLM_KOD_Update),
    path('Document_attributes_SPC_CLM_KOD/Remove', document_attributes_SPC_CLM_KOD.Document_attributes_SPC_CLM_KOD_Remove),
    path('Document_attributes_SPC_CLM_KOD/Lookup/', document_attributes_SPC_CLM_KOD.Document_attributes_SPC_CLM_KOD_Lookup),
    path('Document_attributes_SPC_CLM_KOD/Info/', document_attributes_SPC_CLM_KOD.Document_attributes_SPC_CLM_KOD_Info),
    path('Document_attributes_SPC_CLM_KOD/Copy', document_attributes_SPC_CLM_KOD.Document_attributes_SPC_CLM_KOD_Copy),

]
