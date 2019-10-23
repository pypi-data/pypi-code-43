from django.db.models import Prefetch

# Imports from other dependencies.
from election.models import Race
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


# Imports from race_ratings.
from raceratings.models import Author
from raceratings.models import Category
from raceratings.models import RaceRating
from raceratings.serializers import RaceAdminSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass


class RatingAdminView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        races = (
            Race.objects.filter(cycle__slug="2020")
            .prefetch_related(
                Prefetch(
                    "ratings",
                    queryset=RaceRating.objects.select_related(
                        "race", "category"
                    ).order_by("created", "pk"),
                )
            )
            .select_related(
                "office",
                "office__body",
                "office__division",
                "office__division__level",
                "office__division__parent",
                "division",
                "division__level",
                "division__parent",
            )
            .order_by("office__division__label")
        )

        race_data = RaceAdminSerializer(races, many=True).data

        return Response(race_data)

    def post(self, request, *args, **kwargs):
        try:
            credited_author = Author.objects.exclude(user_id__isnull=True).get(
                user_id=request.user.id
            )
        except Author.DoesNotExist:
            # credited_author = Author.objects.get(
            #     first_name="Steve",
            #     last_name="Shepard"
            # )

            if not request.user.is_anonymous():
                author_params = dict(
                    first_name=request.user.first_name,
                    last_name=request.user.last_name,
                )
            else:
                author_params = dict(first_name="Unknown", last_name="Staffer")

            credited_author = Author.objects.get_or_create(**author_params)

        for uid, ratings in request.data.items():
            race = Race.objects.get(uid=uid)
            last_rating = race.ratings.latest("created")

            for pk, data in ratings.items():
                category = None
                expl = None

                if data.get("category"):
                    category = Category.objects.get(
                        short_label=data["category"]
                    )

                if data.get("explanation"):
                    expl = data["explanation"]

                if data["post_type"] == "create":
                    # can't have a new rating without a category
                    if not category:
                        continue

                    # if a new rating came through with the same rating,
                    # ignore it
                    if category == last_rating.category:
                        continue

                    race_rating_dict = dict(
                        race_id=race.pk,
                        author_id=credited_author.pk,
                        category_id=category.pk,
                        explanation=expl,
                    )

                    new_rating = RaceRating.objects.create(**race_rating_dict)
                elif data["post_type"] == "update":
                    rating = RaceRating.objects.get(pk=pk)

                    rating.category = category if category else rating.category
                    rating.explanation = expl if expl else rating.explanation

                    rating.save()

        return Response("created ratings", status=status.HTTP_201_CREATED)
