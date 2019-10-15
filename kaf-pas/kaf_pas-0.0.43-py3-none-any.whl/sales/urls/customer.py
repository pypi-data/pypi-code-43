from django.urls import path

from kaf_pas.sales.views import customer

urlpatterns = [

    path('Customer/Fetch/', customer.Customer_Fetch),
    path('Customer/Add', customer.Customer_Add),
    path('Customer/Update', customer.Customer_Update),
    path('Customer/Remove', customer.Customer_Remove),
    path('Customer/Lookup/', customer.Customer_Lookup),
    path('Customer/Info/', customer.Customer_Info),

]
