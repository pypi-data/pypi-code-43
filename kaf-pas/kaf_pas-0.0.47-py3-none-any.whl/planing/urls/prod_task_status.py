from django.urls import path

from kaf_pas.planing.views import prod_task_status

urlpatterns = [

    path('Prod_task_status/Fetch/', prod_task_status.Prod_task_status_Fetch),
    path('Prod_task_status/Add', prod_task_status.Prod_task_status_Add),
    path('Prod_task_status/Update', prod_task_status.Prod_task_status_Update),
    path('Prod_task_status/Remove', prod_task_status.Prod_task_status_Remove),
    path('Prod_task_status/Lookup/', prod_task_status.Prod_task_status_Lookup),
    path('Prod_task_status/Info/', prod_task_status.Prod_task_status_Info),
    path('Prod_task_status/Copy', prod_task_status.Prod_task_status_Copy),

]
