from django.urls import path
from juntagrico_webdav import views

urlpatterns = [
    path('wd/list/<int:id>/', views.list),
    path('wd/get/<int:id>/', views.get_item)
]
