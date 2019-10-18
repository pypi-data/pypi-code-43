from django.urls import path

from kaf_pas.input.views import user_view

urlpatterns = [

    path('User_view/Fetch/', user_view.User_view_Fetch),
    path('User_view/Add', user_view.User_view_Add),
    path('User_view/Update', user_view.User_view_Update),
    path('User_view/Remove', user_view.User_view_Remove),
    path('User_view/Lookup/', user_view.User_view_Lookup),
    path('User_view/Info/', user_view.User_view_Info),

]
