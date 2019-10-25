# -*- coding: utf-8 -*-
#!/usr/bin/python3

# Narrator: Visualizer for tweet data
# by Chris Lindgren <chris.a.lindgren@gmail.com>
# Distributed under the BSD 3-clause license.
# See LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause for details.

# WHAT IS IT?
# A set of functions that process and create regular sum and temporal charts to help refine broader narrative of the data set(s).
# It functions only with Python 3.x and is not backwards-compatible.

# Warning: narrator performs very little custom error-handling, so make sure your inputs are formatted properly! If you have questions, please let me know via email.
from os import listdir
from os.path import isfile, join
import arrow
import ast
import csv
import pandas as pd
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import functools
import operator
import re
import emoji
import string
import math

'''
    See README.md for an overview and comments for extended explanation.
'''
class topperObject:
    '''an object class with attributes that store desired top X samples from the corpus'''
    def __init__(self, top_x_tweets=None, top_x_hashtags=None, top_x_tweeters=None,
                top_x_targets=None, top_x_topics=None, top_x_urls=None, top_x_rts=None,
                period_dates=None):
        self.top_x_hashtags = top_x_hashtags
        self.top_x_tweeters = top_x_tweeters
        self.top_x_tweets = top_x_tweets
        self.top_x_topics = top_x_topics
        self.top_x_urls = top_x_urls
        self.top_x_rts = top_x_rts
        self.period_dates = period_dates

##################################################################

## General Functions

##################################################################

'''
    Initialize topperObject
'''
def initializeTO():
    return topperObject()

'''
    date_range_writer: Takes beginning date and end date to write a range of those dates per Day as a List
    - Args:
        - bd= String. Beginning date in YYYY-MM-DD format
        - ed= String. Ending date in YYYY-MM-DD format
    - Returns List of arrow date objects for whatever needs.
'''
def date_range_writer(bd, ed):
    # Make period date-range
    begin_date = arrow.get(bd, 'YYYY-MM-DD')
    end_date = arrow.get(ed, 'YYYY-MM-DD')
    date_range = arrow.Arrow.range('day', begin_date, end_date)
    return date_range

'''
    period_writer():  Accepts list of lists of period date information
    and returns a Dict of per Period dates for temporal analyses.
        - Args:
            - periodObj: Optional first argument periodObject, Default is None
            - 'ranges': Hierarchical list in following structure:
                ranges = [
                    ['p1', ['2018-01-01', '2018-03-30']],
                    ['p2', ['2018-04-01', '2018-06-12']],
                    ...
                ]
'''
def period_dates_writer(topperObject=None, **kwargs):
    period_dict = {}
    for r in kwargs['ranges']:
        period_list = []
        p_dates = date_range_writer(r[1][0], r[1][1]) # send period date range
        for d in p_dates:
            # Append returned date range to period list
            period_list.append( str(d.format('YYYY-MM-DD')) )
        period_dict.update({r[0]: period_list})

    if topperObject == None:
        return period_dict
    else:
        topperObject.period_dates = period_dict
        return topperObject

##################################################################

## SUMMARIZER FUNCTIONS

##################################################################
'''
    skeletor: Takes desired date range and list of keys to create a skeleton Dict before hydrating it with the sample values. Overall, this provides default 0 Int values for every keyword in the sample.
    - Args:
        - aggregate_level= String. Current options include:
            - 'day': per Day
            - 'period_day': Days per Period
            - 'period': per Period
        - date_range= 
            - If 'day' aggregate level, a List of per Day dates ```['2018-01-01', '2018-01-02', ...]```
            - If 'period' aggregate level, a Dict of periods with respective date Lists: ```{{'1': ['2018-01-01', '2018-01-02', ...]}}```
        - keys= List of keys for hydrating the Dict
    - Returns full Dict 'skeleton' with default 0 Integer values for the grouper() function
'''
def skeletor(**kwargs):
    dict_groups = {}
    # Write per Day Dict skeleton
    if kwargs['aggregate_level'] == 'day':
        for r in kwargs['date_range']:
            dict_groups.update({ r: {} })
            for h in kwargs['keys']:
                dict_groups[r].update({ h: 0})
    # Write Days per Period Dict skeleton
    elif kwargs['aggregate_level'] == 'period_day':
        for p in kwargs['date_range']:
            dict_groups.update({ p: {} })
            for day in kwargs['date_range'][p]:
                dict_groups[p].update({ day: {} })
                for h in kwargs['keys']:
                    dict_groups[p][day].update({h: 0 })
    # Write per Period Dict skeleton
    elif kwargs['aggregate_level'] == 'period':
        for p in kwargs['date_range']:
            dict_groups.update({ p: {} })
            for h in kwargs['keys']:
                dict_groups[p].update({h: 0 })
    return dict_groups

