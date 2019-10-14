# -*- coding: utf-8 -*-
"""Main module."""

import datetime
import json

from typing import List, Dict


class Tweet():
    """
    Modelization of the Tweet object that can be retrieved from the Twitter API
    """

    def __init__(self,
                 # Basic attributes
                 created_at=None, id=None, id_str=None, text=None,
                 source=None, truncated=None, in_reply_to_status_id=None,
                 in_reply_to_status_id_str=None, in_reply_to_user_id=None,
                 in_reply_to_screen_name=None, quoted_status_id=None,
                 quoted_status_id_str=None, is_quote_status=None,
                 quoted_status=None, retweeted_status=None, quote_count=None,
                 reply_count=None, retweet_count=None, favorite_count=None,
                 favorited=None, retweeted=None, possibly_sensitive=None,
                 filter_level=None, lang=None, matching_rules=None,
                 current_user_retweet=None, scopes=None,
                 withheld_copyright=None, withheld_in_countries=None,
                 withheld_scope=None, geo=None, full_text=None,
                 display_text_range=None,


                 # User object
                 user__id=None, user__id_str=None, user__name=None,
                 user__screen_name=None, user__location=None, user__url=None,
                 user__description=None, user__derived=None,
                 user__protected=None, user__verified=None,
                 user__followers_count=None, user__friends_count=None,
                 user__listed_count=None, user__favourites_count=None,
                 user__statuses_count=None, user__created_at=None,
                 user__utc_offset=None, user__time_zone=None,
                 user__geo_enabled=None, user__lang=None,
                 user__contributors_enabled=None,
                 user__profile_background_color=None,
                 user__profile_background_image_url=None,
                 user__profile_background_image_url_https=None,
                 user__profile_background_tile=None,
                 user__profile_banner_url=None, user__profile_image_url=None,
                 user__profile_image_url_https=None,
                 user__profile_link_color=None,
                 user__profile_sidebar_border_color=None,
                 user__profile_sidebar_fill_color=None,
                 user__profile_text_color=None,
                 user__profile_use_background_image=None,
                 user__default_profile=None, user__default_profile_image=None,
                 user__withheld_in_countries=None, user__withheld_scope=None,
                 user__is_translator=None, user__following=None,
                 user__notifications=None,
                 user__is_translation_enabled=None,
                 user__has_extended_profile=None,
                 user__translator_type=None,


                 # Coordinates object
                 coordinates__coordinates=None, coordinates__type=None,


                 # Place object
                 place__id=None, place__url=None, place__place_type=None,
                 place__name=None, place__full_name=None,
                 place__country_code=None, place__country=None,
                 place__attributes=None,

                 # Place-Bounding box
                 place__bounding_box__coordinates=None,
                 place__bounding_box__type=None,


                 # Entities object
                 # Entities hashtags
                 entities__hashtags__indices=None,
                 entities__hashtags__text=None,
                 # Entities media
                 entities__media__display_url=None,
                 entities__media__expanded_url=None, entities__media__id=None,
                 entities__media__id_str=None, entities__media__indices=None,
                 entities__media__media_url=None,
                 entities__media__media_url_https=None,
                 entities__media__source_status_id=None,
                 entities__media__source_status_id_str=None,
                 entities__media__type=None, entities__media__url=None,
                 # Entities media sizes
                 entities__media__sizes__thumb__h=None,
                 entities__media__sizes__thumb__resize=None,
                 entities__media__sizes__thumb__w=None,
                 entities__media__sizes__large__h=None,
                 entities__media__sizes__large__resize=None,
                 entities__media__sizes__large__w=None,
                 entities__media__sizes__medium__h=None,
                 entities__media__sizes__medium__resize=None,
                 entities__media__sizes__medium__w=None,
                 entities__media__sizes__small__h=None,
                 entities__media__sizes__small__resize=None,
                 entities__media__sizes__small__w=None,
                 # Entities urls
                 entities__urls__display_url=None,
                 entities__urls__expanded_url=None,
                 entities__urls__indices=None, entities__urls__url=None,
                 # Entities urls unwound
                 entities__urls__unwound__url=None,
                 entities__urls__unwound__status=None,
                 entities__urls__unwound__title=None,
                 entities__urls__unwound__description=None,
                 # Entities user_mentions
                 entities__user_mentions__id=None,
                 entities__user_mentions__id_str=None,
                 entities__user_mentions__indices=None,
                 entities__user_mentions__name=None,
                 entities__user_mentions__screen_name=None,
                 # Entities symbols
                 entities__symbols__indices=None, entities__symbols__text=None,
                 # Entities polls
                 entities__polls__end_datetime=None,
                 entities__polls__duration_minutes=None,
                 # Entities polls options
                 entities__polls__options__position=None,
                 entities__polls__options__text=None,

                 # Extended_entities object
                 # Entities media
                 extended_entities__media__display_url=None,
                 extended_entities__media__expanded_url=None,
                 extended_entities__media__id=None,
                 extended_entities__media__id_str=None,
                 extended_entities__media__indices=None,
                 extended_entities__media__media_url=None,
                 extended_entities__media__media_url_https=None,
                 extended_entities__media__source_status_id=None,
                 extended_entities__media__source_status_id_str=None,
                 extended_entities__media__type=None,
                 extended_entities__media__url=None,
                 extended_entities__media__sizes__thumb__h=None,
                 extended_entities__media__sizes__thumb__resize=None,
                 extended_entities__media__sizes__thumb__w=None,
                 extended_entities__media__sizes__large__h=None,
                 extended_entities__media__sizes__large__resize=None,
                 extended_entities__media__sizes__large__w=None,
                 extended_entities__media__sizes__medium__h=None,
                 extended_entities__media__sizes__medium__resize=None,
                 extended_entities__media__sizes__medium__w=None,
                 extended_entities__media__sizes__small__h=None,
                 extended_entities__media__sizes__small__resize=None,
                 extended_entities__media__sizes__small__w=None,


                 # Metadata object
                 metadata__result_type=None,
                 metadata__iso_language_code=None,

                 # Additional fields (not from the Tweeter model)
                 polarity=None,
                 trtext=None,

                 # Ignore possible additional arguments
                 **kwargs
                 ):

        # Basic attributes
        try:
            self.created_at =\
                datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except Exception:
            self.created_at = created_at

        try:
            self.id = int(id)
        except Exception:
            self.id = id

        if type(truncated) is str:
            if truncated == "True":
                self.truncated = True
            elif truncated == "False":
                self.truncated = False
        else:
            self.truncated = truncated

        try:
            self.in_reply_to_status_id = int(in_reply_to_status_id)
        except Exception:
            self.in_reply_to_status_id = in_reply_to_status_id

        try:
            self.in_reply_to_user_id = int(in_reply_to_user_id)
        except Exception:
            self.in_reply_to_user_id = in_reply_to_user_id

        try:
            self.quoted_status_id = int(quoted_status_id)
        except Exception:
            self.quoted_status_id = quoted_status_id

        if type(is_quote_status) is str:
            if is_quote_status == "True":
                self.is_quote_status = True
            elif is_quote_status == "False":
                self.is_quote_status = False
        else:
            self.is_quote_status = is_quote_status
        try:
            self.retweet_count = int(retweet_count)
        except Exception:
            self.retweet_count = retweet_count

        try:
            self.favorite_count = int(favorite_count)
        except Exception:
            self.favorite_count = favorite_count

        self.text = text
        if full_text is not None:
            self.text = full_text
        self.source = source
        self.in_reply_to_screen_name = in_reply_to_screen_name

        self.id_str = id_str
        self.in_reply_to_status_id_str = in_reply_to_status_id_str
        self.quoted_status_id_str = quoted_status_id_str
        self.quoted_status = quoted_status
        self.retweeted_status = retweeted_status
        self.quote_count = quote_count
        self.reply_count = reply_count
        self.favorited = favorited
        self.retweeted = retweeted
        self.possibly_sensitive = possibly_sensitive
        self.filter_level = filter_level
        self.lang = lang
        self.matching_rules = matching_rules
        self.current_user_retweet = current_user_retweet
        self.scopes = scopes
        self.withheld_copyright = withheld_copyright
        self.withheld_in_countries = withheld_in_countries
        self.withheld_scope = withheld_scope
        self.geo = geo
        self.display_text_range = display_text_range

        # User object
        self.user = {}

        try:
            self.user["id"] = int(user__id)
        except Exception:
            self.user["id"] = user__id

        try:
            self.user["created_at"] = datetime.datetime.strptime(
                user__created_at, "%Y-%m-%d %H:%M:%S")
        except Exception:
            self.user["created_at"] = user__created_at

        if type(user__verified) is str:
            if user__verified == "True":
                self.user["verified"] = True
            elif user__verified == "False":
                self.user["verified"] = False
        else:
            self.user["verified"] = user__verified

        try:
            self.user["followers_count"] = int(user__followers_count)
        except Exception:
            self.user["followers_count"] = user__followers_count

        try:
            self.user["friends_count"] = int(user__friends_count)
        except Exception:
            self.user["friends_count"] = user__friends_count

        try:
            self.user["listed_count"] = int(user__listed_count)
        except Exception:
            self.user["listed_count"] = user__listed_count

        try:
            self.user["favourites_count"] = int(user__favourites_count)
        except Exception:
            self.user["favourites_count"] = user__favourites_count

        try:
            self.user["statuses_count"] = int(user__statuses_count)
        except Exception:
            self.user["statuses_count"] = user__statuses_count

        if type(user__geo_enabled) is str:
            if user__geo_enabled == "True":
                self.user["geo_enabled"] = True
            elif user__geo_enabled == "False":
                self.user["geo_enabled"] = False
        else:
            self.user["geo_enabled"] = user__geo_enabled

        self.user["name"] = user__name
        self.user["screen_name"] = user__screen_name
        self.user["location"] = user__location
        self.user["profile_image_url"] = user__profile_image_url
        self.user["lang"] = user__lang

        self.user["id_str"] = user__id_str
        self.user["url"] = user__url
        self.user["description"] = user__description
        self.user["derived"] = user__derived
        self.user["protected"] = user__protected
        self.user["utc_offset"] = user__utc_offset
        self.user["time_zone"] = user__time_zone
        self.user["contributors_enabled"] = user__contributors_enabled
        self.user["profile_background_color"] = user__profile_background_color
        self.user["profile_background_image_url"] =\
            user__profile_background_image_url
        self.user["profile_background_image_url_https"] =\
            user__profile_background_image_url_https
        self.user["profile_background_tile"] = user__profile_background_tile
        self.user["profile_banner_url"] = user__profile_banner_url
        self.user["profile_image_url_https"] = user__profile_image_url_https
        self.user["profile_link_color"] = user__profile_link_color
        self.user["profile_sidebar_border_color"] =\
            user__profile_sidebar_border_color
        self.user["profile_sidebar_fill_color"] =\
            user__profile_sidebar_fill_color
        self.user["profile_text_color"] = user__profile_text_color
        self.user["profile_use_background_image"] =\
            user__profile_use_background_image
        self.user["default_profile"] = user__default_profile
        self.user["default_profile_image"] = user__default_profile_image
        self.user["withheld_in_countries"] = user__withheld_in_countries
        self.user["withheld_scope"] = user__withheld_scope
        self.user["is_translator"] = user__is_translator
        self.user["following"] = user__following
        self.user["notifications"] = user__notifications

        if type(user__is_translation_enabled) is str:
            if user__is_translation_enabled == "True":
                self.user["is_translation_enabled"] = True
            elif user__is_translation_enabled == "False":
                self.user["is_translation_enabled"] = False
        else:
            self.user["is_translation_enabled"] =\
                user__is_translation_enabled

        if type(user__has_extended_profile) is str:
            if user__has_extended_profile == "True":
                self.user["has_extended_profile"] = True
            elif user__has_extended_profile == "False":
                self.user["has_extended_profile"] = False
        else:
            self.user["has_extended_profile"] =\
                user__has_extended_profile

        self.user["translator_type"] = user__translator_type

        # Coordinates object
        self.coordinates = {}
        self.coordinates["type"] = coordinates__type
        try:
            self.coordinates["coordinates"] =\
                [float(coords)
                    for coords in json.loads(coordinates__coordinates)]
        except Exception:
            self.coordinates["coordinates"] = coordinates__coordinates

        # Place object
        self.place = {}
        self.place["id"] = place__id
        self.place["name"] = place__name
        self.place["full_name"] = place__full_name
        self.place["country"] = place__country
        self.place["country_code"] = place__country_code
        self.place["place_type"] = place__place_type
        self.place["url"] = place__url
        self.place["attributes"] = place__attributes
        # Place-Bounding box
        self.place["bounding_box"] = {}
        try:
            coords = json.loads(place__bounding_box__coordinates)
            self.place["bounding_box"]["coordinates"] =\
                [[[float(coords[x][y][z])
                    for z in range(len(coords[x][y]))]
                    for y in range(len(coords[x]))]
                    for x in range(len(coords))]

        except Exception:
            self.place["bounding_box"]["coordinates"] =\
                place__bounding_box__coordinates
        self.place["bounding_box"]["type"] = place__bounding_box__type

        # Entities object
        self.entities = {}
        # Entities hashtags
        self.entities["hashtags"] = {}
        try:
            self.entities["hashtags"]["text"] =\
                json.loads(entities__hashtags__text)
        except Exception:
            self.entities["hashtags"]["text"] = entities__hashtags__text

        self.entities["hashtags"]["indices"] = entities__hashtags__indices
        # Entities media
        self.entities["media"] = {}
        try:
            self.entities["media"]["media_url"] =\
                json.loads(entities__media__media_url)
        except Exception:
            self.entities["media"]["media_url"] = entities__media__media_url
        self.entities["media"]["display_url"] = entities__media__display_url
        self.entities["media"]["expanded_url"] = entities__media__expanded_url
        self.entities["media"]["id"] = entities__media__id
        self.entities["media"]["id_str"] = entities__media__id_str
        self.entities["media"]["indices"] = entities__media__indices
        self.entities["media"]["media_url_https"] =\
            entities__media__media_url_https
        self.entities["media"]["source_status_id"] =\
            entities__media__source_status_id
        self.entities["media"]["source_status_id_str"] =\
            entities__media__source_status_id_str
        self.entities["media"]["type"] = entities__media__type
        self.entities["media"]["url"] = entities__media__url
        # Entities media sizes
        self.entities["media"]["sizes"] = {}
        self.entities["media"]["sizes"]["thumb"] = {}
        self.entities["media"]["sizes"]["large"] = {}
        self.entities["media"]["sizes"]["medium"] = {}
        self.entities["media"]["sizes"]["small"] = {}
        self.entities["media"]["sizes"]["thumb"]["h"] =\
            entities__media__sizes__thumb__h
        self.entities["media"]["sizes"]["thumb"]["resize"] =\
            entities__media__sizes__thumb__resize
        self.entities["media"]["sizes"]["thumb"]["w"] =\
            entities__media__sizes__thumb__w
        self.entities["media"]["sizes"]["large"]["h"] =\
            entities__media__sizes__large__h
        self.entities["media"]["sizes"]["large"]["resize"] =\
            entities__media__sizes__large__resize
        self.entities["media"]["sizes"]["large"]["w"] =\
            entities__media__sizes__large__w
        self.entities["media"]["sizes"]["medium"]["h"] =\
            entities__media__sizes__medium__h
        self.entities["media"]["sizes"]["medium"]["resize"] =\
            entities__media__sizes__medium__resize
        self.entities["media"]["sizes"]["medium"]["w"] =\
            entities__media__sizes__medium__w
        self.entities["media"]["sizes"]["small"]["h"] =\
            entities__media__sizes__small__h
        self.entities["media"]["sizes"]["small"]["resize"] =\
            entities__media__sizes__small__resize
        self.entities["media"]["sizes"]["small"]["w"] =\
            entities__media__sizes__small__w
        # Entities urls
        self.entities["urls"] = {}
        try:
            self.entities["urls"]["expanded_url"] =\
                json.loads(entities__urls__expanded_url)
        except Exception:
            self.entities["urls"]["expanded_url"] =\
                entities__urls__expanded_url
        self.entities["urls"]["display_url"] = entities__urls__display_url
        self.entities["urls"]["indices"] = entities__urls__indices
        self.entities["urls"]["url"] = entities__urls__url
        # Entities urls unwound
        self.entities["urls"]["unwound"] = {}
        self.entities["urls"]["unwound"]["url"] = entities__urls__unwound__url
        self.entities["urls"]["unwound"]["status"] =\
            entities__urls__unwound__status
        self.entities["urls"]["unwound"]["title"] =\
            entities__urls__unwound__title
        self.entities["urls"]["unwound"]["description"] =\
            entities__urls__unwound__description
        # Entities user_mentions
        self.entities["user_mentions"] = {}
        try:
            self.entities["user_mentions"]["screen_name"] =\
                json.loads(entities__user_mentions__screen_name)
        except Exception:
            self.entities["user_mentions"]["screen_name"] =\
                entities__user_mentions__screen_name
        self.entities["user_mentions"]["id"] = entities__user_mentions__id
        self.entities["user_mentions"]["id_str"] =\
            entities__user_mentions__id_str
        self.entities["user_mentions"]["indices"] =\
            entities__user_mentions__indices
        self.entities["user_mentions"]["name"] = entities__user_mentions__name
        # Entities symbols
        self.entities["symbols"] = {}
        self.entities["symbols"]["indices"] = entities__symbols__indices
        self.entities["symbols"]["text"] = entities__symbols__text
        # Entities polls
        self.entities["polls"] = {}
        self.entities["polls"]["end_datetime"] = entities__polls__end_datetime
        self.entities["polls"]["duration_minutes"] =\
            entities__polls__duration_minutes
        # Entities polls options
        self.entities["polls"]["options"] = {}
        self.entities["polls"]["options"]["position"] =\
            entities__polls__options__position
        self.entities["polls"]["options"]["text"] =\
            entities__polls__options__text

        # Extended_entities object
        # Entities media
        self.extended_entities = {}
        self.extended_entities["media"] = {}
        self.extended_entities["media"]["id"] = extended_entities__media__id
        self.extended_entities["media"]["display_url"] =\
            extended_entities__media__display_url
        self.extended_entities["media"]["expanded_url"] =\
            extended_entities__media__expanded_url
        self.extended_entities["media"]["id_str"] =\
            extended_entities__media__id_str
        self.extended_entities["media"]["indices"] =\
            extended_entities__media__indices
        self.extended_entities["media"]["media_url"] =\
            extended_entities__media__media_url
        self.extended_entities["media"]["media_url_https"] =\
            extended_entities__media__media_url_https
        self.extended_entities["media"]["source_status_id"] =\
            extended_entities__media__source_status_id
        self.extended_entities["media"]["source_status_id_str"] =\
            extended_entities__media__source_status_id_str
        self.extended_entities["media"]["type"] =\
            extended_entities__media__type
        self.extended_entities["media"]["url"] = extended_entities__media__url
        self.extended_entities["media"]["sizes"] = {}
        self.extended_entities["media"]["sizes"]["thumb"] = {}
        self.extended_entities["media"]["sizes"]["large"] = {}
        self.extended_entities["media"]["sizes"]["medium"] = {}
        self.extended_entities["media"]["sizes"]["small"] = {}
        self.extended_entities["media"]["sizes"]["thumb"]["h"] =\
            extended_entities__media__sizes__thumb__h
        self.extended_entities["media"]["sizes"]["thumb"]["resize"] =\
            extended_entities__media__sizes__thumb__resize
        self.extended_entities["media"]["sizes"]["thumb"]["w"] =\
            extended_entities__media__sizes__thumb__w
        self.extended_entities["media"]["sizes"]["large"]["h"] =\
            extended_entities__media__sizes__large__h
        self.extended_entities["media"]["sizes"]["large"]["resize"] =\
            extended_entities__media__sizes__large__resize
        self.extended_entities["media"]["sizes"]["large"]["w"] =\
            extended_entities__media__sizes__large__w
        self.extended_entities["media"]["sizes"]["medium"]["h"] =\
            extended_entities__media__sizes__medium__h
        self.extended_entities["media"]["sizes"]["medium"]["resize"] =\
            extended_entities__media__sizes__medium__resize
        self.extended_entities["media"]["sizes"]["medium"]["w"] =\
            extended_entities__media__sizes__medium__w
        self.extended_entities["media"]["sizes"]["small"]["h"] =\
            extended_entities__media__sizes__small__h
        self.extended_entities["media"]["sizes"]["small"]["resize"] =\
            extended_entities__media__sizes__small__resize
        self.extended_entities["media"]["sizes"]["small"]["w"] =\
            extended_entities__media__sizes__small__w

        # Metadata object
        self.metadata = {}
        self.metadata["result_type"] = metadata__result_type
        self.metadata["iso_language_code"] = metadata__iso_language_code

        # Additional fields
        self.polarity = polarity
        self.trtext = trtext

    # Setter methods
    def set_polarity(self, polarity):
        self.polarity = polarity

    def set_trtext(self, trtext):
        self.trtext = trtext

    def get_tweet_fields_subset(self, fields: List[str]) -> Dict:
        """
        Keep just the specified fields and return a dict
        with just the information specified. Works just with non-nested fields
        (nested ones can only be specified as a whole)
        """

        tweet_subset = {}
        for field in fields:
            try:
                tweet_subset[field] = self[field]
            except AttributeError:
                pass
        return tweet_subset

    def as_short_json(self, dictionary: Dict = None) -> Dict:
        """
        Return the Tweet object in a short JSON-like representation
        but without all the null key-value pairs
        """

        if dictionary is None:
            json_tweet = {}
            for key, value in self.__dict__.items():
                if type(value) is dict:
                    nested_dict = self.as_short_json(value)
                    if nested_dict is not None:
                        json_tweet[key] = nested_dict
                elif value is not None:
                    json_tweet[key] = value
            return json_tweet

        else:
            dictie = {}
            for key, value in dictionary.items():
                if type(value) is dict:
                    nested_dict = self.as_short_json(value)
                    if nested_dict is not None:
                        dictie[key] = nested_dict
                elif value is not None:
                    dictie[key] = value
            if len(dictie) == 0:
                return None
            else:
                return dictie

    def as_long_json(self) -> Dict:
        """
        Return the Tweet object in a JSON-like representation (nested dicts).
        Just the __dict__ of the class
        """

        return self.__dict__

    def __getitem__(self, key):
        return getattr(self, key)
