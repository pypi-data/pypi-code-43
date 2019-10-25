from django.urls import path

from kaf_pas.ckk.views import attr_type

urlpatterns = [

    path('Attr_type/Fetch/', attr_type.Attr_type_Fetch),
    path('Attr_type/Add', attr_type.Attr_type_Add),
    path('Attr_type/Update', attr_type.Attr_type_Update),
    path('Attr_type/Remove', attr_type.Attr_type_Remove),
    path('Attr_type/Lookup/', attr_type.Attr_type_Lookup),
    path('Attr_type/Info/', attr_type.Attr_type_Info),

]
