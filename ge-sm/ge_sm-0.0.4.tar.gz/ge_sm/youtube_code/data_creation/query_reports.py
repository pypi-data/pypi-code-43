import pandas as pd

from ge_sm.youtube_code.settings.chaa_jaa_settings import channelsdict, std_metric_details as sm
from ge_sm.youtube_code.api_code.youtube_analytics_api import YoutubeAnalyticsAPI, YoutubeAPI

#Not using this at present
def get_allvideodetails(yt, channel):
    # # Get playlist details
    request_pl = yt.reports.playlists().list(channelId=channel, part='snippet').execute()
    playlists_ids = [i['id'] for i in request_pl['items']]
    # have two lists to deal with possible duplication of video id
    all_videos = []; all_video_ids = []
    for pl in playlists_ids:
        request = yt.reports.playlistItems().list(part = 'snippet, contentDetails', playlistId = pl).execute()
        for i in request['items']:
            v = i['snippet']
            video_pub = v['publishedAt']
            video_title = v['title']
            video_id = v['resourceId']['videoId']
            #add playlst id here
            video_pl = pl
            # deal with duplicate video ids here
            if video_id not in all_video_ids:
                all_videos.append([video_id, video_title,'https://youtu.com/embed/' + video_id, video_pub, video_pl])
                all_video_ids.append(video_id)
    return(all_videos)

def get_report(yta, channel, startdate, enddate, metrics, dimensions, *filter):
    """performs the request to get analytics data according to dims and metrics"""
    request = {'ids': channel, 'startDate': startdate, 'endDate': enddate,'maxResults': '200', 'dimensions': dimensions,
               'metrics': metrics}
    if len(filter) > 0:
        #add sort or similar from the filter parameter, note it is the first element of tuple is key, second value
        request[filter[0][0]] = filter[0][1]
    return yta.analytics.reports().query(**request).execute()

def run_video_report(sd, ed):
    """sd start date, ed enddate"""
    metrics_list = []; metrics_order = []; metrics_names = []
    for p, q in sm.items():
        #get GE names and order
        metrics_names.append(p)
        metrics_order.append(q[0])
        #if a metric / split metric add to post_metrics
        if q[2] !=None: metrics_list.append(q[0])
    stdmetrics = ','.join(metrics_list)
    # hold video details as list of data frames
    df_videos = None
    #loop over each channel
    for id in channelsdict:
        channel = channelsdict[id]
        #get name of anlaytics.dat file for this channel
        yta_dat = channel['analyticsdat']
        yt_dat = channel['youtubedat']
        yt = YoutubeAPI(youtubedat = yt_dat)
        yta = YoutubeAnalyticsAPI(analyticsdat = yta_dat)
        data_list = []
        #playlists = get_allplaylists(yt, id)
        #get all videos plus the names, id, urls
        vid_details = get_allvideodetails(yt, id)
        #get video names
        # have to dael with possible video id duplication
        df_vidnames = pd.DataFrame([{'playList': v[4], 'video': v[0], 'videoname': v[1], 'videourl': v[2], 'videopub': v[3]} for v in vid_details])
        # get api data for each channel
        resp = get_report(yta,'channel==' + id, sd, ed, 'estimatedMinutesWatched,' + stdmetrics,
        'video', ('sort','-estimatedMinutesWatched'))
        # get column headers and data
        col_headers = [d['name'] for d in resp['columnHeaders']]
        data = resp['rows']
        # loop over all data, and zip correct head to metrics value
        for d in data:
            x = (dict(zip(col_headers, d)))
            x['ChName'] = channel['name'] # name and id of channel for output
            x['ChId'] = id
            #append to data list
            data_list.append(x)
        # set dictionary values to be dataframe
        df = pd.DataFrame(data_list)
        #merge in with video names
        df = pd.merge(df, df_vidnames, how='inner', on='video')
        #add to existing dataframe
        if df_videos is None:
            df_videos = df
        else:
            df_videos = df_videos.append(df, sort=True)
            df_videos.reset_index(drop=True, inplace=True)

    #do subscriber calculation
    df_videos['subscribers'] = df_videos['subscribersGained'] - df_videos['subscribersLost']
    df_videos['watchtime'] = df_videos['views'] * df_videos['averageViewDuration'] / 60
    #sort out column headers
    df_videos = df_videos[['ChName', 'ChId', 'playList', 'video', 'videoname', 'videourl', 'videopub', 'estimatedMinutesWatched'] + metrics_order]
    #convert vid published into something sensible
    df_videos['videopub'] = pd.to_datetime(df_videos['videopub'].str.slice(0, 10), format='%Y-%m-%d',
                   errors='coerce')
    df_videos.columns = ['Channel name', 'Channel ID', 'PlayList', 'Video Id', 'Video name', 'Url', 'Date published', 'Est Minutes Watched'] + metrics_names
    return(df_videos)
