import pandas as pd
import logging

from ge_sm.facebook_code.api_code.facebook_API import FaceBookPageData
#from common.logger import write_to_log
from ge_sm.facebook_code.settings.chaa_jaa_settings import pg_info, page_output_details as po, demo_groups


log = logging.getLogger('facebook_api_log')

#@write_to_log
def get_page_insights(fb, page_metrics, page_metrics_splits, sd, ed, period) -> pd.DataFrame:

    # get insights data in similar manner to post
    pg_metrics_str = ','.join(page_metrics)
    fb.query_insights(metrics = pg_metrics_str, since = sd, until = ed, period = period)
    all_insights = []
    date_len = len(fb.insight_data['data'][0]['values'])
    #loop over all elements in date range
    for i in range(date_len):
        d = {}
        for m in page_metrics:
            d[m] = 0
        data = fb.insight_data['data']
        for p in data:
            d['end_time'] = p['values'][i]['end_time']
            result = p['values'][i]['value']
            # sort out rubbish dictionary output, i.e. if it one of the dictionaries...
            if p['name'] in page_metrics_splits:
                # get details
                met_list = page_metrics_splits[p['name']]
                # go over all possible split values for this metric
                # if in metric value then set output to be this, else set to 0
                for t in met_list:
                    d[p['name'] + '_' + t] = 0
                    if t in result: d[p['name'] + '_' + t] = result[t]
            else:
                d[p['name']] = result
        # append data as list of dictionaries for data frame
        all_insights.append(d)
    return pd.DataFrame(all_insights)

#@write_to_log
def construct_insight_data(stdate, eddate, period): #mnth: int = None, yr: int = None):

    #sort out metrics from imported page details
    #see post comments for more info here
    pm_list = []; page_metrics_order = []; pm_split = {}; page_metrics_names = []
    for p, q in po.items():
        #get GE names and order
        page_metrics_names.append(p)
        #if a metric / split metric add to post_metrics
        if q[2] !=None: pm_list.append(q[0])
        #If a split metric then add to list of splits / add new split metric
        if q[2] != 'Metric' and q[2] != None:
            page_metrics_order.append(q[0] + '_' + q[2])
            if q[0] in pm_split:
                pm_split[q[0]].append(q[2])
            else:
                pm_split[q[0]] = [q[2]]
        else:
            page_metrics_order.append(q[0])
    fb_page_obj = FaceBookPageData(pagetoken = pg_info['access_token'], page = pg_info['pageId'])
    df_page_insights = get_page_insights(fb_page_obj, pm_list, pm_split, stdate, eddate, period)

    # print(df_page_insights.tail().to_string())
    #add in pageid and page name
    df_page_insights['pageId'] = pg_info['pageId']
    df_page_insights['pageName'] = pg_info['facebookPageName']
    df_page_insights['date'] = pd.to_datetime(df_page_insights['end_time'].str.slice(0, 10), format='%Y-%m-%d',
                                      errors='coerce') - pd.Timedelta('1 day')
    #do various page metric calcs
    df_page_insights['Perc reach organic'] = \
        df_page_insights['page_impressions_organic_unique'] / df_page_insights['page_impressions_unique']
    df_page_insights['Perc reach viral'] = \
        df_page_insights['page_impressions_viral_unique'] / df_page_insights['page_impressions_unique']
    df_page_insights['Perc reach paid']  = \
        df_page_insights['page_impressions_paid_unique'] / df_page_insights['page_impressions_unique']
    df_page_insights['Engagement_rate'] = \
        df_page_insights['page_consumptions_unique'] / df_page_insights['page_impressions_unique']
    df_page_insights['Net_Likes'] = \
        df_page_insights['page_fan_adds_unique'] - df_page_insights['page_fan_removes_unique']
    df_page_insights = df_page_insights[page_metrics_order]
    df_page_insights.columns = page_metrics_names
    return df_page_insights


def get_fb_demo_data(sd, ed, period = 'day'): #mnth: int = None, yr: int = None):
    """queries page level data for the current month"""
    #Use dictionary of possible demos
    fb = FaceBookPageData(pagetoken = pg_info['access_token'], page = pg_info['pageId'])
    demo_mets = ['page_impressions_by_age_gender_unique']
    fb.query_insights(metrics=demo_mets, since = sd, until = ed, period = period)


    demo_data = fb.insight_data['data'][0]['values']

    demo_list = []
    #Loop over all values for dataframe
    for d in demo_data:
        dg_dict = d['value']
        end_time = d['end_time']
        # go over all demo groups
        for dg_key, dg_item in demo_groups.items():
            pd_dict = {}
            pd_dict['end_time'] = end_time
            pd_dict['Page name'] = pg_info['facebookPageName']
             # set gender / age group to be zero for each
            pd_dict['Gender'] = dg_item[0]
            pd_dict['Age'] = dg_item[1]
            pd_dict['Impressions'] = 0
            # if this key in fb dictionary, then set value
            if dg_key in dg_dict:
                pd_dict['Impressions'] = dg_dict[dg_key]
                # add to dictionary
            demo_list.append(pd_dict)
    df_demos = pd.DataFrame(demo_list)
    df_demos['Date'] = pd.to_datetime(df_demos['end_time'].str.slice(0, 10), format='%Y-%m-%d',
                                      errors='coerce') - pd.Timedelta('1 day')
    #print(df_demos.to_string())
    df_order = ['Date', 'Page name', 'Gender', 'Age', 'Impressions']
    return df_demos[df_order]


if __name__ == '__main__':

    # to load historic data
    populate_historic()




