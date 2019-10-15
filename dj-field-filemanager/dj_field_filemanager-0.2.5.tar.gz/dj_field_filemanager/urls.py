try:
    from django.urls import re_path
except ImportError:  # Django<2.0
    from django.conf.urls import url as re_path

from .api import ModelViewSet, StorageViewSet

storage_list = StorageViewSet.as_view({'get': 'list', 'post': 'create'})
storage_detail = StorageViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

model_list = ModelViewSet.as_view({'get': 'list', 'post': 'create'})
model_detail = ModelViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    re_path(r'^(?P<model>[\w\.]+)/(?P<parent_field>[\w-]+)/(?P<parent_pk>[\d]+)/(?P<pk>.*)/$', model_detail,
            name='model_view_detail'),
    re_path(r'^(?P<model>[\w\.]+)/(?P<parent_field>[\w-]+)/(?P<parent_pk>[\d]+)/$', model_list,
            name='model_view_list'),

    re_path(r'^(?P<code>[\w\.]+)/(?P<pk>.*)/$', storage_detail, name='storage_view_detail'),
    re_path(r'^(?P<code>[\w\.]+)/$', storage_list, name='storage_view_list'),
]
