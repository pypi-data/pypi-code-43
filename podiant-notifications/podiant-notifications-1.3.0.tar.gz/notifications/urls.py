from .views import NotificationListView, NotificationDetailView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(
        r'^$',
        login_required(NotificationListView.as_view()),
        name='user_notifications'
    ),
    url(
        r'^(?P<pk>\d+)/$',
        login_required(NotificationDetailView.as_view()),
        name='user_notification'
    )
]