'''
    get_sample_size: Helper function for summarizer functions. If sample=True,
    then sample sent here and returned to the summarizer for output.
    - Args:
        - sort_check= Boolean. If True, sort the corpus.
        - sort_date_check= Boolean. If True, sort corpus based on dates.
        - df= DataFrame of corpus.
        - ss= Integer of sample size to output.
        - sample_check= Boolean. If True, use ss value. If False, use full corpus.
    - Returns DataFrame to summarizer function.
'''
def get_sample_size(sort_check, sort_date_check, sort_type, df, ss, sample_check):
    # Check if to be sorted or not
    if sort_check == True:
        sorted_df = sorted(df, key=lambda x: x[1], reverse=True)
        print('\n\nTop 10 sorted by counts:\n\n', sorted_df[:10])
        # Check if delimited sample size
        if sample_check == True:
            top_dates = sorted_df[:ss]
            return top_dates
        elif sample_check == False:
            return sorted_df
    elif sort_date_check == True:
        if sort_type == True:
            sorted_df = sorted(df, key=lambda x: x[0], reverse=True) #descending
        elif sort_type == False:
            sorted_df = sorted(df, key=lambda x: x[0], reverse=False) #ascending
        
        print('\n\nFirst 10 sorted by dates:\n\n', sorted_df[:10])
        # Check if delimited sample size
        if sample_check == True:
            top_dates = sorted_df[:ss]
            return top_dates
        elif sample_check == False:
            return sorted_df
    elif sort_check == False and sort_date_check == False:
        print('\n\nFirst 10:\n\n', df[:10])
        # Check if delimited sample size
        if sample_check == True:
            first_dates = df[:ss]
            return first_dates
        elif sample_check == False:
            return df

        
'''
    whichPeriod: Helper function for grouper(). Isolates what period a date is in for use.
    - Args: 
        - period_dates= Dict of Lists per period
        - date= String. Date to lookup.
    - Returns String of period to grouper().
'''
def whichPeriod(period_dates, date):
    for p in period_dates:
        if date in period_dates[p]:
            return p
    return False

'''
    grouper: Takes default values in 'skeleton' Dict and hydrates them with sample List of Tuples
    - Args:
        - group_type= String. Current options include:
            - 'day': per Day
            - 'period_day': Days per Period
            - 'period': per Period
        - listed_tuples= List of Tuples from get_sample_size(). 
            - Example structure is the following: [(('keyword', '01-27-2019'), 100), (...), ...]
        - skeleton= Dict. Fully hydrated skeleton dict, wherein grouper() updates its default 0 Int values.
    - Returns Dict of updated values per keyword
'''
def grouper(**kwargs):
    print('\n\nHydrating skeleton with sample now ...')
    if kwargs['group_type'] == 'day':
        for g in kwargs['listed_tuples']:
            if g[0][1] in kwargs['skeleton']:
                kwargs['skeleton'][g[0][1]][g[0][0]] = g[1]
    elif kwargs['group_type'] == 'period_day':
        for g in kwargs['listed_tuples']:
            # Parse periods
            for p in kwargs['skeleton']:
                # If date in period, assign new keyword value
                if g[0][1] in kwargs['skeleton'][p]:
                    kwargs['skeleton'][p][g[0][1]][g[0][0]] = g[1]
    elif kwargs['group_type'] == 'period':
        for g in kwargs['listed_tuples']:
            # Parse periods and accrue totals for each hashtag
            for p in kwargs['skeleton']:
                # Accrue totals per period
                p_check = whichPeriod(kwargs['period_dates'], g[0][1]) #returns period of date
                if p_check is not False:
                    kwargs['skeleton'][p_check][g[0][0]] = g[1] + kwargs['skeleton'][p_check][g[0][0]]
                    
    return kwargs['skeleton']

