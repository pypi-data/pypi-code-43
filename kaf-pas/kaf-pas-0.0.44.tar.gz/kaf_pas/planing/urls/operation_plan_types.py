from django.urls import path

from kaf_pas.planing.views import operation_plan_types

urlpatterns = [

    path('OperationPlanTypes/Fetch/', operation_plan_types.Operation_plan_types_Fetch),
    path('OperationPlanTypes/Add', operation_plan_types.Operation_plan_types_Add),
    path('OperationPlanTypes/Update', operation_plan_types.Operation_plan_types_Update),
    path('OperationPlanTypes/Remove', operation_plan_types.Operation_plan_types_Remove),
    path('OperationPlanTypes/Lookup/', operation_plan_types.Operation_plan_types_Lookup),
    path('OperationPlanTypes/Info/', operation_plan_types.Operation_plan_types_Info),
    path('OperationPlanTypes/Copy', operation_plan_types.Operation_plan_types_Copy),

]
