from django.urls import path

from juntagrico_pg import views

urlpatterns = [
    path('jpg/home', views.home),
    path('jpg/sql', views.execute_sql)
]
