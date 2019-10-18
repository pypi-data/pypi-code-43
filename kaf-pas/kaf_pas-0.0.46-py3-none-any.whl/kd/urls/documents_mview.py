from django.urls import path

from kaf_pas.kd.views import documents_mview

urlpatterns = [

    path('Documents_mview/Fetch/', documents_mview.Documents_mview_Fetch),
    path('Documents_bad_mview/Fetch/', documents_mview.Documents_bad_mview_Fetch),
    path('Documents_mview/Add', documents_mview.Documents_mview_Add),
    path('Documents_mview/Update', documents_mview.Documents_mview_Update),
    path('Documents_mview/Remove', documents_mview.Documents_mview_Remove),
    path('Documents_mview/Lookup/', documents_mview.Documents_mview_Lookup),
    path('Documents_mview/Info/', documents_mview.Documents_mview_Info),
    path('Documents_bad_mview/Info/', documents_mview.Documents_mview_bad_Info),
    path('Documents_mview/RefreshMView', documents_mview.Documents_mview_RefreshMView),

]
