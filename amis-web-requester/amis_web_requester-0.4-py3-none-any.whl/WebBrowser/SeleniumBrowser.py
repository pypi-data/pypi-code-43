from selenium import webdriver
import os
import signal
from Requesters.Response import Response


class SeleniumBrowser:

    def __init__(self, registration=None):
        """

        :param registration: instance of IRegistration
        """

        self.__registration = registration

        # TODO load driver depend on OS type
        dir_path = os.path.dirname(os.path.realpath(__file__))
        chromedriver = os.path.join(dir_path, 'drivers', 'chromedriver_win')

        options = webdriver.ChromeOptions()

        # Comment next line to see browser
        options.add_argument('headless')  # <====== comment this line to see browser

        options.add_argument('window-size=1200x400')  # optional
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        self.__browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)

        self.__browser.delete_all_cookies()

        if registration:
            registration.register(self.__browser)


    def __del__(self):
        self.__browser.delete_all_cookies()
        self.__browser.close()
        os.kill(self.__browser.service.process.pid, signal.SIGTERM)


    def execute_script(self, script):
        """

        :param text of script
        :return: script result
        """
        return self.__browser.execute_script(script)


    def execute_html(self,html_content):
        """

        :param html_content: raw html
        :return:  executed html with js
        """
        self.__browser.get("data:text/html;charset=utf-8,{html_content}".format(html_content=html_content))

        return self.__browser.page_source


    def make_actions(self,actions):
        """

        :param actions: list of IAction
        :return: None
        """

        for action in actions:
            action.make_action(self.__browser)


    def make_get_request(self, url, parameters=None):

        # TODO use Requesters
        self.__browser.get(url=url)

        status = 200
        html_content = self.__browser.page_source

        return Response(status=status, data=html_content)


    def get_html(self):

        return self.__browser.page_source


    def set_element_text(self,element_id,text):

        script="document.getElementById('{0}').value = {1};".format(element_id, text)
        self.execute_script(script)
        # element = self.__browser.find_element_by_id(element_id)
        # element.click()


    def push_element(self, parent_tag, parent_class, element_tag, element_class):

        parent = self.__browser.find_element_by_css_selector('{0}.{1}'.format(parent_tag, parent_class))
        if parent:
            element = parent.find_element_by_css_selector('{0}.{1}'.format(element_tag, element_class))
            if element:
                element.click()