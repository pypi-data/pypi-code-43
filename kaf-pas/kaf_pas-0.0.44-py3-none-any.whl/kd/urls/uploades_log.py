from django.urls import path

from kaf_pas.kd.views import uploades_log

urlpatterns = [

    path('Uploades_log/Fetch/', uploades_log.Uploades_log_Fetch),
    path('Uploades_log/Add', uploades_log.Uploades_log_Add),
    path('Uploades_log/Update', uploades_log.Uploades_log_Update),
    path('Uploades_log/Remove', uploades_log.Uploades_log_Remove),
    path('Uploades_log/Lookup/', uploades_log.Uploades_log_Lookup),
    path('Uploades_log/Info/', uploades_log.Uploades_log_Info),
    path('Uploades_log/Copy', uploades_log.Uploades_log_Copy),

]
