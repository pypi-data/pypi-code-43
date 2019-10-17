from django.urls import path

from kaf_pas.kd.views import pathes_view

urlpatterns = [

    path('Pathes_view/Fetch/', pathes_view.Pathes_view_Fetch),
    path('Pathes_view/Add', pathes_view.Pathes_view_Add),
    path('Pathes_view/Update', pathes_view.Pathes_view_Update),
    path('Pathes_view/Remove', pathes_view.Pathes_view_Remove),
    path('Pathes_view/Lookup/', pathes_view.Pathes_view_Lookup),
    path('Pathes_view/Info/', pathes_view.Pathes_view_Info),

]
