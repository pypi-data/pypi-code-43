import argparse
from oauth2client import client, file, tools
from googleapiclient.discovery import build
from httplib2 import Http
from pathlib import Path
# put in path name for secrets et al as running from batch file
########################
pathname = Path(__file__).parent.parent.parent
########################


class GoogleAnalyticsAPI:
    """Create a google analytics session using oauth2 flow
    by abstracting this away makes it easier to change the oauth2 flow in the future"""
    def __init__(self, scopes = ['https://www.googleapis.com/auth/analytics.readonly'],
                 secrets_path = pathname / 'google_analytics_code/api_code/google_analytics_secrets_details.json',
                 discovery_uri = ('https://analyticsreporting.googleapis.com/$discovery/rest')):
        self.scopes = scopes
        self.secrets_path = secrets_path
        self.discovery_uri = discovery_uri
        self.initialize_analyticsreporting()

    def __repr__(self):
        return f'{self.__class__.__name__}(scopes="{self.scopes}"", secrets_path="{self.secrets_path}",' \
               f'discovery_uri="{self.discovery_uri}"'


    def initialize_analyticsreporting(self):
        # Parse command-line arguments.
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         parents=[tools.argparser])
        flags = parser.parse_args([])
        # Set up a Flow object to be used if we need to authenticate.
        flow = client.flow_from_clientsecrets(self.secrets_path, scope=self.scopes,
                                              message=tools.message_if_missing(self.secrets_path))
        storage = file.Storage(pathname + 'analyticsreporting.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(flow, storage, flags)
        self.analytics = build('analytics', 'v4', http=credentials.authorize(http=Http()),
                               discoveryServiceUrl=self.discovery_uri) #PB COMMENT, NOT SURE WHAT LAST LINE MEANS?


if __name__ == '__main__':

    ga = GoogleAnalyticsAPI()
    print(ga)
