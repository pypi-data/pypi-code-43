from django.urls import path

from kaf_pas.kd.views import document_attributes_STMP_1

urlpatterns = [

    path('Document_attributes_STMP_1/Fetch/', document_attributes_STMP_1.Document_attributes_STMP_1_Fetch),
    path('Document_attributes_STMP_1/Add', document_attributes_STMP_1.Document_attributes_STMP_1_Add),
    path('Document_attributes_STMP_1/Update', document_attributes_STMP_1.Document_attributes_STMP_1_Update),
    path('Document_attributes_STMP_1/Remove', document_attributes_STMP_1.Document_attributes_STMP_1_Remove),
    path('Document_attributes_STMP_1/Lookup/', document_attributes_STMP_1.Document_attributes_STMP_1_Lookup),
    path('Document_attributes_STMP_1/Info/', document_attributes_STMP_1.Document_attributes_STMP_1_Info),
    path('Document_attributes_STMP_1/Copy', document_attributes_STMP_1.Document_attributes_STMP_1_Copy),

]
