from django.urls import path

from kaf_pas.planing.views import operations_plan_status

urlpatterns = [

    path('OperationsPlanStatus/Fetch/', operations_plan_status.OperationsPlanStatus_Fetch),
    path('OperationsPlanStatus/Add', operations_plan_status.OperationsPlanStatus_Add),
    path('OperationsPlanStatus/Update', operations_plan_status.OperationsPlanStatus_Update),
    path('OperationsPlanStatus/Remove', operations_plan_status.OperationsPlanStatus_Remove),
    path('OperationsPlanStatus/Lookup/', operations_plan_status.OperationsPlanStatus_Lookup),
    path('OperationsPlanStatus/Info/', operations_plan_status.OperationsPlanStatus_Info),
    path('OperationsPlanStatus/Copy', operations_plan_status.OperationsPlanStatus_Copy),

]
