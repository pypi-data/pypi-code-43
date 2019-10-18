from django.urls import path

from kaf_pas.sales.views import precent_materials

urlpatterns = [

    path('Precent_materials/Fetch/', precent_materials.Precent_materials_Fetch),
    path('Precent_materials/Add', precent_materials.Precent_materials_Add),
    path('Precent_materials/Update', precent_materials.Precent_materials_Update),
    path('Precent_materials/Remove', precent_materials.Precent_materials_Remove),
    path('Precent_materials/Lookup/', precent_materials.Precent_materials_Lookup),
    path('Precent_materials/Info/', precent_materials.Precent_materials_Info),

]
