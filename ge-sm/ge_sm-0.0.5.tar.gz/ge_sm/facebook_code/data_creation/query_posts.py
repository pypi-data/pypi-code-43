import pandas as pd
import logging

#from common.logger import write_to_log
from ge_sm.facebook_code.api_code.facebook_API import FaceBookPostData
from ge_sm.facebook_code.settings.chaa_jaa_settings import pg_info, post_output_details as po

log = logging.getLogger('facebook_api_log')

def get_post_insights(fb, post_iterator, post_metrics, post_metrics_split) -> pd.DataFrame:
    '''use post connection and attributes methods, yields total shares, reactions and comments
    plus insights for a laugh :)'''

    post_metrics_str = ','.join(post_metrics)
    all_insights = []
    for post in post_iterator:
        #get all post connections / attributes, post metrics
        fb.query_post_connections(post['id'])
        fb.query_post_attributes(post['id'])
        fb.query_post_insights(post['id'], metrics = post_metrics_str)

        # construct basic post dictionary
        d = {'postId': post['id'],
             'created_time': post['created_time'],
             'message' : None,
             'permalink_url': post['permalink_url'],
             'vid_duration': 0,
             #'comments': None,
             'total_reactions': 0,
             'total_shares': 0,
             'total_comments': 0}

        # TODO should log empty values
        if fb.post_connections.get('message') is not None:
            d['message'] = fb.post_connections['message']
        #Find video length
        if 'properties' in post:
            for p in post['properties']:
                if p['name'] == 'Length': d['vid_duration'] =  p['text']

        #now do insights
        #set default value up here
        for m in post_metrics:
            d[m] = 0
        #so now only will overwrite missing ones!
        for p in fb.post_insights['data']:
            #get value for the metric
            result = p['values'][0]['value']
            # sort out rubbish dictionary output, i.e. if it one of the dictionaries...
            if p['name'] in post_metrics_split:
                #get details
                met_list = post_metrics_split[p['name']]
                #go over all possible split values for this metric
                #if in metric value then set output to be this, else set to 0
                for t in met_list:
                    d[p['name'] + '_' + t] = 0
                    if t in result: d[p['name'] + '_' + t] = result[t]
            else:
                d[p['name']] = result

        #append data as list of dictionaries for data framw
        all_insights.append(d)
    return pd.DataFrame(all_insights)

#@write_to_log
def construct_post_data(stdt, eddt):

    # get all posts for all pages in this date range
    #Get fb post object
    fb_post_obj = FaceBookPostData(pagetoken = pg_info['access_token'], page = pg_info['pageId'])
    #call method to get all post ids / dates
    fb_post_obj.query_all_posts(since = stdt, until = eddt)
    # this is a list of dictionarys, date then post_id
    post_iterator = fb_post_obj.posts

    #sort out metrics from imported page details
    pm_list = []; post_metrics_order = []; pm_split = {}; post_metrics_names = []
    for p, q in po.items():
        #get GE names and order
        post_metrics_names.append(p)
        #if a metric / split metric add to post_metrics
        if q[2] !=None: pm_list.append(q[0])
        #If a split metric then add to list of splits / add new split metric
        if q[2] != 'Metric' and q[2] != None:
            post_metrics_order.append(q[0] + '_' + q[2])
            if q[0] in pm_split:
                pm_split[q[0]].append(q[2])
            else:
                pm_split[q[0]] = [q[2]]
        else:
            post_metrics_order.append(q[0])

    df_post_insights = get_post_insights(fb_post_obj, post_iterator, pm_list, pm_split)
    #add in pageid and page name
    df_post_insights['pageId'] = pg_info['pageId']
    df_post_insights['pageName'] = pg_info['facebookPageName']
    df_post_insights['date'] = pd.to_datetime(df_post_insights['created_time'].str.slice(0, 10), format='%Y-%m-%d',
                                      errors='coerce')
    #this was in milliseconds
    df_post_insights['post_video_avg_time_watched'] = df_post_insights['post_video_avg_time_watched'] / 1000
    df_post_insights['post_activity'] = df_post_insights['post_activity_by_action_type_like'] + \
                                        df_post_insights['post_activity_by_action_type_comment'] + \
                                        df_post_insights['post_activity_by_action_type_share']
    df_post_insights['post_engagements'] = df_post_insights['post_activity'] + df_post_insights['post_clicks']
    df_post_insights = df_post_insights[post_metrics_order]
    df_post_insights.columns = post_metrics_names
    post_metrics_names.remove('Post release date')
    #get rid of long post name
    df_post_insights['Post name'] = df_post_insights['Post name'].str.slice(0, 255)
    return df_post_insights[post_metrics_names]

