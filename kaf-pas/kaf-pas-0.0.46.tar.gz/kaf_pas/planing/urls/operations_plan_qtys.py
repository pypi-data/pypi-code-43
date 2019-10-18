from django.urls import path

from kaf_pas.planing.views import operations_plan_qtys

urlpatterns = [

    path('Operations_plan_qtys/Fetch/', operations_plan_qtys.Operations_plan_qtys_Fetch),
    path('Operations_plan_qtys/Add', operations_plan_qtys.Operations_plan_qtys_Add),
    path('Operations_plan_qtys/Update', operations_plan_qtys.Operations_plan_qtys_Update),
    path('Operations_plan_qtys/Remove', operations_plan_qtys.Operations_plan_qtys_Remove),
    path('Operations_plan_qtys/Lookup/', operations_plan_qtys.Operations_plan_qtys_Lookup),
    path('Operations_plan_qtys/Info/', operations_plan_qtys.Operations_plan_qtys_Info),
    path('Operations_plan_qtys/Copy', operations_plan_qtys.Operations_plan_qtys_Copy),

]
