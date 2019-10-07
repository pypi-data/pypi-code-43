from django.urls import include, path

urlpatterns = [
    path('admin_tools_stats/', include('admin_tools_stats.urls')),
]
