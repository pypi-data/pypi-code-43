import facebook
import logging

from ge_sm.facebook_code.api_code.facebook_secrets import long_access_token

#is this used?
#from common.logger import write_to_log

log = logging.getLogger('facebook_api_log')

class FaceBookAPIConnection:
    """base connection to FB API"""

    def __init__(self, access_token=long_access_token, version="3.1"):
        self.access_token = access_token
        self.version = version
        self.my_account_info = None
        self.graph = facebook.GraphAPI(access_token=self.access_token, version=self.version)

    def __repr__(self):
        return f'{self.__class__.__name__}(access_token="{self.access_token}", version="{self.version}")'

    def get_object(self):
        """get info about 'my' account"""
        self.my_account_info = self.graph.get_object('me/accounts')

class FaceBookPageData(FaceBookAPIConnection):
    """API connection to page related queries"""
    def __init__(self, *, pagetoken=None, page=None):
        super().__init__()
        self.pagetoken = pagetoken
        self.page = page
        self.graph = facebook.GraphAPI(access_token=self.pagetoken, version=self.version)
        self.insight_data = None

    def __repr__(self):
        return f'{self.__class__.__name__}(pagetoken="{self.pagetoken}", page="{self.page}")'


    def query_insights(self, connection_name='insights', metrics=None, since='2019-01-01', until='2019-02-02',
                       period='week'):
        """query insights data - sets a set of default metrics is nothing is passes in"""
        if metrics is None:
            metrics = 'page_fans, page_fan_adds, page_fan_removes, page_impressions_unique, ' \
                      'page_impressions_organic_unique, page_impressions_paid_unique, page_impressions_viral_unique'
        self.insight_data = self.graph.get_connections(id=self.page, connection_name=connection_name, metric=metrics,
                                                       since=since, until=until, period=period)

class FaceBookPostData(FaceBookAPIConnection):
    """API connection to page related queries"""
    def __init__(self, *, pagetoken=None, page=None):
        super().__init__()
        self.pagetoken = pagetoken
        self.page = page
        self.graph = facebook.GraphAPI(access_token=self.pagetoken, version=self.version)
        self.post_ids, self.posts, self.post_data, self.post_connections = None, None, None, None
        self.post_insights, self.post_attributes = None, None


    def query_post_ids(self, fields=None, limit=50):
        """return post ids and limit to the value of 'limit'"""
        if fields is None:
            fields = f'posts.fields(title, created_time).limit({limit})'
        self.post_ids = self.graph.get_object(id=self.page, fields=fields)

    def query_posts(self):
        """retrieve post date from feed - prespective is post posted by 'me' on 'my feed' on 'my page'"""
        self.post_data = self.graph.get_connections(id=self.page, connection_name='feed')

    def query_all_posts(self, fields=None, since='2018-08-01', until='2018-08-31'):
        """Queried all posts to return data an id of each post and returns generator object"""
        if fields is None:
            #fields = 'created_time, message, type'
            fields = 'created_time, permalink_url, properties'
        self.posts = self.graph.get_all_connections(id=self.page, connection_name='posts', fields=fields,
                                                    since=since, until=until)

    def query_post_connections(self, postid):
        """returns connections to the post"""
        self.post_connections = self.graph.get_object(id=postid, fields="""message, comments.summary(total_count), 
                                                      reactions.summary(total_count), shares""")

    def query_post_attributes(self, postid, connection_name='comments', include_hidden=True,
                              order='reverse_chronological', filter='stream', summary='total_count'):
        self.post_attributes = self.graph.get_connections(id=postid, connection_name=connection_name,
                                                          include_hidden=include_hidden, order=order,
                                                          filter=filter, summary=summary)
																

    def query_post_insights(self, postid, connection_name='insights', metrics='post_activity_by_action_type',
                            datepreset='yesterday', period='lifetime', show_description_from_api_doc=True):
        self.post_insights = self.graph.get_connections(id=postid, connection_name=connection_name, metric=metrics,
                                                        datepreset=datepreset,period=period,
                                                        show_description_from_api_doc=show_description_from_api_doc)










