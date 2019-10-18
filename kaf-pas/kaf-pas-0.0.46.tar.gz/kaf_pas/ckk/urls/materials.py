from django.urls import path

from kaf_pas.ckk.views import materials

urlpatterns = [

    path('Materials/Fetch/', materials.Materials_Fetch),
    path('Materials/Add', materials.Materials_Add),
    path('Materials/Update', materials.Materials_Update),
    path('Materials/Remove', materials.Materials_Remove),
    path('Materials/Lookup/', materials.Materials_Lookup),
    path('Materials/Info/', materials.Materials_Info),

]