'''
    grouped_dict_to_df:
    - Args:
        - sum_option= String. Options for grouping into a Dataframe.
            - group_hash_temporal= Multiple groups of hashtags
        - output_type= Sring. oPtions for DF outputs
            - d3js= Good for small multiples in D3.js 
            - python= Good for small multiples in matplot
        - time_agg_type= String. Options for type of temporal grouping.
            - period= Grouped by periods
        - group_dict= Hydrated Dict to convert to a DataFrame for visualization or output
    - Returns DataFrame for use with a plotter function or output as CSV
'''
def grouped_dict_to_df(**kwargs):
    if kwargs['sum_option'] == 'group_hash_temporal' and kwargs['time_agg_type'] == 'period':
        
        if kwargs['output_type'] == 'd3js':
            ph = []
            for p in kwargs['group_dict']:
                for ht in kwargs['group_dict'][p]:
                    ph.append([int(p), ht, kwargs['group_dict'][p][ht]])

            columns = ['period','hashtag','count']
            df_return = pd.DataFrame(ph, columns=columns)
            
            return df_return
        elif kwargs['output_type'] == 'python':
            period_col_values = []
            data = {'columns': {}}
            for p in kwargs['group_dict']:
                for ht in kwargs['group_dict'][p]:
                    # Append hashtag values
                    if ht not in data['columns']:
                        data['columns'].update({ht: [ kwargs['group_dict'][p][ht] ]})
                    elif ht in data['columns']:
                        data['columns'][ht].append(kwargs['group_dict'][p][ht])
                    # Append period
                    if int(p) not in period_col_values:
                        period_col_values.append(int(p))

            df_periods = pd.DataFrame({'period': period_col_values})
            df_hts = pd.DataFrame(data['columns'])
            df_return = df_periods.join(df_hts)
            
            return df_return

'''
    find_term: Helper function for accumulator(). Searches for hashtag in tweet.
        If there, return True. If not, return False.
        - Args:
            - search= String. Term to search for.
            - text= String. Text to search.
        - Returns Boolean
'''
def find_term(search, text):
    result = re.findall('\\b'+search+'\\b', text, flags=re.IGNORECASE)
    if len(result) > 0:
        print('Term:', search, '\n\nResult;', result)
        return True
    else:
        return False

'''
    accumulator: Helper function for summarizer functions. Accumulates by hashtag lists and keyword lists.
    - Args:
        - checker= String. Options for accumulation:
            - hashtags: Hashtag search.
            - keywords: Keyword search.
        - df_list= List. DataFrame passed as a list for traversing
        - check_list= List. List of terms to accrue and append
            - If hashtags, converted to List of hashtags
            - If keywords, List of dicts, where each key is its accompanying hashtag.
    - Returns a hydrated list of Tuples with hashtags and accompanying date.
'''
def accumulator(checker, df_list, check_list):
    if checker == 'hashtags':
        print('Started accumulating tweets with hashtags.')
        hashes_and_dates = []
        for h in df_list:
            ht = ast.literal_eval(h[1])
            if type(ht) is not float:
                ht = [n.strip() for n in ht]
                if len(ht) > 1:
                    for i in ht:
                        # Check if in hash_list
                        if i in check_list:
                            # Append hashtag and date
                            hashes_and_dates.append( (i, h[0], int(float(h[2]))) )
                elif len(ht) == 1:
                    if ht[0] in check_list:
                        # Append hashtag and date
                        hashes_and_dates.append( (ht[0], h[0], int(float(h[2]))) )
        print('Accumulating tweets with hashtags complete.')
        return hashes_and_dates
    elif checker == 'keywords':
        print('Started accumulating tweets with keywords.')
        keywords_and_dates = []
        # Traverse list of tweets, check for keywords
        for t in df_list:
            for ht in check_list:
                for kw in ht:
                    for k in ht[kw]:
                        # k = keyword in each hashtag's list
                        # Search for it in a tweet
                        check_keyword = k in str(t[2])
                        # Filter out if hashtag_list hashtag is used
                        if check_keyword == True:
                            check_ht = find_term( kw, str(t[2]) )
                            # If not found as hashtag_list, append it
                            if check_ht == False:
                                keywords_and_dates.append( (kw, t[0], int(float(t[3])), k) )
        print('Accumulating tweets with keywords complete.')
        return keywords_and_dates

