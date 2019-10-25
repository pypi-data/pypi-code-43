from requests_futures.sessions import FuturesSession
from concurrent.futures import CancelledError, TimeoutError
import logging
import json
import time

logger = logging.getLogger(__name__)

class StakionError(RuntimeError):
    '''Stakion custom exception'''
    pass

class publisherPost():
    """Publish message using POST.
    
    Parameters
    ----------
    url: str
        URL to post messages to
    api_key: str
        API key
    """
    def __init__(self, url, auth_url, api_key):
        self.url = url
        self.session = FuturesSession()
        self.auth_url = auth_url
        
        if '.' not in api_key:
            raise ValueError('Invalid API key, check that you are using the API key and not the token Id.')
        else:
            self.api_key = str(api_key)
        
        self.refreshing_token = None
        self.access_token = self._get_access_token()
        self.timeout = 60
        self.max_retries = 3
    
    def _get_access_token(self):
        logger.debug('Getting access token')
        future = FuturesSession().post(
            self.auth_url, json={'apiKey': self.api_key}
        )
        self.refreshing_token = future
        
        try:
            response = future.result()
            access_token = json.loads(response.content)['access_token']
        except (CancelledError, TimeoutError, Exception) as e:
            access_token = None
            logger.warn('Could not get access token - error = {}'.format(e))
        return access_token
    
    def emit(self, message, callback, nb_retries = 0):
        """Publish message
        
        Parameters
        ----------
        message: dict
            Message to push to Stakion.
        callback: func
            The callback function is called when the message is acknowledges.
        """
        def response_hook(resp, *args, **kwargs):
            logger.debug('status_code = {} - nb_retries = {}'.format(resp.status_code, nb_retries))
            if resp.status_code == 200:
                callback(message['__uuid'])
            elif (resp.status_code == 401):
                if (nb_retries < self.max_retries):
                    error = json.loads(resp.content)['error']
                    if error == 'Expired access token':
                        
                        if self.refreshing_token.done():
                            self.access_token = self._get_access_token()
                            self.emit(message, callback, nb_retries + 1)
                        else:
                            # Wait for token refresh
                            logger.debug('Waiting for refresh token - uid = {}'.format(message['__uuid']))
                            while self.refreshing_token.done() == False:
                                time.sleep(0.1)
                            
                            # Token is either refreshed or hasn't updated
                            self.emit(message, callback, nb_retries + 1)
                    
                    else:
                        logger.warning('Could not send message - uid = ${}'.format(message['__uuid']))
                else:
                    logger.error('Tried refreshing access token {} times but failed.'.format(self.max_retries))
            else:
                logger.warning('Could not send message - uid = ${}'.format(message['__uuid']))
        
        self.session.headers['authorization'] = self.access_token
        future = self.session.post(self.url, json={'log': message}, hooks={
            'response': response_hook
        })