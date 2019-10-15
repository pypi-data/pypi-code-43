from django.urls import path

from kaf_pas.kd.views import cdw_attrs

urlpatterns = [

    path('Cdw_attrs/Fetch/', cdw_attrs.Cdw_attrs_Fetch),
    path('Cdw_attrs/Add', cdw_attrs.Cdw_attrs_Add),
    path('Cdw_attrs/Update', cdw_attrs.Cdw_attrs_Update),
    path('Cdw_attrs/Remove', cdw_attrs.Cdw_attrs_Remove),
    path('Cdw_attrs/Lookup/', cdw_attrs.Cdw_attrs_Lookup),
    path('Cdw_attrs/Info/', cdw_attrs.Cdw_attrs_Info),

]
