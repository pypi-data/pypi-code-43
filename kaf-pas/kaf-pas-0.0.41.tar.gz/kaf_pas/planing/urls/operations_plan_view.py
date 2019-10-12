from django.urls import path

from kaf_pas.planing.views import operations_plan_view

urlpatterns = [

    path('Operations_plan_view/Fetch/', operations_plan_view.Operations_plan_view_Fetch),
    path('Operations_plan_view/Add', operations_plan_view.Operations_plan_view_Add),
    path('Operations_plan_view/Update', operations_plan_view.Operations_plan_view_Update),
    path('Operations_plan_view/Remove', operations_plan_view.Operations_plan_view_Remove),
    path('Operations_plan_view/Lookup/', operations_plan_view.Operations_plan_view_Lookup),
    path('Operations_plan_view/Info/', operations_plan_view.Operations_plan_view_Info),
    path('Operations_plan_view/Copy', operations_plan_view.Operations_plan_view_Copy),

]
