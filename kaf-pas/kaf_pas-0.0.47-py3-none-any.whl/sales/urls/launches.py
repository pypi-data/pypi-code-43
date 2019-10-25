from django.urls import path

from kaf_pas.sales.views import launches

urlpatterns = [

    path('Launches/Fetch/', launches.Launches_Fetch),
    path('Launches/Add', launches.Launches_Add),
    path('Launches/Update', launches.Launches_Update),
    path('Launches/Remove', launches.Launches_Remove),
    path('Launches/Lookup/', launches.Launches_Lookup),
    path('Launches/Info/', launches.Launches_Info),
    path('Launches/Copy', launches.Launches_Copy),

]
