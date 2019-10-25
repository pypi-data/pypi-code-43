from django.urls import path

from kaf_pas.sales.views import status_launch

urlpatterns = [

    path('Status_launch/Fetch/', status_launch.Status_launch_Fetch),
    path('Status_launch/Add', status_launch.Status_launch_Add),
    path('Status_launch/Update', status_launch.Status_launch_Update),
    path('Status_launch/Remove', status_launch.Status_launch_Remove),
    path('Status_launch/Lookup/', status_launch.Status_launch_Lookup),
    path('Status_launch/Info/', status_launch.Status_launch_Info),
    path('Status_launch/Copy', status_launch.Status_launch_Copy),

]
