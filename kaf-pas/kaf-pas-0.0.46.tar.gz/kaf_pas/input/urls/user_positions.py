from django.urls import path

from kaf_pas.input.views import user_positions

urlpatterns = [

    path('User_positions/Fetch/', user_positions.User_positions_Fetch),
    path('User_positions/Add', user_positions.User_positions_Add),
    path('User_positions/Update', user_positions.User_positions_Update),
    path('User_positions/Remove', user_positions.User_positions_Remove),
    path('User_positions/Lookup/', user_positions.User_positions_Lookup),
    path('User_positions/Info/', user_positions.User_positions_Info),

]
