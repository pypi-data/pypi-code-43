from django.urls import path

from kaf_pas.kd.views import pathes

urlpatterns = [

    path('Pathes/Fetch/', pathes.Pathes_Fetch),
    path('Pathes/Add', pathes.Pathes_Add),
    path('Pathes/Update', pathes.Pathes_Update),
    path('Pathes/Remove', pathes.Pathes_Remove),
    path('Pathes/Lookup/', pathes.Pathes_Lookup),
    path('Pathes/Info/', pathes.Pathes_Info),

]
