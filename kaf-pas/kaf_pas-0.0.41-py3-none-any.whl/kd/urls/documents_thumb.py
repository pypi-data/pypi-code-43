from django.urls import path

from kaf_pas.kd.models.download_file import download_attach_file, download_attach_file_10
from kaf_pas.kd.views import documents_thumb

urlpatterns = [

    path('DocumentsThumb/Fetch/', documents_thumb.Documents_thumb_Fetch),
    path('DocumentsThumb/Add', documents_thumb.Documents_thumb_Add),
    path('DocumentsThumb/Update', documents_thumb.Documents_thumb_Update),
    path('DocumentsThumb/Remove', documents_thumb.Documents_thumb_Remove),
    path('DocumentsThumb/Lookup/', documents_thumb.Documents_thumb_Lookup),
    path('DocumentsThumb/Info/', documents_thumb.Documents_thumb_Info),
    path('DocumentsThumb/Download/<int:id>/', download_attach_file),
    path('DocumentsThumb/Download10/<int:id>/', download_attach_file_10),
]
