# -*- coding: utf8 -*-
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.CreateView.as_view(), name="create"),
    path('update/', views.UpdateView.as_view(), name="update"),
    path('profile/', views.ProfileView.as_view(), name="profile"),
    path('admin/', admin.site.urls),
]
