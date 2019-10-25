from django.urls import path

from kaf_pas.sales.views import precent_dogovors

urlpatterns = [

    path('Precent_dogovors/Fetch/', precent_dogovors.Precent_dogovors_Fetch),
    path('Precent_dogovors/Add', precent_dogovors.Precent_dogovors_Add),
    path('Precent_dogovors/Update', precent_dogovors.Precent_dogovors_Update),
    path('Precent_dogovors/Remove', precent_dogovors.Precent_dogovors_Remove),
    path('Precent_dogovors/Lookup/', precent_dogovors.Precent_dogovors_Lookup),
    path('Precent_dogovors/Info/', precent_dogovors.Precent_dogovors_Info),
    path('Precent_dogovors/Copy', precent_dogovors.Precent_dogovors_Copy),

]