'''
    hashtag_summarizer: Counts hashtag use and optionally as temporally
    distributed.
    - Args:
        - search_option: String. Either 'hashtags' or' tweets_and_hashtags'. The second 
            option searches for hashtags in the hashtag column and keywords in 
            the tweet column. For example, you search for someone's name in the 
            corpus that isn't always represented as a hashtag.
        - keyword_list= List. A list of keywords of which you search within the tweet column.
        - df_corpus= DataFrame of tweet corpus
        - hash_col= String value of the DataFrame column name for hashtags.
        - tweet_col= String value of the DataFrame column name for tweets.
        - sum_option= String. Current options for sampling include the following:
            - 'sum_all_hash': Sum of all hashtags across entire corpus
            - 'sum_group_hash': Sum of a group of hashtags (List) across entire corpus
            - 'sum_single_hash': Sum of a single hashtag (String) across entire corpus
            - 'single_hash_per_day': Sum of single hashtag per Day in provided range
            - 'group_hash_per_day': Sum of group of hashtags per Day in provided range
        - single_hash= String of single hashtag to isolate.
        - hash_list= List of hashtags to isolate.
        - time_agg_type= If sum by group temporally, define its temporal aggregation:
            - 'day': Aggregate time per Day
            - 'period': Aggregate time per period
        - date_col= String value of the DataFrame column name for the dates in xx-xx-xxxx format.
        - sort_check= Boolean. If True, sort sums per day.
        - sort_date_check= Boolean. If True, sort by dates.
        - sort_type= Boolean. If True, descending order. If False, ascending order.
        - output_type= String. OPtions for particular Dataframe output
            - d3js= DF in a format conduive for small multiples chart in D3.js
            - python= DF in a format conduive for small multiples chart in python's matplot
    - Return: Depending on option, a sample as a List of Tuples or Dict of grouped samples
'''
def hashtag_summarizer(**kwargs):
    # 1. Clean data
    print('Cleaning the hashtag data.')
    clean_hash_data = kwargs['df_corpus'][(kwargs['df_corpus'][kwargs['hash_col']].isnull() == False)]
    clean_hash_data_filtered = clean_hash_data[clean_hash_data[kwargs['hash_col']].str.contains('#')]
    clean_hash_data_filtered = clean_hash_data.reset_index()
    
    print('Hashtag data cleaned, now writing samples.')
    # 2. Count and sort
    
    cleaned_hashtags = []
    # Option 2.1 - Count per Hashtag, across entire corpus
    if kwargs['sum_option'] == 'sum_all_hash':
        print('Hydrating by desired', kwargs['sum_option'])
        for h in list(clean_hash_data_filtered[kwargs['hash_col']]):
            h = ast.literal_eval(h)
            if type(h) is not float:
                h = [n.strip() for n in h]
                if len(h) > 1 and type(h) is not float:
                    for i in h:
                        cleaned_hashtags.append(i)
                elif len(h) == 1 and type(h) is not float:
                    cleaned_hashtags.append(h[0]) 
        
        # Count'em up
        hashtag_date_totals = list(Counter(cleaned_hashtags).items())
        
        print('Writing up the sample')
        top_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            df=hashtag_date_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )
        return top_x
    # Option 2.2 - Count group of hashtags across entire corpus
    elif kwargs['sum_option'] == 'sum_group_hash':
        print('Hydrating by desired', kwargs['sum_option'])
        for h in list(clean_hash_data_filtered[kwargs['hash_col']]):
            h = ast.literal_eval(h)
            if type(h) is not float:
                h = [n.strip() for n in h]
                if len(h) > 1 and type(h) is not float:
                    for i in h:
                        if i in kwargs['hash_list']:
                            cleaned_hashtags.append(i)
                elif len(h) == 1 and type(h) is not float and h[0] in kwargs['hash_list']:
                    cleaned_hashtags.append(h[0]) 
        
        # Count'em up
        hashtag_date_totals = list(Counter(cleaned_hashtags).items())
        
        print('Writing up the sample')
        top_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            df=hashtag_date_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )
        return top_x
    # Option 2.3 - Count single hashtag across entire corpus
    elif kwargs['sum_option'] == 'sum_single_hash':
        print('Hydrating by desired', kwargs['sum_option'])
        for h in list(clean_hash_data_filtered[kwargs['hash_col']]):
            h = ast.literal_eval(h)
            if type(h) is not float:
                h = [n.strip() for n in h]
                if len(h) > 1 and type(h) is not float:
                    for i in h:
                        if i == kwargs['single_hash']:
                            cleaned_hashtags.append(i)
                elif len(h) == 1 and type(h) is not float and h[0] == kwargs['single_hash']:
                    cleaned_hashtags.append(h[0]) 
        
        hashtag_date_totals = list(Counter(cleaned_hashtags).items())
        
        print('Writing up the sample')
        top_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            df=hashtag_date_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )
        return top_x
    # Option 2.4 - Count a single hashtag temporally across entire corpus
    elif kwargs['sum_option'] == 'single_hash_temporal':
        # Isolate columns of interest: Dates (xx-xx-xxxx) and 
        df_hash_data = clean_hash_data_filtered[[kwargs['date_col'], kwargs['hash_col'], [kwargs['id']]]]
        print('Hydrating by desired', kwargs['sum_option'])
        hashtags_and_dates = []
        for h in df_hash_data.values.tolist():
            ht = ast.literal_eval(h[1])
            if type(ht) is not float:
                ht = [n.strip() for n in ht]
                if len(ht) > 1:
                    for i in ht:
                        # Check if in hash_list
                        if i == kwargs['single_hash']:
                            # Append hashtag and date
                            hashtags_and_dates.append( (i, h[0]) )
                elif len(ht) == 1 and ht[0] == kwargs['single_hash']:
                    # Append hashtag and date
                    hashtags_and_dates.append( (ht[0], h[0]) )
        
        hashtag_date_totals = list(Counter(hashtags_and_dates).items())

        print('Writing up the sample')
        top_date_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            df=hashtag_date_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )

        # Group sample per Day or per Period
        temporal_top_date_x = grouper(
            listed_tuples=top_date_x,
            group_type=kwargs['time_agg_type'],
            skeleton=kwargs['skeleton']
        )
        return temporal_top_date_x
    # Option 2.5 - Count grouping of hashtags temporally across entire corpus
    elif kwargs['sum_option'] == 'group_hash_temporal':
        print('Hydrating by desired', kwargs['sum_option'])
        merged_hashtags_and_dates = []
        hashtags_and_dates = []
        # Write Lists with desired keyword and/or hashtag info
        if kwargs['search_option'] == 'hashtags':
            # If hashtags a concern ONLY
            df_hash_data = clean_hash_data_filtered[[kwargs['date_col'], kwargs['hash_col']]]
            for h in df_hash_data.values.tolist():
                ht = ast.literal_eval(h[1])
                if type(ht) is not float:
                    ht = [n.strip() for n in ht]
                    if len(ht) > 1:
                        for i in ht:
                            # Check if in hash_list
                            if i in kwargs['hash_list']:
                                # Append hashtag and date
                                hashtags_and_dates.append( (i, h[0]) )
                    elif len(ht) == 1:
                        if ht[0] in kwargs['hash_list']:
                            # Append hashtag and date
                            hashtags_and_dates.append( (ht[0], h[0]) )
        elif kwargs['search_option'] == 'tweets_and_hashtags':
            # 1. Search and list hashtags
            df_hash_data = clean_hash_data_filtered[[kwargs['date_col'], kwargs['hash_col'], kwargs['id_col']]]
            hashtags_dates_tweetid = accumulator('hashtags', df_hash_data.values.tolist(), kwargs['hash_list'])
            
            # 2. Search and list keywords; Also filters out tweets already accounted by the hashtag_list
            df_kw_data = kwargs['df_corpus'][ [kwargs['date_col'], kwargs['hash_col'], kwargs['tweet_col'], kwargs['id_col'] ]]
            kwhts_dates_tweetid = accumulator('keywords', df_kw_data.values.tolist(), kwargs['keyword_list'])
            
            # 3. Merge Lists and filter out unecessary items
            merged_list = hashtags_dates_tweetid + kwhts_dates_tweetid
            for m in merged_list:
                merged_hashtags_and_dates.append((m[0], m[1]))
        
        hashtag_date_totals = list(Counter(merged_hashtags_and_dates).items())
        
        print('Writing up the sample')
        top_date_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            df=hashtag_date_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )

        print('Grouping the sample based on the', kwargs['time_agg_type'], 'option.')
        
        grouped_top_date_x = {}
        if kwargs['time_agg_type'] == 'period':
            grouped_top_date_x = grouper(
                listed_tuples=top_date_x,
                group_type=kwargs['time_agg_type'],
                skeleton=kwargs['skeleton'],
                period_dates=kwargs['period_dates']
            )
        elif kwargs['time_agg_type'] == 'period_day':
            grouped_top_date_x = grouper(
                listed_tuples=top_date_x,
                group_type=kwargs['time_agg_type'],
                skeleton=kwargs['skeleton']
            )
            
        print('\n\nConverting data to a DataFrame.')
        
        df_grouped_top_date_x = grouped_dict_to_df(
            sum_option=kwargs['sum_option'],
            time_agg_type=kwargs['time_agg_type'],
            group_dict=grouped_top_date_x,
            output_type=kwargs['output_type']
        )

        print('\n\nSample hydration complete!')
        return df_grouped_top_date_x

