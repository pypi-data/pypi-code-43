import logging
import re
from typing import Union, Dict, List, Generator

from tweet_model.tweet import Tweet
from tweet_manager.lib import format_csv

# Configure logger
LOG_FORMAT = '[%(asctime)-15s] %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger("logger")


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


def get_tweet_from_csv_line_OLD(header_fields, line_fields):
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
    return Tweet(**tweet_contents)


def get_tweet_from_csv_line(header_fields, line_fields):
    """
    Given the fields of a CSV line and header, the function instances a Tweet
    object with all the non-empty attributes initialized to the values
    indicated in the CSV entry.
    Accepts embedded tweets in "quoted_status" and "retweeted_statusW
    Returns a Tweet object
    """

    tweet_contents = {}
    quoted_contents = {}
    retweeted_contents = {}
    quoted_pattern = re.compile(r"^(quoted_status\.)(.*)$")
    retweeted_pattern = re.compile(r"^(retweeted_status\.)(.*)$")

    for i in range(len(line_fields)):
        if line_fields[i] != '':
            quoted_match = quoted_pattern.match(header_fields[i])
            retweeted_match = retweeted_pattern.match(header_fields[i])
            if quoted_match is not None:
                quoted_contents[
                    quoted_match.group(2).replace(".", "__")] =\
                    line_fields[i]
            elif retweeted_match is not None:
                retweeted_contents[
                    retweeted_match.group(2).replace(".", "__")] =\
                    line_fields[i]
            else:
                tweet_contents[header_fields[i].replace(".", "__")] =\
                    line_fields[i]

    if bool(quoted_contents):    # Check non empty
        tweet_contents["quoted_status"] = Tweet(**quoted_contents)
    if bool(retweeted_contents):    # Check non empty
        tweet_contents["retweeted_status"] = Tweet(**retweeted_contents)

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
                logger.error('The field in the header ' + error_string
                             + 'is not a valid element of a Tweet')
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


def get_tweet_collection_fields_subset(
        tweet_collection: Union[List[Tweet], Generator[Tweet, None, None]],
        fields: List[str])\
        -> Generator[Dict, None, None]:
    """
    Given a list of Tweet objects, keep just the specified fields and
    return a generator of dicts with just the information specified
    """
    for tweet in tweet_collection:
        yield tweet.get_tweet_fields_subset(fields)


class NotValidTweetError(Exception):
    pass
