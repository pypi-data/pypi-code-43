from django.urls import path

from isc_common.auth.views import user

urlpatterns = [

    path('User/Fetch/', user.User_Fetch),
    path('User/FetchExclBots/', user.User_FetchExclBots),
    path('User/Add', user.User_Add),
    path('User/Update', user.User_Update),
    path('User/Remove', user.User_Remove),
    path('User/Lookup/', user.User_Lookup),
    path('User/Info/', user.User_Info),

]
