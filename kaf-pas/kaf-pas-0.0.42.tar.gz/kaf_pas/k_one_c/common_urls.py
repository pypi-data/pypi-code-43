from django.urls import path, include

urlpatterns = [
    path('logic/', include('kaf_pas.k_one_c.urls.nomenklatura')),
]
