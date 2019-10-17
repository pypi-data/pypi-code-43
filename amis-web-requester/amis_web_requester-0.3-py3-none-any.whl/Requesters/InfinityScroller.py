import time
from WebBrowser.SeleniumBrowser import SeleniumBrowser


class InfinityScroller:

    def __init__(self, url, registration=None, actions=None, scroll_pause=3):
        """

        :param url: site url
        :param registration: instance of IRegistration
        :param actions: list of IAction
        """

        self.__url = url
        self.__registration = registration
        self.__actions = actions
        self.__scroll_pause = scroll_pause

        self.__selenium = SeleniumBrowser(registration=registration)

        response = self.__selenium.make_get_request(self.__url)
        self.__html_content = response.get_data()

        self.__last_height = 0
        self.__new_height = 0


    def scroll(self):
        """
        Scroll page and return html. After each scrolling there is html intersection between scroll results

        :return: html or None if scroll finish.
        """

        # first call
        if self.__new_height == 0:
            self.__new_height = self.__selenium.execute_script("return document.body.scrollHeight")
            return self.__html_content

        if self.__new_height != self.__last_height:
            self.__last_height = self.__new_height

            # perform actions
            self.__selenium.make_actions(self.__actions)

            # Wait to load page
            time.sleep(self.__scroll_pause)

            # upload data
            self.__html_content = self.__selenium.get_html()

            # Calculate new scroll height and compare with last scroll height
            self.__new_height = self.__selenium.execute_script("return document.body.scrollHeight")

            return self.__html_content

        return None