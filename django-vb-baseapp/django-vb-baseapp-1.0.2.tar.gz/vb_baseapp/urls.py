from django.urls import path

from .views import IndexView

app_name = 'vb_baseapp'

urlpatterns = [path('', view=IndexView.as_view(), name='index')]
