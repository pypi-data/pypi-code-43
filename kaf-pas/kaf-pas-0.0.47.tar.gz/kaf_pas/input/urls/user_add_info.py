from django.urls import path

from kaf_pas.input.views import user_add_info

urlpatterns = [

    path('User_add_info/Fetch/', user_add_info.User_add_info_Fetch),
    path('User_add_info/Add', user_add_info.User_add_info_Add),
    path('User_add_info/Update', user_add_info.User_add_info_Update),
    path('User_add_info/Remove', user_add_info.User_add_info_Remove),
    path('User_add_info/Lookup/', user_add_info.User_add_info_Lookup),
    path('User_add_info/Info/', user_add_info.User_add_info_Info),

]
