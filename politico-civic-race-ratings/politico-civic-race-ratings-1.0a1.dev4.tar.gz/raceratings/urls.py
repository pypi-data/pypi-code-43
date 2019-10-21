# Imports from Django.
from django.urls import path
from django.urls import re_path


# Imports from race_ratings.
from raceratings.views import Home
from raceratings.views import RacePage
from raceratings.views import RatingsEditor
from raceratings.viewsets import BodyRatingsViewSet
from raceratings.viewsets import RaceRatingsAPIViewSet
from raceratings.viewsets import RaceRatingsFilterViewSet
from raceratings.viewsets import RaceRatingsFeedViewSet
from raceratings.viewsets import RatingAdminView


urlpatterns = [
    path(Home.path, Home.as_view(), name=Home.name),
    re_path(RacePage.path, RacePage.as_view(), name=RacePage.name),
    path("editor/", RatingsEditor.as_view(), name="raceratings-editor"),
    re_path(
        r"^api/ratings/$",
        RaceRatingsAPIViewSet.as_view(),
        name="raceratings_api_ratings-api",
    ),
    re_path(
        r"^api/filters/$",
        RaceRatingsFilterViewSet.as_view(),
        name="raceratings_api_filters-api",
    ),
    re_path(
        r"^api/feed/$",
        RaceRatingsFeedViewSet.as_view(),
        name="raceratings_api_feed-api",
    ),
    re_path(
        r"^api/body-ratings/$",
        BodyRatingsViewSet.as_view(),
        name="raceratings_api_body-ratings-api",
    ),
    re_path(
        r"^api/admin/ratings/$",
        RatingAdminView.as_view(),
        name="raceratings_api_ratings-admin",
    ),
]
