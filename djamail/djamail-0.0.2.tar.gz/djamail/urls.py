from django.conf.urls import url
from djamail import views

urlpatterns = [
    url(r'^preview$', views.preview),
]
