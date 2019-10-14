from tweet_model.tweet import Tweet
from tweet_model import utils

import pytest
import os
import datetime


#################
#   FIXTURES    #
#################
@pytest.fixture(scope="module")
def empty_tweet():
    return Tweet()


@pytest.fixture(scope="module")
def tweet1():
    return Tweet(id="128977963458933",
                 text="En un lugar de la Mancha...",
                 user__name="Julio César",
                 user__created_at="2019-05-01 23:54:27")


@pytest.fixture(scope="module")
def tweet2(csv_file_path):
    """
    Returns a real tweet instantiated from a CSV. For this to work
    test_get_tweet_from_csv_raw_line_OK should be OK. The instantiated tweet is
    the first in the CSV doc (2nd line, just after the header)
    """

    with open(csv_file_path) as file_reader:
        header = file_reader.readline()
        tweet_contents = file_reader.readline()
    tweet = utils.get_tweet_from_csv_raw_line(header, tweet_contents)
    return tweet


@pytest.fixture(scope="module")
def dict_tweet1():
    dictionary_tweet1 = {}
    dictionary_tweet1["id"] = 128977963458933
    dictionary_tweet1["text"] = "En un lugar de la Mancha..."
    dictionary_tweet1["user"] = {}
    dictionary_tweet1["user"]["name"] = "Julio César"
    dictionary_tweet1["user"]["created_at"] =\
        datetime.datetime(2019, 5, 1, 23, 54, 27)

    return dictionary_tweet1


@pytest.fixture(scope="module")
def dict_tweet2():
    """
    Dictionary representation of the same data as the fixture "tweet2"
    """

    dictionary_tweet2 = {}
    dictionary_tweet2["created_at"] = datetime.datetime(2019, 5, 1, 23, 59, 16)
    dictionary_tweet2["favorite_count"] = 0
    dictionary_tweet2["id"] = 1123738691938193410
    dictionary_tweet2["in_reply_to_screen_name"] = 'leoffmiranda'
    dictionary_tweet2["in_reply_to_status_id"] = 1123737830554066945
    dictionary_tweet2["in_reply_to_user_id"] = 176244402
    dictionary_tweet2["is_quote_status"] = False
    dictionary_tweet2["retweet_count"] = 0
    dictionary_tweet2["source"] =\
        '<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>'
    dictionary_tweet2["text"] = '@leoffmiranda perfeito. Pele ta na categoria Tolkien pra fantasia, pode ate existir escritores de fantasia melhores… https://t.co/sl5Nd82l71'
    dictionary_tweet2["truncated"] = True

    dictionary_tweet2["entities"] = {}
    dictionary_tweet2["entities"]["urls"] = {}
    dictionary_tweet2["entities"]["urls"]["expanded_url"] =\
        ['https://twitter.com/i/web/status/1123738691938193410']

    dictionary_tweet2["entities"]["user_mentions"] = {}
    dictionary_tweet2["entities"]["user_mentions"]["screen_name"] = ['leoffmiranda']

    dictionary_tweet2["user"] = {}
    dictionary_tweet2["user"]["created_at"] = datetime.datetime(2009, 8, 24, 20, 21, 5)
    dictionary_tweet2["user"]["favourites_count"] = 108774
    dictionary_tweet2["user"]["followers_count"] = 4803
    dictionary_tweet2["user"]["friends_count"] = 1044
    dictionary_tweet2["user"]["geo_enabled"] = True
    dictionary_tweet2["user"]["id"] = 68503128
    dictionary_tweet2["user"]["lang"] = "pt"
    dictionary_tweet2["user"]["listed_count"] = 45
    dictionary_tweet2["user"]["location"] = "ArenaCorinthians"
    dictionary_tweet2["user"]["name"] = 'Corinthians matou o futebol. #RipFutibas'
    dictionary_tweet2["user"]["profile_image_url"] = 'http://pbs.twimg.com/profile_images/1099105765711929345/dz5f_SdP_normal.jpg'
    dictionary_tweet2["user"]["screen_name"] = 'tathiane_vidal'
    dictionary_tweet2["user"]["statuses_count"] = 177470
    dictionary_tweet2["user"]["verified"] = False

    return dictionary_tweet2