##################################################################

## PLOTTER FUNCTIONS

##################################################################

'''
    bar_plotter: Plot the desired column sums as a bar chart
    -- Args:
        ax=None # Resets the chart
        counter = List of tuples returned from match_maker(),
        path = String of desired path to directory,
        output = String value of desired file name (.png)
    - Returns: Nothing

'''
def bar_plotter(**kwargs):
    if kwargs['ax'] is None:
        fig = plt.figure()
        kwargs['ax'] = fig.add_subplot(111)

    frequencies = []
    names = []
    # [(('#buildthewall', '2019-03-14'), 1),
        # (('#buildthewall', '2019-02-28'), 30),
        # (('#buildthewall', '2019-02-27'), 80), ... ]
    for c in kwargs['counter']:
        frequencies.append(c[1])
        names.append(c[0])

    N = len(names)
    x_coordinates = np.arange(len(kwargs['counter']))
    kwargs['ax'].bar(x_coordinates, frequencies, align='center')

    kwargs['ax'].xaxis.set_major_locator(plt.FixedLocator(x_coordinates))
    kwargs['ax'].xaxis.set_major_formatter(plt.FixedFormatter(names))

    plt.xticks(range(N)) # add loads of ticks
    plt.xticks(rotation='vertical')

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = kwargs['margin'] # inch margin
    s = maxsize/plt.gcf().dpi*N+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(bottom=-0.15)
    plt.savefig(join(kwargs['path'], kwargs['output']))
    print('File ', kwargs['output'], ' saved to ', kwargs['path'])
    plt.show()

