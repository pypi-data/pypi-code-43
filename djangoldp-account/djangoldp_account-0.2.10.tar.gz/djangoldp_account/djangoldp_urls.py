"""djangoldp project URL Configuration"""

from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt

from django_registration.backends.activation.views import RegistrationView
from djangoldp.permissions import LDPPermissions
from djangoldp.views import LDPViewSet
from djangoldp_account.forms import LDPUserForm
from .models import ChatProfile, Account
from .views import userinfocustom, RPLoginView, RPLoginCallBackView, check_user

Group._meta.serializer_fields = ['name']
Group._meta.anonymous_perms = getattr(settings, 'GROUP_ANONYMOUS_PERMISSIONS', ['view'])
Group._meta.authenticated_perms = getattr(settings, 'GROUP_AUTHENTICATED_PERMISSIONS', ['inherit'])
Group._meta.owner_perms = getattr(settings, 'GROUP_OWNER_PERMISSIONS', ['inherit'])

urlpatterns = [
    url(r'^groups/',
        LDPViewSet.urls(model=Group, fields=['@id', 'name', 'user_set'],
                        permission_classes=getattr(settings, 'GROUP_PERMISSION_CLASSES', [LDPPermissions]),
        )
    ),
    url(r'^auth/register/$',
        RegistrationView.as_view(
            form_class=LDPUserForm
        ),
        name='django_registration_register',
    ),
    url(r'^auth/', include('django_registration.backends.activation.urls')),
    url(r'^auth/', include('django.contrib.auth.urls')),
    url(r'^accounts/', LDPViewSet.urls(model=Account, permission_classes=[LDPPermissions])),
    url(r'^chat-profile/', LDPViewSet.urls(model=ChatProfile, permission_classes=[LDPPermissions])),
    url(r'^oidc/login/callback/?$', RPLoginCallBackView.as_view(), name='oidc_login_callback'),
    url(r'^oidc/login/?$', RPLoginView.as_view(), name='oidc_login'),
    url(r'^userinfo/?$', csrf_exempt(userinfocustom)),
    url(r'^check-user/?$', csrf_exempt(check_user)),
    url(r'^', include('oidc_provider.urls', namespace='oidc_provider'))
]
