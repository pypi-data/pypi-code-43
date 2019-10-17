from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_ZONE

urlpatterns = [

    path('Document_attributes_SPC_CLM_ZONE/Fetch/', document_attributes_SPC_CLM_ZONE.Document_attributes_SPC_CLM_ZONE_Fetch),
    path('Document_attributes_SPC_CLM_ZONE/Add', document_attributes_SPC_CLM_ZONE.Document_attributes_SPC_CLM_ZONE_Add),
    path('Document_attributes_SPC_CLM_ZONE/Update', document_attributes_SPC_CLM_ZONE.Document_attributes_SPC_CLM_ZONE_Update),
    path('Document_attributes_SPC_CLM_ZONE/Remove', document_attributes_SPC_CLM_ZONE.Document_attributes_SPC_CLM_ZONE_Remove),
    path('Document_attributes_SPC_CLM_ZONE/Lookup/', document_attributes_SPC_CLM_ZONE.Document_attributes_SPC_CLM_ZONE_Lookup),
    path('Document_attributes_SPC_CLM_ZONE/Info/', document_attributes_SPC_CLM_ZONE.Document_attributes_SPC_CLM_ZONE_Info),
    path('Document_attributes_SPC_CLM_ZONE/Copy', document_attributes_SPC_CLM_ZONE.Document_attributes_SPC_CLM_ZONE_Copy),

]
