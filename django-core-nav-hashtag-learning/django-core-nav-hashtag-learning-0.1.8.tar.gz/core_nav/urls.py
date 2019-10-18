from core_nav import views
from django.urls import path

app_name = 'core_nav'
urlpatterns = [
        path('settings/', views.SettingsView.as_view(), name='settings'),
        path('about/', views.AboutView.as_view(), name='about'),
        path('school-details/', views.SchoolDetailsView.as_view(), name='school-details'),
        path('get-started/', views.GetStarted.as_view(), name='get-started'),
        path('get-started-invite/', views.GetStarted.as_view(), name='get-started-invite'),
        path('overview-help/', views.OverviewHelp.as_view(), name='overview-help'),
]