# Imports from other dependencies.
from election.models import Race
from rest_framework import generics


# Imports from race_ratings.
from raceratings.serializers import RaceListSerializer
from raceratings.serializers import RaceSerializer


class RaceMixin(object):
    def get_queryset(self):
        return Race.objects.filter(cycle__slug="2018")


class RaceList(RaceMixin, generics.ListAPIView):
    serializer_class = RaceListSerializer


class RaceViewSet(RaceMixin, generics.RetrieveAPIView):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer
