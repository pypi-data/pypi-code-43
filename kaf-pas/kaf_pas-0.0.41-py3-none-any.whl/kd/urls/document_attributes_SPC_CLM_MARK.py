from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_MARK

urlpatterns = [

    path('Document_attributes_SPC_CLM_MARK/Fetch/', document_attributes_SPC_CLM_MARK.Document_attributes_SPC_CLM_MARK_Fetch),
    path('Document_attributes_SPC_CLM_MARK/Add', document_attributes_SPC_CLM_MARK.Document_attributes_SPC_CLM_MARK_Add),
    path('Document_attributes_SPC_CLM_MARK/Update', document_attributes_SPC_CLM_MARK.Document_attributes_SPC_CLM_MARK_Update),
    path('Document_attributes_SPC_CLM_MARK/Remove', document_attributes_SPC_CLM_MARK.Document_attributes_SPC_CLM_MARK_Remove),
    path('Document_attributes_SPC_CLM_MARK/Lookup/', document_attributes_SPC_CLM_MARK.Document_attributes_SPC_CLM_MARK_Lookup),
    path('Document_attributes_SPC_CLM_MARK/Info/', document_attributes_SPC_CLM_MARK.Document_attributes_SPC_CLM_MARK_Info),
    path('Document_attributes_SPC_CLM_MARK/Copy', document_attributes_SPC_CLM_MARK.Document_attributes_SPC_CLM_MARK_Copy),

]
