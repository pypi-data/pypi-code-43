# Imports from python.
from itertools import chain, groupby


# Imports from other dependencies.
from election.models import Race
from geography.models import Division
from geography.models import DivisionLevel
from government.models import Body
from rest_framework.response import Response
from rest_framework.views import APIView


# Imports from race_ratings.
from raceratings.models import Category
from raceratings.serializers import BodyRatingSerializer
from raceratings.serializers import CategorySerializer
from raceratings.serializers import DistrictSerializer
from raceratings.serializers import RaceAPISerializer
from raceratings.serializers import RaceRatingFeedSerializer
from raceratings.serializers import StateSerializer


class BodyRatingsViewSet(APIView):
    def get(self, request, format=None):
        data = []
        bodies = Body.objects.all()

        for body in bodies:
            latest_rating = body.ratings.latest("created")
            data.append(BodyRatingSerializer(latest_rating).data)

        return Response(data)


class RaceRatingsAPIViewSet(APIView):
    def get(self, request, format=None):
        races = Race.objects.filter(
            cycle__slug="2020", special=False
        ).order_by("office__division__label")

        race_data = RaceAPISerializer(races, many=True).data

        return Response(race_data)


class RaceRatingsFeedViewSet(APIView):
    def get(self, request, format=None):
        races = Race.objects.filter(
            cycle__slug="2020", special=False
        ).order_by("office__division__label")

        races = races

        ratings = [race.ratings.order_by("created")[1:] for race in races]
        ratings = list(chain(*ratings))
        ratings = sorted(ratings, key=lambda r: r.created)
        grouped = {}
        for key, group in groupby(ratings, lambda r: r.created):
            date = key.strftime("%Y-%m-%d")

            grouped[date] = [
                RaceRatingFeedSerializer(rating).data for rating in list(group)
            ]

        return Response(grouped)


class RaceRatingsFilterViewSet(APIView):
    def get(self, request, format=None):
        categories = Category.objects.all()
        states = Division.objects.filter(level__name=DivisionLevel.STATE)
        districts = Division.objects.filter(level__name=DivisionLevel.DISTRICT)

        categories_data = CategorySerializer(categories, many=True).data
        states_data = StateSerializer(states, many=True).data
        districts_data = DistrictSerializer(districts, many=True).data

        data = {
            "categories": categories_data,
            "states": states_data,
            "districts": districts_data,
        }

        return Response(data)
