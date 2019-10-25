from django.urls import path

from kaf_pas.planing.views import prod_tasks

urlpatterns = [

    path('Prod_tasks/Fetch/', prod_tasks.Prod_tasks_Fetch),
    path('Prod_tasks/Add', prod_tasks.Prod_tasks_Add),
    path('Prod_tasks/Update', prod_tasks.Prod_tasks_Update),
    path('Prod_tasks/Remove', prod_tasks.Prod_tasks_Remove),
    path('Prod_tasks/Lookup/', prod_tasks.Prod_tasks_Lookup),
    path('Prod_tasks/Info/', prod_tasks.Prod_tasks_Info),
    path('Prod_tasks/Copy', prod_tasks.Prod_tasks_Copy),

]
