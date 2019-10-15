from django.conf.urls import url

from . import views


urlpatterns = [
    url('^id4me/login/$', views.login, name="id4me_login"),
    url('^id4me/callback/$', views.callback, name='id4me_callback'),
]

