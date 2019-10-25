from django.urls import path

from kaf_pas.production.views import operation_resources

urlpatterns = [

    path('Operation_resources/Fetch/', operation_resources.Operation_resources_Fetch),
    path('Operation_resources/Add', operation_resources.Operation_resources_Add),
    path('Operation_resources/Update', operation_resources.Operation_resources_Update),
    path('Operation_resources/Remove', operation_resources.Operation_resources_Remove),
    path('Operation_resources/Lookup/', operation_resources.Operation_resources_Lookup),
    path('Operation_resources/Info/', operation_resources.Operation_resources_Info),

]
