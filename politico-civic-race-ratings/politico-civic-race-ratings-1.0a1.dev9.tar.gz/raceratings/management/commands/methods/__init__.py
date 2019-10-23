# Imports from race_ratings.
from raceratings.management.commands.methods.bootstrap.home import Home
from raceratings.management.commands.methods.bootstrap.race import Race


class BootstrapContentMethods(Home, Race):
    pass
