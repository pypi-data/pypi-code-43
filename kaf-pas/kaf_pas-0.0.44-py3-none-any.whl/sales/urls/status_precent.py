from django.urls import path

from kaf_pas.sales.views import status_precent

urlpatterns = [

    path('StatusPrecent/Fetch/', status_precent.StatusPrecent_Fetch),
    path('StatusPrecent/Add', status_precent.StatusPrecent_Add),
    path('StatusPrecent/Update', status_precent.StatusPrecent_Update),
    path('StatusPrecent/Remove', status_precent.StatusPrecent_Remove),
    path('StatusPrecent/Lookup/', status_precent.StatusPrecent_Lookup),
    path('StatusPrecent/Info/', status_precent.StatusPrecent_Info),
    path('StatusPrecent/Copy', status_precent.StatusPrecent_Copy),

]
