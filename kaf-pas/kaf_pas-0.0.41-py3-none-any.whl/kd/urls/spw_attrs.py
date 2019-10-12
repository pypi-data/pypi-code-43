from django.urls import path

from kaf_pas.kd.views import spw_attrs

urlpatterns = [

    path('Spw_attrs/Fetch/', spw_attrs.Spw_attrs_Fetch),
    path('Spw_attrs/Info/', spw_attrs.Spw_attrs_Info),
    path('Spw_attrs/Update', spw_attrs.Spw_attrs_Update),
    # path('Spw_attrs/Remove', spw_attrs.Spw_attrs_Remove),
]
