from django.urls import path

from kaf_pas.production.views import resource

urlpatterns = [

    path('Resource/Fetch/', resource.Resource_Fetch),
    path('Resource/Add', resource.Resource_Add),
    path('Resource/Update', resource.Resource_Update),
    path('Resource/Remove', resource.Resource_Remove),
    path('Resource/Lookup/', resource.Resource_Lookup),
    path('Resource/Info/', resource.Resource_Info),

]
