from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_FACTORY

urlpatterns = [

    path('Document_attributes_SPC_CLM_FACTORY/Fetch/', document_attributes_SPC_CLM_FACTORY.Document_attributes_SPC_CLM_FACTORY_Fetch),
    path('Document_attributes_SPC_CLM_FACTORY/Add', document_attributes_SPC_CLM_FACTORY.Document_attributes_SPC_CLM_FACTORY_Add),
    path('Document_attributes_SPC_CLM_FACTORY/Update', document_attributes_SPC_CLM_FACTORY.Document_attributes_SPC_CLM_FACTORY_Update),
    path('Document_attributes_SPC_CLM_FACTORY/Remove', document_attributes_SPC_CLM_FACTORY.Document_attributes_SPC_CLM_FACTORY_Remove),
    path('Document_attributes_SPC_CLM_FACTORY/Lookup/', document_attributes_SPC_CLM_FACTORY.Document_attributes_SPC_CLM_FACTORY_Lookup),
    path('Document_attributes_SPC_CLM_FACTORY/Info/', document_attributes_SPC_CLM_FACTORY.Document_attributes_SPC_CLM_FACTORY_Info),
    path('Document_attributes_SPC_CLM_FACTORY/Copy', document_attributes_SPC_CLM_FACTORY.Document_attributes_SPC_CLM_FACTORY_Copy),

]
