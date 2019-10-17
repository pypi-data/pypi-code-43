from django.urls import path

from kaf_pas.ckk.views import files_askon

urlpatterns = [

    path('Files_askon/Fetch/', files_askon.Files_askon_Fetch),
    path('Files_askon/Add', files_askon.Files_askon_Add),
    path('Files_askon/Update', files_askon.Files_askon_Update),
    path('Files_askon/Remove', files_askon.Files_askon_Remove),
    path('Files_askon/Lookup/', files_askon.Files_askon_Lookup),
    path('Files_askon/Info/', files_askon.Files_askon_Info),
    path('Files_askon/Copy', files_askon.Files_askon_Copy),

]
