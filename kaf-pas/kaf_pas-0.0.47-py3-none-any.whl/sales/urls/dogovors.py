from django.urls import path

from kaf_pas.sales.views import dogovors, precent

urlpatterns = [

    path('Dogovors/Fetch/', dogovors.Dogovors_Fetch),
    path('Dogovors/Add', dogovors.Dogovors_Add),
    path('Dogovors/Update', dogovors.Dogovors_Update),
    path('Dogovors/Remove', dogovors.Dogovors_Remove),
    path('Dogovors/Lookup/', dogovors.Dogovors_Lookup),
    path('Dogovors/Info/', dogovors.Dogovors_Info),
    path('Dogovors/Copy', dogovors.Dogovors_Copy),
    path('Dogovors/Upload', dogovors.Dogovor_UploadFile),
    path('Dogovors/Download/', dogovors.Dogovort_DownloadFile),
]
