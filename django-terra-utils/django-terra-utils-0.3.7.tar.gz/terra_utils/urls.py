from django.urls import path

from terra_utils.views import SettingsView

app_name = 'terra_utils'

urlpatterns = [
    path('settings/', SettingsView.as_view(), name='settings'),
]
