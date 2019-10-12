from django.urls import path

from kaf_pas.planing.views import operations_plan_refs

urlpatterns = [

    path('OperationsPlanRefs/Fetch/', operations_plan_refs.Operations_plan_refs_Fetch),
    path('OperationsPlanRefs/Add', operations_plan_refs.Operations_plan_refs_Add),
    path('OperationsPlanRefs/Update', operations_plan_refs.Operations_plan_refs_Update),
    path('OperationsPlanRefs/Remove', operations_plan_refs.Operations_plan_refs_Remove),
    path('OperationsPlanRefs/Lookup/', operations_plan_refs.Operations_plan_refs_Lookup),
    path('OperationsPlanRefs/Info/', operations_plan_refs.Operations_plan_refs_Info),
    path('OperationsPlanRefs/Copy', operations_plan_refs.Operations_plan_refs_Copy),

]
