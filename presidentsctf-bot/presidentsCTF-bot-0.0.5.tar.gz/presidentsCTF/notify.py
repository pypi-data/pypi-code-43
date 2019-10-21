#!/usr/bin/env python3

"""
Slack - get live updates.
"""
import logging

import slack
import tweepy

from presidentsCTF import config

def send_slack_messages(messages):
    """Sends a message to the slack channel specified in the config"""
    token = config.config["slack"]["token"]
    channel = config.config["slack"]["channel"]

    client = slack.WebClient(token)

    logging.debug("Sending {} messages to slack".format(len(messages)))
    for msg in messages:
        response = client.chat_postMessage(channel=channel,text=msg)
        if not response["ok"]:
            logging.warn("Error sending slack message: {}".format(response))

def send_twitter_messages(messages):
    """Sends a message to a twitter account specified in the config"""
    conf = config.config["twitter"]
    auth = tweepy.OAuthHandler(conf["consumer_key"], conf["consumer_secret"])
    auth.set_access_token(conf["access_token"], conf["access_token_secret"])
    api = tweepy.API(auth)

    logging.debug("Sending {} messages to twitter".format(len(messages)))
    for msg in messages:
        try:
            api.update_status(msg)
        except tweepy.error.TweepError as e:
            logging.warn(e)
