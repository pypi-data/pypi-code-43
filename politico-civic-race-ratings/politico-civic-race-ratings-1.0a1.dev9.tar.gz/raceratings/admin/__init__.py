# Imports from Django.
from django.contrib import admin


# Imports from other dependencies.
from election.models import Race


# Imports from race_ratings.
from raceratings.admin.page_content import PageContentAdmin
from raceratings.admin.race_rating import RaceRatingAdmin
from raceratings.models import Author
from raceratings.models import BodyRating
from raceratings.models import Category
from raceratings.models import DataProfile
from raceratings.models import RaceRating
from raceratings.models import RatingPageContent


admin.site.register(Author)
admin.site.register(BodyRating)
admin.site.register(Category)
admin.site.register(DataProfile)
admin.site.register(RatingPageContent, PageContentAdmin)
admin.site.register(RaceRating, RaceRatingAdmin)
