from django.urls import path

from . import views

app_name = "cas"

urlpatterns = [
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("user/language", views.language, name="language"),
    path("environment", views.enviroment, name="environment"),
    path("user/profile", views.profile, name="profile"),
    path("user/settings", views.userSettings, name="settings"),
    path("file/upload", views.upload, name="upload"),
]
