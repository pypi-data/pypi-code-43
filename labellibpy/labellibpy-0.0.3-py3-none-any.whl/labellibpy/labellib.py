import requests
import os

class LabelService():
    """
        This class has static methods to help get labels from label server
    """

    @staticmethod
    def getThese(messages: list) -> list:
        """
            This function receives a list of messages and try to retrieve it from server. Server address must be in a environment variable LABEL_SERVER.
        """
        label_server = os.environ.get('LABEL_SERVER', None)
        
        if label_server:
            return LabelService()._create_generic_request(messages, label_server)
        
        raise EnvironmentError("Environment variable LABEL_SERVER not configured. \nPlease set it up and try again.")
        #return LabelService()._create_generic_request(messages, 'http://localhost:8000/api/v1/labels')

    @staticmethod
    def _create_generic_request(messages: list, link: str) -> requests.get:
        link = link + LabelService()._format_data_to_request(messages)
        #print(link)
        req = None

        try:
            req = requests.get(
                link,
                headers={'content-type': 'application/json'}
            )

        except requests.exceptions.HTTPError as err:
            raise err

        except requests.exceptions.ConnectionError as err:
            raise err

        except requests.exceptions.Timeout as err:
            raise err

        except requests.exceptions.RequestException as err:
            raise err
        
        return req.text
    
    @staticmethod
    def _format_data_to_request(messages: list) -> str:
        string_created = '?messages='
        for message in messages:
            string_created += str(message)+','

        # slice to avoid return a string like 1,2,3,4,
        string_created = string_created[0: len(string_created)-1]
        #print(string_created)
        return string_created