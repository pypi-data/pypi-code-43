from django.urls import path

from kaf_pas.kd.views import documents_view

urlpatterns = [

    path('Documents_view/Fetch/', documents_view.Documents_view_Fetch),
    path('Documents_bad_view/Fetch/', documents_view.Documents_bad_view_Fetch),
    path('Documents_view/Add', documents_view.Documents_view_Add),
    path('Documents_view/Update', documents_view.Documents_view_Update),
    path('Documents_view/Remove', documents_view.Documents_view_Remove),
    path('Documents_view/Lookup/', documents_view.Documents_view_Lookup),
    path('Documents_view/Info/', documents_view.Documents_view_Info),
    path('Documents_bad_view/Info/', documents_view.Documents_view_bad_Info),

]
