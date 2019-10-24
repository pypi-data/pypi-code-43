from ge_sm.common.secrets import *

pg_info = {
    "pageId": os.environ.setdefault('CHAA_JAA_PAGEID', '****'),
    "facebookPageName": os.environ.setdefault('CHAA_JAA_FACEBOOKPAGENAME', '****'),
    "gePageName": os.environ.setdefault('CHAA_JAA_GEPAGENAME', '****'),
    "pageApp": os.environ.setdefault('CHAA_JAA_PAGEAPP', '****'),
    "access_token": os.environ.setdefault('CHAA_JAA_ACCESS_TOKEN', '****')
}

page_output_details = {'Date': ['date','1a',None],
'Page ID':['pageId',1,None],
'Page name':['pageName',2,None],
'Total reach':['page_impressions_unique',3,'Metric'],
'Paid reach':['page_impressions_paid_unique',4,'Metric'],
'Organic reach':['page_impressions_organic_unique',5,'Metric'],
'Viral reach':['page_impressions_viral_unique',6,'Metric'],
'Perc reach organic':['Perc reach organic',7,None], ## organic reach/  total reach
'Perc reach paid':['Perc reach paid',8,None], ## paid reach/  total reach
'Perc reach viral':['Perc reach viral',9,None], ## viral reach/  total reach
'Total Impressions':['page_impressions',10,'Metric'],
'Paid impressions':['page_impressions_paid',11,'Metric'],
'Organic impressions':['page_impressions_organic',12,'Metric'],
'Viral impressions':['page_impressions_viral',13,'Metric'],
'Total clicks':['page_consumptions',13,'Metric'],
'Unique clicks':['page_consumptions_unique',13,'Metric'],
'Engagement rate: unique clicks/reach':['Engagement_rate',14,None], ## Unique clicks / total reach
'Engaged users':['page_engaged_users',15,'Metric'],
'Page post engagements':['page_post_engagements',16,'Metric'],
'New likes':['page_fan_adds_unique',17,'Metric'],
'Unlikes':['page_fan_removes_unique',18,'Metric'],
'Net likes':['Net_Likes',19,None], ## New likes - Unlikes
'Page likes':['page_positive_feedback_by_type',20,'like'],
'Page shares':['page_positive_feedback_by_type',21,'link'],
'Page comments':['page_positive_feedback_by_type',22,'comment'],
'Page answers':['page_positive_feedback_by_type',22,'answer'],
'Page claims':['page_positive_feedback_by_type',22,'claim'],
'Page rsvps':['page_positive_feedback_by_type',22,'rsvp'],
'Page others':['page_positive_feedback_by_type',22,'other'],
'Total video views':['page_video_views',23,'Metric'],
'Unique video views':['page_video_views_unique',24,'Metric'],
'Total 10s video views':['post_video_views_10s',25,'Metric'],
'Total 30s video views':['page_video_complete_views_30s',26,'Metric']}


demo_groups = {'F.13-17': ['Female','13-17'], 'F.18-24':['Female','18-24'], 'F.25-34':['Female','25-34'], 'F.35-44':['Female','35-44'], 
'F.45-54':['Female','45-54'], 'F.55-64':['Female','55-64'], 'F.65+':['Female','65+'], 
'M.13-17':['Male','13-17'], 'M.18-24':['Male','18-24'], 'M.25-34':['Male','25-34'], 'M.35-44':['Male','35-44'], 
'M.45-54':['Male','45-54'], 'M.55-64':['Male','55-64'], 'M.65+':['Male','65+'], 
'U.13-17':['Male','13-17'], 'U.18-24':['Male','18-24'], 'U.25-34':['Male','25-34'], 'U.35-44':['Male','35-44'], 
'U.45-54':['Male','45-54'], 'U.55-64':['Male','55-64'], 'U.65+':['Male','65+']}


#This is dictionary of post metrics: GE name, FB name, order for dataframe, type:
#:None is field, metric is metric, else is key of dictionary for this metric (when data comes out as dictionary, e.g., post_activity_by_action_type
post_output_details = {'Date': ['date','1a',None],
'Post release date' : ['created_time',1,None],
'Post Id' : ['postId',2,None],
'Page ID' : ['pageId',3,None],
'Page name' : ['pageName',4,None],
'Post name' : ['message',5,None],
'url': ['permalink_url', '5a', None],
'total_comments' : ['total_comments',6,None],
'total_reactions' : ['total_reactions',7,None],
'total_shares' : ['total_shares',8,None],
'Post engagement fan' : ['post_engaged_fan',31, 'Metric'],
'Post engaged users' : ['post_engaged_users',9,'Metric'],
'Total post impressions' : ['post_impressions',10,'Metric'],
'Total post impressions organic': ['post_impressions_organic',11,'Metric'],
'Total post impressions paid': ['post_impressions_paid',13,'Metric'],
'Total post impressions viral' : ['post_impressions_viral',16,'Metric'],
'Total post reach' : ['post_impressions_unique',15,'Metric'],
'Organic reach' : ['post_impressions_organic_unique',12,'Metric'],
'Paid reach' : ['post_impressions_paid_unique',14,'Metric'],
'Viral reach' : ['post_impressions_viral_unique',16,'Metric'],
'Post Engagements' : ['post_engagements',16,None], ## sum of Post clicks and Post reactions, comments, shares
'Negative actions' : ['post_negative_feedback',17,'Metric'],
'Post likes' : ['post_reactions_like_total',18,'Metric'],
'Post loves' : ['post_reactions_love_total',18,'Metric'],
'Post wow' : ['post_reactions_wow_total',18,'Metric'],
'Post haha' : ['post_reactions_haha_total',18,'Metric'],
'Average video view time' : ['post_video_avg_time_watched',19,'Metric'],
'Total video views' : ['post_video_views',20,'Metric'],
'10 second video views' : ['post_video_views_10s',21,'Metric'],
'Unique 10 second video views' : ['post_video_views_10s_unique',22,'Metric'],
'Total unique video views' : ['post_video_views_unique',23,'Metric'],
'Total reactions, comments, shares' : ['post_activity',25,None], ##sum of below
'Post reactions' : ['post_activity_by_action_type',25,'like'],
'Post comments' : ['post_activity_by_action_type',24,'comment'],
'Post shares' : ['post_activity_by_action_type',26,'share'],
'Video duration':['vid_duration',23,None],
'30 second video views' : ['page_video_complete_views_30s',27,'Metric'],
'Unique 30 second video views' : ['page_video_complete_views_30s_unique',28,'Metric'],
'Post clicks' : ['post_clicks',30,'Metric'],
'Post clicks unique' : ['post_clicks_unique',30,'Metric'],
'Post clicks_video' : ['post_clicks_by_type',30,'video play'],
'Post clicks_photo' : ['post_clicks_by_type',30,'photo view'],
'Post clicks_other' : ['post_clicks_by_type',30,'other'],
'Post clicks unique_video' : ['post_clicks_by_type_unique',30,'video play'],
'Post clicks unique_photo' : ['post_clicks_by_type_unique',30,'photo view'],
'Post clicks unique_other' : ['post_clicks_by_type_unique',30,'other']}



