from django.urls import path

from kaf_pas.kd.views import document_attr_cross

urlpatterns = [

    path('Document_attr_cross/Fetch/', document_attr_cross.Document_attr_cross_Fetch),
    path('Document_attr_cross/Add', document_attr_cross.Document_attr_cross_Add),
    path('Document_attr_cross/Update', document_attr_cross.Document_attr_cross_Update),
    path('Document_attr_cross/Remove', document_attr_cross.Document_attr_cross_Remove),
    path('Document_attr_cross/Lookup/', document_attr_cross.Document_attr_cross_Lookup),
    path('Document_attr_cross/Info/', document_attr_cross.Document_attr_cross_Info),

]
