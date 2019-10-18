from django.urls import path

from kaf_pas.kd.views import document_attributes_STMP_2

urlpatterns = [

    path('Document_attributes_STMP_2/Fetch/', document_attributes_STMP_2.Document_attributes_STMP_2_Fetch),
    path('Document_attributes_STMP_2/Add', document_attributes_STMP_2.Document_attributes_STMP_2_Add),
    path('Document_attributes_STMP_2/Update', document_attributes_STMP_2.Document_attributes_STMP_2_Update),
    path('Document_attributes_STMP_2/Remove', document_attributes_STMP_2.Document_attributes_STMP_2_Remove),
    path('Document_attributes_STMP_2/Lookup/', document_attributes_STMP_2.Document_attributes_STMP_2_Lookup),
    path('Document_attributes_STMP_2/Info/', document_attributes_STMP_2.Document_attributes_STMP_2_Info),
    path('Document_attributes_STMP_2/Copy', document_attributes_STMP_2.Document_attributes_STMP_2_Copy),

]
