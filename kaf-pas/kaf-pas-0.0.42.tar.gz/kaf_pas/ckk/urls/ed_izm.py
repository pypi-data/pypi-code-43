from django.urls import path

from kaf_pas.ckk.views import ed_izm

urlpatterns = [

    path('Ed_izm/Fetch/', ed_izm.Ed_izm_Fetch),
    path('Ed_izm/Add', ed_izm.Ed_izm_Add),
    path('Ed_izm/Update', ed_izm.Ed_izm_Update),
    path('Ed_izm/Remove', ed_izm.Ed_izm_Remove),
    path('Ed_izm/Lookup/', ed_izm.Ed_izm_Lookup),
    path('Ed_izm/Info/', ed_izm.Ed_izm_Info),

]
