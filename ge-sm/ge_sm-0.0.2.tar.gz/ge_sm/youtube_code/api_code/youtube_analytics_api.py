from oauth2client import client, file, tools
from apiclient.discovery import build
import httplib2
from pathlib import Path

# put in path name for secrets et al as running from batch file
########################
pathname = Path(__file__).parent.parent.parent
########################

class YoutubeAnalyticsAPI:
    """Create a youtube analytics session using oauth2 flow
    by abstracting this away makes it easier to change the oauth2 flow in the future"""
    def __init__(self, scopes = ['https://www.googleapis.com/auth/yt-analytics.readonly'],
                 secrets_path = pathname / 'youtube_code/api_code/youtube_secrets_details.json',
                 analyticsdat = 'YTanalytics.dat'):
        self.scopes = scopes
        self.secrets_path = secrets_path
        self.initialize_analyticsreporting(analyticsdat)

    def __repr__(self):
        return f'{self.__class__.__name__}(scopes="{self.scopes}"", secrets_path="{self.secrets_path}"'


    def initialize_analyticsreporting(self, analyticsdat):
        # Parse command-line arguments.
        args = tools.argparser.parse_args()
        # Set up a Flow object to be used if we need to authenticate.
        flow = client.flow_from_clientsecrets(self.secrets_path, scope = ' '.join(self.scopes),
                                              message=tools.message_if_missing(self.secrets_path))
        storage = file.Storage(pathname / analyticsdat)
        credentials = storage.get()
        if credentials is None or credentials.invalid: credentials = tools.run_flow(flow, storage, args)
        http = credentials.authorize(httplib2.Http())
        self.analytics = build('youtubeAnalytics', 'v2', http = http)

class YoutubeAPI:
    """Create a youtube analytics session using oauth2 flow
    by abstracting this away makes it easier to change the oauth2 flow in the future"""
    def __init__(self, scopes = ['https://www.googleapis.com/auth/youtube.readonly',
                                 'https://www.googleapis.com/auth/yt-analytics.readonly'],
                 secrets_path = pathname / 'youtube_code/api_code/youtube_secrets_details.json',
                 youtubedat = 'youtubedat.dat'):
        self.scopes = scopes
        self.secrets_path = secrets_path
        self.initialize_apireporting(youtubedat)

    def __repr__(self):
        return f'{self.__class__.__name__}(scopes="{self.scopes}"", secrets_path="{self.secrets_path}"'

    def initialize_apireporting(self, youtubedat):
        # Parse command-line arguments.
        args = tools.argparser.parse_args()
        # Set up a Flow object to be used if we need to authenticate.
        flow = client.flow_from_clientsecrets(self.secrets_path, scope = ' '.join(self.scopes),
                                              message=tools.message_if_missing(self.secrets_path))
        storage = file.Storage(pathname / youtubedat)
        credentials = storage.get()
        if credentials is None or credentials.invalid: credentials = tools.run_flow(flow, storage, args)
        http = credentials.authorize(httplib2.Http())
        self.reports = build('youtube', 'v3', http = http)


