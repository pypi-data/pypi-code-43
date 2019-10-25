from django.urls import path

from kaf_pas.kd.views import document_attributes_SPC_CLM_USER_

urlpatterns = [

    path('Document_attributes_SPC_CLM_USER/Fetch/', document_attributes_SPC_CLM_USER_.Document_attributes_SPC_CLM_USER__Fetch),
    path('Document_attributes_SPC_CLM_USER/Add', document_attributes_SPC_CLM_USER_.Document_attributes_SPC_CLM_USER__Add),
    path('Document_attributes_SPC_CLM_USER/Update', document_attributes_SPC_CLM_USER_.Document_attributes_SPC_CLM_USER__Update),
    path('Document_attributes_SPC_CLM_USER/Remove', document_attributes_SPC_CLM_USER_.Document_attributes_SPC_CLM_USER__Remove),
    path('Document_attributes_SPC_CLM_USER/Lookup/', document_attributes_SPC_CLM_USER_.Document_attributes_SPC_CLM_USER__Lookup),
    path('Document_attributes_SPC_CLM_USER/Info/', document_attributes_SPC_CLM_USER_.Document_attributes_SPC_CLM_USER__Info),
    path('Document_attributes_SPC_CLM_USER/Copy', document_attributes_SPC_CLM_USER_.Document_attributes_SPC_CLM_USER__Copy),

]