'''
    temporal_bar_plotter: Plot the desired column sums as a temporal bar chart
    -- Args:
        ax=None # Resets the chart
        counter = List of tuples returned from match_maker()
        title= String. Title of the chart.
        margin= Float in inches for adjusting margin
        subplot_adj_bottom= Float in inches for adjusting bottom margin issues
        path = String of desired path to directory
        output = String value of desired file name (.png)
    - Returns: Nothing.
'''
def temporal_bar_plotter(**kwargs):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
    frequencies = []
    names = []
    dates = kwargs['date_range']

    for c in kwargs['counter']:
        for d in dates:
            if  d == c[0]:
                frequencies.append(c[1])
                names.append( c[0]+':  '+str(c[1]) )
                
    N = len(names)
    x_coordinates = np.arange(N) #changed from counter
    ax.bar(x_coordinates, frequencies, align='center')

    ax.xaxis.set_major_locator(plt.FixedLocator(x_coordinates))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(names))
    
    plt.xticks(range(N)) # add loads of ticks
    plt.xticks(rotation='vertical')

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = kwargs['margin'] # inch margin
    s = maxsize/plt.gcf().dpi*N+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])
    
    # Tweak spacing to prevent clipping of tick-labels
    plt.title(kwargs['title'], fontdict=None, loc='center', pad=None)
    plt.subplots_adjust(bottom=kwargs['subplot_adj_bottom'])
    plt.savefig(join(kwargs['path'], kwargs['output']))
    print('File ', kwargs['output'], ' saved to ', kwargs['path'])
    plt.show()

