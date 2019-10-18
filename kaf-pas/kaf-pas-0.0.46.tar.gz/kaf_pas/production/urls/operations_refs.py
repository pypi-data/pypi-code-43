from django.urls import path

from kaf_pas.production.views import operations_refs

urlpatterns = [

    path('operations_refs/Fetch/', operations_refs.Operations_refs_Fetch),
    path('operations_refs/Add', operations_refs.Operations_refs_Add),
    path('operations_refs/Update', operations_refs.Operations_refs_Update),
    path('operations_refs/Remove', operations_refs.Operations_refs_Remove),
    path('operations_refs/Lookup/', operations_refs.Operations_refs_Lookup),
    path('operations_refs/Info/', operations_refs.Operations_refs_Info),

]
