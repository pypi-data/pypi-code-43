from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_MATERIAL

urlpatterns = [

    path('Document_attributes_SPC_CLM_MATERIAL/Fetch/', document_attributes_SPC_CLM_MATERIAL.Document_attributes_SPC_CLM_MATERIAL_Fetch),
    path('Document_attributes_SPC_CLM_MATERIAL/Add', document_attributes_SPC_CLM_MATERIAL.Document_attributes_SPC_CLM_MATERIAL_Add),
    path('Document_attributes_SPC_CLM_MATERIAL/Update', document_attributes_SPC_CLM_MATERIAL.Document_attributes_SPC_CLM_MATERIAL_Update),
    path('Document_attributes_SPC_CLM_MATERIAL/Remove', document_attributes_SPC_CLM_MATERIAL.Document_attributes_SPC_CLM_MATERIAL_Remove),
    path('Document_attributes_SPC_CLM_MATERIAL/Lookup/', document_attributes_SPC_CLM_MATERIAL.Document_attributes_SPC_CLM_MATERIAL_Lookup),
    path('Document_attributes_SPC_CLM_MATERIAL/Info/', document_attributes_SPC_CLM_MATERIAL.Document_attributes_SPC_CLM_MATERIAL_Info),
    path('Document_attributes_SPC_CLM_MATERIAL/Copy', document_attributes_SPC_CLM_MATERIAL.Document_attributes_SPC_CLM_MATERIAL_Copy),

]
