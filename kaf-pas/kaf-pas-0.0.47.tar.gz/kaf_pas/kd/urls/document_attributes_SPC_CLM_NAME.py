from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_NAME

urlpatterns = [

    path('Document_attributes_SPC_CLM_NAME/Fetch/', document_attributes_SPC_CLM_NAME.Document_attributes_SPC_CLM_NAME_Fetch),
    path('Document_attributes_SPC_CLM_NAME/Add', document_attributes_SPC_CLM_NAME.Document_attributes_SPC_CLM_NAME_Add),
    path('Document_attributes_SPC_CLM_NAME/Update', document_attributes_SPC_CLM_NAME.Document_attributes_SPC_CLM_NAME_Update),
    path('Document_attributes_SPC_CLM_NAME/Remove', document_attributes_SPC_CLM_NAME.Document_attributes_SPC_CLM_NAME_Remove),
    path('Document_attributes_SPC_CLM_NAME/Lookup/', document_attributes_SPC_CLM_NAME.Document_attributes_SPC_CLM_NAME_Lookup),
    path('Document_attributes_SPC_CLM_NAME/Info/', document_attributes_SPC_CLM_NAME.Document_attributes_SPC_CLM_NAME_Info),
    path('Document_attributes_SPC_CLM_NAME/Copy', document_attributes_SPC_CLM_NAME.Document_attributes_SPC_CLM_NAME_Copy),

]
