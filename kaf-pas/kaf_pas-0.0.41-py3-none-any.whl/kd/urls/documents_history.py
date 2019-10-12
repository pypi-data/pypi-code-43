from django.urls import path

from kaf_pas.kd.views import documents_history

urlpatterns = [

    path('Documents_history/Fetch/', documents_history.Documents_history_Fetch),
    path('Documents_history/Add', documents_history.Documents_history_Add),
    path('Documents_history/Update', documents_history.Documents_history_Update),
    path('Documents_history/Remove', documents_history.Documents_history_Remove),
    path('Documents_history/Lookup/', documents_history.Documents_history_Lookup),
    path('Documents_history/Info/', documents_history.Documents_history_Info),
    path('Documents_history/Copy', documents_history.Documents_history_Copy),

]
