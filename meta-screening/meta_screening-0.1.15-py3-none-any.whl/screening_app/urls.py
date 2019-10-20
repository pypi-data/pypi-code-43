from django.urls.conf import path
from django.contrib import admin


app_name = "screening_app"

urlpatterns = [
    path("admin/", admin.site.urls),
]
