from django.urls import path

from kaf_pas.planing.views import prod_task_importances

urlpatterns = [

    path('Prod_task_importances/Fetch/', prod_task_importances.Prod_task_importances_Fetch),
    path('Prod_task_importances/Add', prod_task_importances.Prod_task_importances_Add),
    path('Prod_task_importances/Update', prod_task_importances.Prod_task_importances_Update),
    path('Prod_task_importances/Remove', prod_task_importances.Prod_task_importances_Remove),
    path('Prod_task_importances/Lookup/', prod_task_importances.Prod_task_importances_Lookup),
    path('Prod_task_importances/Info/', prod_task_importances.Prod_task_importances_Info),
    path('Prod_task_importances/Copy', prod_task_importances.Prod_task_importances_Copy),

]
