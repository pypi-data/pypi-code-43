import tweepy
import emoji

import pandas as pd
import numpy as np
import regex as re

from google.cloud import translate

translate_client = None
translate_active = False

CONSUMER_KEY = None
CONSUMER_SECRET = None
OWNER = None
OWNER_ID = None

api = None

M5S_NAME = '@Mov5Stelle'
LEGA_NAME = '@LegaSalvini'
PADE_NAME = '@pdnetwork'
FORZA_NAME ='@forza_italia'

party_names = [M5S_NAME, LEGA_NAME, PADE_NAME, FORZA_NAME]

def activate_translator():
    global translate_client, translate_active
    
    try:
        translate_client = translate.Client()
    except:
        print('Make sure have the credentials to acces the google translate api')
        translate_client = None
        return
    
    translate_active = True

def set_tweepy_authorizaton(consumer_key, consumer_secret, owner, owner_id):
    global CONSUMER_KEY, CONSUMER_SECRET, OWNER, OWNER_ID, api

    CONSUMER_KEY = consumer_key
    CONSUMER_SECRET = consumer_secret
    OWNER = owner
    OWNER_ID = owner_id

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(owner, owner_id)

    api = tweepy.API(auth, wait_on_rate_limit=True)

def get_followers(name='@pdnetwork', size=1):
    if api == None:
        print('Make sure you set up the tweepy authorization using your credentials')
        return

    ids = []
    stop = 0
    for page in tweepy.Cursor(api.followers_ids, screen_name="@pdnetwork").pages():
        if stop>size:
            break

        stop+=1
        ids.extend(page)
    return ids

def get_tweets_from_user(user_id):
    try:
        tweets = api.user_timeline(user_id, per_page=50)
    except:
        return None
    
    if len(tweets) < 10:
        return None
    
    tweets_info = []
    tweet_info_needed = ['id_str', 'created_at', 'text',
                         'is_quote_status', 'retweet_count', 'lang'
                        ]
    user_info_needed = ['name', 'location', 'description', 'id_str']
    
    for tweet in tweets:
        to_append = {}
        for info in tweet_info_needed:
            to_append[info] = tweet._json[info]
        
        hashtags = tweet._json['entities']['hashtags']
        
        to_append['hashtags'] = []
        for hashtag in hashtags:
            to_append['hashtags'].append(hashtag['text'])
        
        for info in user_info_needed:
            to_append['user_' + info] = tweet._json['user'][info]
        
        tweets_info.append(to_append)
        
    return tweets_info

def get_emojis(text):
    emoji_list = []
    data = re.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI for char in word):
            emoji_list.append(word)

    return emoji_list

def del_emojis(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

def translate_tweet(tweet_text, lang='en'):
    return translate_client.translate(tweet_text, target_language=lang)['translatedText']

def clean_tweet(tweet):
    cleaned_tweet = re.sub(r'@\S+', '', tweet) # Remove mentions
    cleaned_tweet = re.sub(r'https\S+', '', cleaned_tweet) # Remove urls
    cleaned_tweet = re.sub(r'\S+…', '', cleaned_tweet) # Remove truncated last word
    cleaned_tweet = re.sub(r'#', '', cleaned_tweet)
    cleaned_tweet = re.sub(r'\n', '', cleaned_tweet)
    cleaned_tweet = re.sub(r'\t', '', cleaned_tweet)
    cleaned_tweet = del_emojis(cleaned_tweet)
    
    return cleaned_tweet.strip()

def get_tweets_from_party_followers(party):
    df = pd.DataFrame()
    user_ids = get_followers(party)
    
    for user_id in user_ids:
        tweets = get_tweets_from_user(user_id)
        
        if tweets == None:
            continue
        
        for tweet in tweets:
            df = df.append(tweet)
        
    return df

def format_dataframe(df):
    df['clean_text'] = df['text'].apply(clean_tweet)
    df['emojis'] = df['text'].apply(get_emojis)

    return df