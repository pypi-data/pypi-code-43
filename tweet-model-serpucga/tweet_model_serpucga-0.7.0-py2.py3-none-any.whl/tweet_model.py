# -*- coding: utf-8 -*-
"""Main module."""

import logging
from typing import Union, Dict, List, Generator

from tweet_manager.lib import format_csv

# Configure logger
LOG_FORMAT = '[%(asctime)-15s] %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger("logger")


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
                 withheld_scope=None, geo=None,


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
                 extended_entities__media__url=None):

        # Basic attributes
        self.created_at = created_at
        self.id = id
        self.id_str = id_str
        self.text = text
        self.source = source
        self.truncated = truncated
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_status_id_str = in_reply_to_status_id_str
        self.in_reply_to_user_id = in_reply_to_user_id
        self.in_reply_to_screen_name = in_reply_to_screen_name
        self.quoted_status_id = quoted_status_id
        self.quoted_status_id_str = quoted_status_id_str
        self.is_quote_status = is_quote_status
        self.quoted_status = quoted_status
        self.retweeted_status = retweeted_status
        self.quote_count = quote_count
        self.reply_count = reply_count
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
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

        # User object
        self.user = {}
        self.user["id"] = user__id
        self.user["id_str"] = user__id_str
        self.user["name"] = user__name
        self.user["screen_name"] = user__screen_name
        self.user["location"] = user__location
        self.user["url"] = user__url
        self.user["description"] = user__description
        self.user["derived"] = user__derived
        self.user["protected"] = user__protected
        self.user["verified"] = user__verified
        self.user["followers_count"] = user__followers_count
        self.user["friends_count"] = user__friends_count
        self.user["listed_count"] = user__listed_count
        self.user["favourites_count"] = user__favourites_count
        self.user["statuses_count"] = user__statuses_count
        self.user["created_at"] = user__created_at
        self.user["utc_offset"] = user__utc_offset
        self.user["time_zone"] = user__time_zone
        self.user["geo_enabled"] = user__geo_enabled
        self.user["lang"] = user__lang
        self.user["contributors_enabled"] = user__contributors_enabled
        self.user["profile_background_color"] = user__profile_background_color
        self.user["profile_background_image_url"] =\
            user__profile_background_image_url
        self.user["profile_background_image_url_https"] =\
            user__profile_background_image_url_https
        self.user["profile_background_tile"] = user__profile_background_tile
        self.user["profile_banner_url"] = user__profile_banner_url
        self.user["profile_image_url"] = user__profile_image_url
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

        # Coordinates object
        self.coordinates = {}
        self.coordinates["coordinates"] = coordinates__coordinates
        self.coordinates["type"] = coordinates__type

        # Place object
        self.place = {}
        self.place["id"] = place__id
        self.place["url"] = place__url
        self.place["place_type"] = place__place_type
        self.place["name"] = place__name
        self.place["full_name"] = place__full_name
        self.place["country_code"] = place__country_code
        self.place["country"] = place__country
        self.place["attributes"] = place__attributes
        # Place-Bounding box
        self.place["bounding_box"] = {}
        self.place["bounding_box"]["coordinates"] =\
            place__bounding_box__coordinates
        self.place["bounding_box"]["type"] = place__bounding_box__type

        # Entities object
        self.entities = {}
        # Entities hashtags
        self.entities["hashtags"] = {}
        self.entities["hashtags"]["indices"] = entities__hashtags__indices
        self.entities["hashtags"]["text"] = entities__hashtags__text
        # Entities media
        self.entities["media"] = {}
        self.entities["media"]["display_url"] = entities__media__display_url
        self.entities["media"]["expanded_url"] = entities__media__expanded_url
        self.entities["media"]["id"] = entities__media__id
        self.entities["media"]["id_str"] = entities__media__id_str
        self.entities["media"]["indices"] = entities__media__indices
        self.entities["media"]["media_url"] = entities__media__media_url
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
        self.entities["urls"]["display_url"] = entities__urls__display_url
        self.entities["urls"]["expanded_url"] = entities__urls__expanded_url
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
        self.entities["user_mentions"]["id"] = entities__user_mentions__id
        self.entities["user_mentions"]["id_str"] =\
            entities__user_mentions__id_str
        self.entities["user_mentions"]["indices"] =\
            entities__user_mentions__indices
        self.entities["user_mentions"]["name"] = entities__user_mentions__name
        self.entities["user_mentions"]["screen_name"] =\
            entities__user_mentions__screen_name
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

    def __getitem__(self, key):
        return getattr(self, key)


