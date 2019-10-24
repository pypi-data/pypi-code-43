from django.contrib import admin
from django.urls import path

app_name = "reference_app"

urlpatterns = [
    path("admin/", admin.site.urls),
]
