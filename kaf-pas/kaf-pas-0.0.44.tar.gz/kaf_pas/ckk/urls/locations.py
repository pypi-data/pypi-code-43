from django.urls import path

from kaf_pas.ckk.views import locations

urlpatterns = [

    path('Locations/Fetch/', locations.Locations_Fetch),
    path('Locations/Add', locations.Locations_Add),
    path('Locations/Update', locations.Locations_Update),
    path('Locations/Remove', locations.Locations_Remove),
    path('Locations/Lookup/', locations.Locations_Lookup),
    path('Locations/Info/', locations.Locations_Info),

]
