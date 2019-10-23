from django.conf.urls import url

from .views import (InfluxdbCheckCreateView, InfluxdbCheckUpdateView,
                    duplicate_check)

urlpatterns = [

    url(r'^influxdbcheck/create/',
        view=InfluxdbCheckCreateView.as_view(),
        name='create-influxdb-check'),

    url(r'^influxdbcheck/update/(?P<pk>\d+)/',
        view=InfluxdbCheckUpdateView.as_view(),
        name='update-influxdb-check'),

    url(r'^influxdbCheck/duplicate/(?P<pk>\d+)/',
        view=duplicate_check,
        name='duplicate-influxdb-check')

]
