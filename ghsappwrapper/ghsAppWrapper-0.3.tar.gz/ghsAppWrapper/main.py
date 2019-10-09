import requests


def GET_SECTION(section_name):
    """Make response to database and clean it

    Arguments:
        section_name {string} -- name of the section to select from locations dict

    Returns:
        object -- response from request to section
    """

    locations = {
        "calendarEvents": "/calendar/tday-events",
        "fieldInfo": "/field-information",
        "scores": "/scores",
        "footballFieldInfo": "/field-information/field-status/football-field",
        "gymInfo": "/field-information/field-status/gym",
        "softballFieldInfo": "/field-information/field-status/softball-field"
    }

    full_url = "https://ghs-app-5a0ba.firebaseio.com" + \
        locations[section_name] + ".json"
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(full_url, headers=headers)
    json_response = response.json()
    if json_response == None:
        return {}
    else:
        return json_response


class ghsApp():

    #############################################################################
    #############################################################################

    def calendarEvents(self):
        """Gets a list of all the events that the app collects from the school calendar.
        We don't collect events that have to do with the following:
        1. Middle school events
        2. Practices
        3. Scrimmages
        4. Sports that isn't one of the following:
            1. Soccer
            2. Football
            3. Baseball
            4. Softball
            5. Field Hockey
            6. Volleyball
            7. Basketball
            8. Lacrosse
        If response comes back as {} then there are no events for today

        Returns:
            dict -- response from calendar events
        """
        return GET_SECTION("calendarEvents")

    #############################################################################
    #############################################################################

    def fieldInfo(self):
        """Get the information for all the homefields supported
        The home fields that are supported are:
        1. Football Field
        2. Gym
        3. Softball Field

        For each field there is the following information:
        1. Current sport on that field (or last sport if vision program is off)
        2. Current away team name (or last away team name if vision program is off)
        3. Start time for current game (or last game if vision program is off)
        4. If the current game is varsity or jv (last game if vision program is off)
        5. Current home game score and away game score (last game scores if the vision program is off)

        Returns:
            dict -- response from field-information section
        """
        return GET_SECTION("fieldInfo")

    #############################################################################
    #############################################################################

    def footballFieldInfo(self):
        """Field information just for the football field

        Returns:
            dict -- response from field-information/football-field section
        """
        return GET_SECTION("footballFieldInfo")

    #############################################################################
    #############################################################################

    def gymInfo(self):
        """Field information just for the gym

        Returns:
            dict -- response from field-information/gym section
        """
        return GET_SECTION("gymInfo")

    #############################################################################
    #############################################################################

    def softballFieldInfo(self):
        """Field information just for the softball field

        Returns:
            dict -- response from field-information/softball-field section
        """
        return GET_SECTION("softballFieldInfo")