'''
    multiline_plotter: Plots and saves a small-multiples line chart from a returned DataFrame from a summarizer function that used the 'python' option
    - Modified src: https://python-graph-gallery.com/125-small-multiples-for-line-chart/
    - Args:
        - style= String. See matplot docs for options available, e.g. 'seaborn-darkgrid' 
        - pallette= String. See matplot docs for options available, e.g. 'Set1'
        - graph_option= String. Current options for sampling include the following:
            - 'single_hash_per_day': Sum of single hashtag per Day in provided range
            - 'group_hash_per_day': Sum of group of hashtags per Day in provided range
            - 'single_hash_per_period': Sum of single hashtag per Period
            - 'group_hash_per_period': Sum of group of hashtags per Period
        - df= DataFrame of data set to be visualized
        - x_col= DataFrame column for x-axis
        - multi_x= Integer for number of graphs along x/rows
        - multi_y= Integer for number of graphs along y/columns
            - NOTE: Only supports 3x3 right now.
        - linewidth= Float. Line width level.
        - alpha= Float (0-1). Opacity level of lines
        - chart_title= String. Title for the overall chart
        - x_title= String. Label for x axis
        - y_title= String. Label for y axis
        - path= String. Path to save figure
        - output= String. Filename for figure.
    - Returns nothing, but plots a 'small multiples' series of charts
'''
def multiline_plotter(**kwargs):
    if kwargs['graph_option'] == 'group_hash_per_period':
        # Initialize the use of a stylesheet
        # See docs for options, e.g., 'dark_background'
        plt.style.use(kwargs['style'])

        # Create a color palette
        # See docs for options, e.g., 'Set1' or 'Paired'
        palette = plt.get_cmap(kwargs['palette'])

        # Create a figure and a grid of subplots
        fig, axs = plt.subplots(nrows=kwargs['multi_x'], ncols=kwargs['multi_y'])

        # counter will store the feature index 
        # to use when highlighting a particular 
        # variable in each subplot
        counter = 0

        # Traverse each individual subplot within the 3x3 grid
        # Note: This code subsets each subplot via axs[row, col]
        for row in range(axs.shape[0]):
            for col in range(axs.shape[1]):
                # Plot every feature in each subplot as a white line
                for feature in kwargs['df'].drop(kwargs['x_col'], axis=1).columns:
                    axs[row, col].plot(kwargs['df'][kwargs['x_col']],
                                   kwargs['df'][feature],
                                   marker="",
                                   color="white", 
                                   linewidth=0.6,
                                   alpha=0.3)
                # For each subplot, plot only one non-"period" feature 
                # via counter and in color
                # Note: counter is input directly inside of palette()
                axs[row, col].plot(kwargs['df'][kwargs['x_col']],
                                   kwargs['df'].drop(kwargs['x_col'], axis=1).iloc[:, counter],
                                   marker="",
                                   color=palette(counter), 
                                   linewidth=2.4,
                                   alpha=0.9)
                
                # Set xlim and ylim for each subplot
                # Define ranges based on data set values
                x_max = math.ceil(max(kwargs['df'].iloc[:, :1].copy().max().values.tolist()))
                x_min = math.floor(min(kwargs['df'].iloc[:, :1].copy().min().values.tolist()))
                y_max = math.ceil(max(kwargs['df'].iloc[:, 1:-1].copy().max().values.tolist()))
                y_min = math.floor(min(kwargs['df'].iloc[:, 1:-1].copy().min().values.tolist()))
                axs[row, col].set_xlim(x_min,x_max)
                axs[row, col].set_ylim(y_min,y_max)

                # Remove x-axis tick marks from the first two rows of subplots
                # TODO: Revise to be modular, based on grid definition besides 3x3
                if row in [0, 1]:
                    axs[row, col].tick_params(labelbottom=False)
                # Remove the y-axis tick marks from the second and third 
                # columns of subplots
                if col in [1, 2]:
                    axs[row, col].tick_params(labelleft=False)          

                # Assign each subplot a title based on the one non-"period" 
                # feature that was highlighted in color
                axs[row, col].set_title(kwargs['df'].drop(kwargs['x_col'], axis=1).iloc[:, counter].name, 
                                        loc="left", 
                                        fontsize=12, 
                                        fontweight=0, 
                                        color=palette(counter))

                # Subplot complete, so increment counter
                # so the next column variable is highlighted
                counter += 1

        # Assign overall title
        fig.suptitle(kwargs['chart_title'], 
                     fontsize=13, 
                     fontweight=0,
                     color="white", 
                     style="italic", 
                     y=1.02)

        # Label axes
        fig.text(0.5, 0.01, kwargs['x_title'], ha="center", va="center")
        fig.text(0.01, 0.5, kwargs['y_title'], ha="center", va="center", rotation='vertical')

        # Unsquish layout
        fig.tight_layout()

        # Export figure as PNG file
        fig.savefig(
            join(kwargs['path'], kwargs['output']),
            dpi=200,
            bbox_inches="tight")
        print('File ', kwargs['output'], ' saved to ', kwargs['path'])
        plt.show()
