from django.urls import path

from kaf_pas.sales.views import precent

urlpatterns = [

    path('Precent/Fetch/', precent.Precent_Fetch),
    path('Precent/Add', precent.Precent_Add),
    path('Precent/Update', precent.Precent_Update),
    path('Precent/Remove', precent.Precent_Remove),
    path('Precent/Lookup/', precent.Precent_Lookup),
    path('Precent/Info/', precent.Precent_Info),
    path('Precent/Upload', precent.Precent_UploadFile),
    path('Precent/Download/', precent.Precent_DownloadFile),
]
