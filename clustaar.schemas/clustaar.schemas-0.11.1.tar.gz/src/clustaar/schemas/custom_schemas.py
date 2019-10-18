from lupin import Schema, bind


class MatchIntentConditionSchema(Schema):
    """We need a custom schema for the MatchIntentCondition because the JSON structure
    does not reflect the one in our models.
    """

    def load(self, cls, data, mapper, allow_partial=False, factory=bind):
        """Loads an instance of cls from dictionary

        Args:
            cls (class): class to instantiate
            data (dict): dictionary of data
            mapper (Mapper): mapper used to load data
            allow_partial (bool): allow partial schema, won't raise error if missing keys
            factory (callable): factory method used to instantiate objects
        Returns:
            object
        """
        return cls(intent_id=data["intent"]["id"])


class CustomerSatisfactionChoiceSchema(Schema):
    """We need a custom schema for the CustomerSatisfactionChoice because the JSON structure
    does not reflect the one in our models.
    """

    def load(self, cls, data, mapper, allow_partial=False, factory=bind):
        """Loads an instance of cls from dictionary

        Args:
            cls (class): class to instantiate
            data (dict): dictionary of data
            mapper (Mapper): mapper used to load data
            allow_partial (bool): allow partial schema, won't raise error if missing keys
            factory (callable): factory method used to instantiate objects
        Returns:
            object
        """
        matching_intent_data = data.get("matchingIntent")
        if matching_intent_data and matching_intent_data.get("id"):
            data["matching_intent_id"] = data["matchingIntent"]["id"]

        return super().load(cls, data, mapper, allow_partial, factory)
