from django.urls import path, re_path
from .views import CredentialModelViewSet
from .base_views import HomeAPIView
from methods.views import BaseMethodModelViewSet, CustomAPIMethodViewSet

urlpatterns = [
    # auth methods
    path('get_credentials/', CredentialModelViewSet.as_view({"post": "create"}), name='get-credentials'),

    # cred info
    re_path(r'^credential/(?P<pk>\d+)/$', CredentialModelViewSet.as_view({"get": "retrieve"}),
            name="credential-detail"),
    path('credential-list/', CredentialModelViewSet.as_view({"get": "list"}), name='credential-list'),

    # Base methods
    path('method/base/detail/<int:pk>/',
         BaseMethodModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'delete'}),
         name='method-base-detail'),
    path('method/base/list/', BaseMethodModelViewSet.as_view({'get': 'list'}), name='method-base-list'),
    path('method/base/create/', BaseMethodModelViewSet.as_view({'post': 'create'}), name='method-base-create'),

    # custom method
    path('method/custom/detail/<int:pk>/',
         CustomAPIMethodViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'delete'}),
         name='method-custom-detail'),
    path('method/custom/list/', CustomAPIMethodViewSet.as_view({'get': 'list'}), name='method-base-list'),
    path('method/custom/create/', CustomAPIMethodViewSet.as_view({'post': 'create'}), name='method-base-create'),

    path('', HomeAPIView.as_view(), name='api'),

]