class NotValidTweetError(Exception):
    pass


def get_tweet_from_csv_raw_line(header, line):
    """
    Given a CSV header and a CSV line in raw format (strings with comma
    separated values), extract the values for every field and then calls
    get_tweet_from_csv_line to instance a Tweet.
    Returns a Tweet object
    """

    header_fields = format_csv.split_csv_line(header)
    line_fields = format_csv.split_csv_line(line)

    return get_tweet_from_csv_line(header_fields, line_fields)


def get_tweet_from_csv_line(header_fields, line_fields):
    """
    Given the fields of a CSV line and header, the function instances a Tweet
    object with all the non-empty attributes initialized to the values
    indicated in the CSV entry.
    Returns a Tweet object
    """

    tweet_contents = {}
    for i in range(len(line_fields)):
        if line_fields[i] != '':
            tweet_contents[header_fields[i].replace(".", "__")] =\
                line_fields[i]

    # try:
    #     tweet = Tweet(**tweet_contents)
    # except Exception as e:
    #     print("An error of type " + type(e).__str__ + "ocurred")
    #     raise Exception
#
#     return tweet
    return Tweet(**tweet_contents)


def get_tweets_from_csv(csv_file):
    """
    Take one argument: a path pointing to a valid CSV file.
    The function reads the file, which should be a collection of tweets with a
    header indicating the tweet fields (user.id, place.bounding_box.type,
    etc.), and instances a new Tweet object for each of the lines in the CSV
    file, assigning each value in the CSV to the corresponding Tweet attribute.
    Returns a list of the Tweet objects instanced.
    """

    tweets = []

    with open(csv_file, 'r') as csv_object:
        header = csv_object.readline()
        body = csv_object.readlines()

    header_fields = format_csv.split_csv_line(header)

    # Check that the header contains valid fields
    test_tweet = Tweet()
    for field in header_fields:
        field_components = field.split(".")
        checking_dict = test_tweet.__dict__
        error_string = ""
        for component in field_components:
            error_string += component
            if (checking_dict is None) or (component not in checking_dict):
                logger.error('The field in the header ' + error_string +
                             'is not a valid element of a Tweet')
                raise NotValidTweetError("Header contains field which doesn't"
                                         + " belong to tweet specification: "
                                         + error_string)
            checking_dict = checking_dict[component]
            error_string += "."

    # Go through every tweet in the file, instance it using the 'Tweet' class
    # and add it to the list 'tweets'
    for j in range(len(body)):
        line_fields = format_csv.split_csv_line(body[j])
        tweets.append(get_tweet_from_csv_line(header_fields, line_fields))

    return tweets


def get_tweet_fields_subset(
        tweet: Tweet,
        fields: List[str]
        ) -> Dict:
    """
    Given a Tweet objects, keep just the specified fields and return a dict
    with just the information specified
    """

    tweet_subset = {}
    for field in fields:
        try:
            tweet_subset[field] = tweet[field]
        except AttributeError:
            pass
    return tweet_subset


def get_tweet_collection_fields_subset(
        tweet_collection: Union[List[Tweet], Generator[Tweet, None, None]],
        fields: List[str]
        ) -> Generator[Dict, None, None]:
    """
    Given a list of Tweet objects, keep just the specified fields and
    return a generator of dicts with just the information specified
    """
    for tweet in tweet_collection:
        yield get_tweet_fields_subset(tweet, fields)
