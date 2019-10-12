from django.urls import path

from kaf_pas.planing.views import operations_plan

urlpatterns = [

    path('OperationsPlan/Fetch/', operations_plan.Operations_plan_Fetch),
    path('OperationsPlan/Add', operations_plan.Operations_plan_Add),
    path('OperationsPlan/Update', operations_plan.Operations_plan_Update),
    path('OperationsPlan/Remove', operations_plan.Operations_plan_Remove),
    path('OperationsPlan/Lookup/', operations_plan.Operations_plan_Lookup),
    path('OperationsPlan/Info/', operations_plan.Operations_plan_Info),
    path('OperationsPlan/Copy', operations_plan.Operations_plan_Copy),

]