#
def run_channel_report(sd, ed):
    """sd start date, ed enddate"""
    metrics_list = []; metrics_order = []; metrics_names = []
    for p, q in sm.items():
        #get GE names and order
        metrics_names.append(p)
        metrics_order.append(q[0])
        #if a metric / split metric add to post_metrics
        if q[2] !=None: metrics_list.append(q[0])
    stdmetrics = ','.join(metrics_list)

    df_channels = None
    #loop over each channel
    for id in channelsdict:
        channel = channelsdict[id]
        #get name of anlaytics.dat file for this channel
        ytadat = channel['analyticsdat']
        yta = YoutubeAnalyticsAPI(analyticsdat = ytadat)
        resp = get_report(yta, 'channel==' + id, sd, ed, stdmetrics, 'day')
        data_list = []
        # break down response object into parts that are required
        col_headers = [d['name'] for d in resp['columnHeaders']]
        data = resp['rows']
        for d in data:
            x = (dict(zip(col_headers, d)))
            x['ChName'] = channel['name'] # name and id of channel for output
            x['ChId'] = id
            data_list.append(x)
        df = pd.DataFrame(data_list)
        # add to existing dataframe
        if df_channels is None:
            df_channels = df
        else:
            df_channels = df_channels.append(df, sort=True)
            df_channels.reset_index(drop=True, inplace=True)

    # do subscriber calculation
    df_channels['subscribers'] = df_channels['subscribersGained'] - df_channels['subscribersLost']
    df_channels['watchtime'] = df_channels['views'] * df_channels['averageViewDuration'] / 60
    # sort out column headers
    df_channels = df_channels[['day', 'ChName', 'ChId'] + metrics_order]
    df_channels.columns = ['Date', 'Channel name','Channel ID'] + metrics_names
    return(df_channels)

def run_demo_report(sd, ed):
    """sd start date, ed enddate"""
    # hold video details as list of data frames
    df_demos = None
    #loop over each channel
    for id in channelsdict:
        channel = channelsdict[id]
        #get name of anlaytics.dat file for this channel
        ytadat = channel['analyticsdat']
        yta = YoutubeAnalyticsAPI(analyticsdat=ytadat)
        data_list = []
        # get api data for each channel
        resp = get_report(yta,'channel==' + id, sd, ed, 'viewerPercentage',
        'ageGroup,gender', ('sort','ageGroup,gender'))
        # get column headers and data
        col_headers = [d['name'] for d in resp['columnHeaders']]
        data = resp['rows']
        # loop over all data, and zip correct head to metrics value
        for d in data:
            x = (dict(zip(col_headers, d)))
            x['ChName'] = channel['name'] # name and id of channel for output
            x['ChId'] = id
            x['Date'] = sd
            #append to data list
            data_list.append(x)
        # set dictionary values to be dataframe
        df = pd.DataFrame(data_list)
        #add to existing dataframe
        if df_demos is None:
            df_demos = df
        else:
            df_demos = df_demos.append(df, sort=True)
            df_demos.reset_index(drop=True, inplace=True)
    #sort ouf month here for date
    df_demos['Date'] = pd.to_datetime(df_demos['Date'].str.slice(0, 10), format='%Y-%m',
                   errors='coerce')
    #sort out column headers
    df_demos = df_demos[['Date', 'ChName', 'ChId', 'gender', 'ageGroup', 'viewerPercentage']]
    return(df_demos)


