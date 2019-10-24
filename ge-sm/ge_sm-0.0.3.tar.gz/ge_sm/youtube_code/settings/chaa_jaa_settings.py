import json
from pathlib import Path
from ge_sm.common.secrets import *


channelsdict = {
	os.environ.get('YT_CHANNEL', ''): {
		'name': 'Chajaa',
		'analyticsdat': 'analytics_CJ.dat',
		'playlist': os.environ.get('YT_PLAYLIST', ''),
		'youtubedat': 'youtube_CJdat.dat'
	}
}

#Metric details
std_metric_details = {'Views': ['views','1a','Metric'],
'Watch time':['watchtime',1,None], ## views * avg view time
'Avg view duration':['averageViewDuration',1,'Metric'],
'Avg view percentage':['averageViewPercentage',2,'Metric'],
'Comments':['comments',3,'Metric'],
'Likes':['likes',4,'Metric'],
'Dislikes':['dislikes',5,'Metric'],
'Shares':['shares',6,'Metric'],
'Subscribers':['subscribers',7, None], ## subs gained - subs lost
'Subscribers gained':['subscribersGained',7,'Metric'], 
'Subscribers lost':['subscribersLost',8,'Metric'], 
'Annotation Clicks':['annotationClicks',9,'Metric'], 
'Annotation clickable impressions':['annotationClickableImpressions',10,'Metric'],
'Annotation click through rate':['annotationClickThroughRate',11,'Metric']}

vid_details = [('ChName','Channel name'), ('ChId', 'Channel ID'), ('video', 'Video Id'), 
('videoname','Video name'), ('videourl', 'URL'), ('videopub','Date published'), ('estimatedMinutesWatched', 'Est Minutes Watched')]


secrets = {
	"installed": {
		"client_id": os.environ.get('YT_CLIENT_ID', ''),
		"project_id": os.environ.get('YT_PROJECT_ID', ''),
		"auth_uri": "https://accounts.google.com/o/oauth2/auth",
		"token_uri": "https://oauth2.googleapis.com/token",
		"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
		"client_secret": os.environ.get('YT_CLIENT_SECRET', ''),
		"redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
	}
}


pathname = Path(__file__).parent.parent.parent
with open(pathname / 'youtube_code/api_code/youtube_secrets_details.json', 'w') as f:
	f.write(json.dumps(secrets))
	f.close()
