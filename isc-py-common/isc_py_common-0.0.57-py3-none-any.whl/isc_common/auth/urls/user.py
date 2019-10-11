from django.urls import path
from isc_common.auth.views.user import User_Fetch, User_Add, User_Update, User_Remove, User_Info, User_Lookup

urlpatterns = [

    path('User/Fetch/', User_Fetch),
    path('User/Add', User_Add),
    path('User/Update', User_Update),
    path('User/Remove', User_Remove),
    path('User/Lookup/', User_Lookup),
    path('User/Info/', User_Info),

]
