from django.urls import path

from kaf_pas.common.views import calendarGraph

urlpatterns = [

    path('CalendarGraph/Fetch/', calendarGraph.CalendarGraph_Fetch),

]