@pytest.fixture(scope="module")
def csv_file_path():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, "resources", "01.csv")


@pytest.fixture(scope="module")
def fake_file_path():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, "resources", "false.csv")


##############
#   TESTS    #
##############
class TestTweetObjects:
    def test_empty_tweet_instantiation__OK(self, empty_tweet):
        """
        Check that a Tweet object can be instantiated with no values and
        then all its not-nested attributes will be None (or False, since Nones
        can be casted to boolean as False)
        """

        for key, value in empty_tweet.__dict__.items():
            if type(value) is not dict:
                assert value in (None, False)

    def test_nonempty_tweet_instantiation__values_OK(self, tweet1):
        """
        Check some of the nested and non-nested fields after instantiating a
        Tweet with some initial valid values
        """

        assert tweet1.id == 128977963458933
        assert tweet1.text == "En un lugar de la Mancha..."
        assert tweet1["user"]["name"] == "Julio César"
        assert tweet1["user"]["created_at"] ==\
            datetime.datetime(2019, 5, 1, 23, 54, 27)
        assert tweet1["coordinates"]["coordinates"] is None

    def test_nonempty_tweet_instantiation__typing_OK(self, tweet1):
        """
        Check some of the nested and non-nested fields have the right typing
        """

        assert type(tweet1.id) == int
        assert type(tweet1.text) == str
        assert type(tweet1["user"]["name"]) == str
        assert type(tweet1["user"]["created_at"]) == datetime.datetime
        assert isinstance(tweet1["coordinates"]["coordinates"], type(None))

    def test_get_tweet_fields_subset_OK(self, tweet1):
        """
        Check that the "as_json" function returns a correct JSON representation
        of the Tweet object
        """

        new_dict = tweet1.get_tweet_fields_subset(["id", "text"])
        assert new_dict == {"id": 128977963458933,
                            "text": "En un lugar de la Mancha..."}

    def test_tweet_list_fields_OK(self, tweet2):
        """
        Check that the list fields in the instantiated tweets work as expected
        """

        assert tweet2["entities"]["user_mentions"]["screen_name"] == \
            ["leoffmiranda"]

    def test_as_short_json_tweet1_OK(self, tweet1):
        """
        Check that the function "as_short_json" returns a correct
        representation of the tweet in dict form and with just the non-empty
        fields
        """

        result = {}
        result["id"] = 128977963458933
        result["text"] = "En un lugar de la Mancha..."
        result["user"] = {}
        result["user"]["name"] = "Julio César"
        result["user"]["created_at"] =\
            datetime.datetime(2019, 5, 1, 23, 54, 27)

        assert result == tweet1.as_short_json()

    def test_as_short_json_tweet2_OK(self, tweet2, dict_tweet2):
        """
        Check that the function "as_short_json" returns a correct
        representation of the tweet2 in dict form and with just the non-empty
        fields
        """

        assert tweet2.as_short_json() == dict_tweet2


class TestTweetUtils:
    def test_get_tweet_from_csv_raw_line_OK(self, csv_file_path):
        """
        Check that a Tweet object can be instantiated from a CSV file that
        contains at least a header in the 1st line indicating the names of the
        fields and a tweet description in the 2nd with a value for each of that
        fields.
        """

        with open(csv_file_path) as file_reader:
            header = file_reader.readline()
            tweet_contents = file_reader.readline()
        tweet = utils.get_tweet_from_csv_raw_line(header, tweet_contents)

        assert tweet["id"] == 1123738691938193410

    def test_get_tweets_from_csv_OK(self, csv_file_path):
        """
        Check that all the tweets from a CSV file can be instantiated at once
        using the function "get_tweets_from_csv". Check the length of the list
        so it matches the lines in the CSV and check some ids of the
        instantiated tweets
        """

        tweets = utils.get_tweets_from_csv(csv_file_path)

        assert len(tweets) == 3214
        assert tweets[3213]["id"] == 1123376500898783238

    def test_get_tweets_from_csv_ERROR(self, fake_file_path):
        """
        Check that, if provided with a file that doesn't correspond to a tweet
        specification, an appropriate exception is raised
        """

        with pytest.raises(utils.NotValidTweetError):
            utils.get_tweets_from_csv(fake_file_path)
