import pandas as pd
import datetime

from ge_sm.google_analytics_code.settings.chaa_jaa_settings import chaajaauser
from ge_sm.google_analytics_code.api_code.google_analytics_api import GoogleAnalyticsAPI
from ge_sm.common.helper_funcs import ga_dim_met_create

def get_report(ga, dimensions, viewid, startdate, enddate, metrics, *orders):
    request = dict(viewId=viewid, pageSize=100000, dateRanges={'startDate': startdate, 'endDate': enddate},
                   dimensions=dimensions, metrics=metrics)
    if len(orders) > 0:
        request['orderBys'] = orders[0][0]
    r = ga.analytics.reports().batchGet(body={'reportRequests': request}).execute()
    return r

def construct_user_report(stdate, eddate, rpttype):

    # Get GA API
    ga = GoogleAnalyticsAPI()
    df_dict = {}
    view = chaajaauser['view']; viewid = chaajaauser['viewId'] #; pgfilter = chaajaauser['pgfilter']
    cjdict = chaajaauser[rpttype]['dimdict']
    metnames = []; mets = []
    # get metric details
    for m_key, m_val in chaajaauser[rpttype]['mets'].items():
        metnames.append(m_key)
        mets.append(m_val)
    # Loop over all dimensions in dimension list and form data frame for each different metric
    for rpt_name, dimdict in cjdict.items():
        dimnames = []; dims = []
        for d_key, d_val in dimdict.items():
            dimnames.append(d_key)
            dims.append(d_val)
        # turn into pairs of dimensions / metrics
        dimensions, metrics = ga_dim_met_create(dims, mets)
        #list of data to turn into dataframe
        data_list = []
        # get report from GA
        resp = get_report(ga, dimensions, viewid, stdate, eddate, metrics) #, pgfilter) # Note additional sorting thing for page views
        # break down response object into parts that are required
        metric_headers = resp['reports'][0]['columnHeader']['metricHeader']['metricHeaderEntries']  # list of metrics
        dim_headers = resp['reports'][0]['columnHeader']['dimensions']  # columns dimensions
        data = resp['reports'][0]['data']['rows']
        for d in data:
            # zip takes iteration and returns pairs, which can then be make key / value in dictionary
            x = dict(zip(dim_headers, d['dimensions']))
            y = dict(zip([d['name'] for d in metric_headers], d['metrics'][0]['values']))
            y['view'] = view
            y['viewid'] = viewid
            data_list.append({**x, **y})
        # set dictionary value to be dataframe
        df_ga_user = pd.DataFrame(data_list)
        # print(rpt_name, dimdict, df_ga_user.head().to_string())
        # sort out names and order of columns
        df_ga_user = df_ga_user[['ga:' + d for d in dims] + ['ga:' + m for m in mets]]
        df_ga_user.columns = dimnames + metnames
        # strip down pages if required
        if rpttype == 'pages':
            df_ga_user['Page Path'] = df_ga_user['Page Path'].str.slice(0, 255)
            df_ga_user['Page Title'] = df_ga_user['Page Title'].str.slice(0, 255)
        if rpttype == 'events':
            df_ga_user['Event Label'] = df_ga_user['Event Label'].str.slice(0, 255)

        # Convert kadence id to numeric if there at all
        if 'KadenceId' in df_ga_user.columns:
            # Get rid of alex and agnes test kadence ids
            df_ga_user = df_ga_user[(df_ga_user['KadenceId'] !='alextest') &
                                    (df_ga_user['KadenceId'] !='agnestest')]
            df_ga_user['KadenceId'] = df_ga_user['KadenceId'].astype(str).str.\
                slice(0, 6, 1).astype('int64')
        df_dict[rpt_name] = df_ga_user

    return df_dict

def make_signedup_df(df_client_pg, df_wagtail_pg, df_client_ur, df_kdids):

    # just get individual dim 1 and 2 for client and kadence ids
    # get the various

    # get unique kadence ids for pages
    df_client_list_pg = df_client_pg.drop_duplicates(subset = 'KadenceId', keep = 'first')
    df_client_list_pg = df_client_list_pg[['KadenceId', 'ClientId']]

    # get unique wagtail ids for pages
    df_wagtail_list_pg = df_wagtail_pg.drop_duplicates(subset = 'KadenceId', keep = 'first')
    df_wagtail_list_pg = df_wagtail_list_pg[['KadenceId', 'WagtailId']]

    # get video events
    df_client_list_ur = df_client_ur[['KadenceId', 'Event Label']][(df_client_ur['Event Category'] == 'Video Interactions')]
    # get unique video titles
    df_client_list_ur = df_client_list_ur.drop_duplicates()
    # count number unique videos seen
    df_client_list_ur = df_client_list_ur[['KadenceId', 'Event Label']].groupby('KadenceId', as_index=False).count()
    df_client_list_ur.columns = ['KadenceId', 'Unique Video Count']
    print(df_client_list_ur.to_string())

    # # Merge both in outer join with kadence id files
    df_match = pd.merge(df_kdids, df_client_list_pg, how = 'left', on = 'KadenceId')

    df_match = pd.merge(df_match, df_wagtail_list_pg, how = 'left', on = 'KadenceId')

    # add in video count
    df_match = pd.merge(df_match, df_client_list_ur, how = 'left', on = 'KadenceId')

    #add in date analysis was run
    df_match['Date'] = pd.to_datetime(datetime.date.today(), format='%Y-%m-%d')
    return df_match[['Date', 'KadenceId', 'WagtailId', 'ClientId', 'Unique Video Count']]



if __name__ == '__main__':
    # print(settings)
    report_control()