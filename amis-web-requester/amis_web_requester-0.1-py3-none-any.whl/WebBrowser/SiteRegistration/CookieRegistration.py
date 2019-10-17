from WebBrowser.SiteRegistration.IRegistration import IRegistration


class CookieRegistration(IRegistration):

    def __init__(self, url=None, cookies=None):
        """

        :param url: registration page
        :param cookies: pickle cookies
        """

        self.__url = url
        self.__cookies = cookies




    def register(self,browser):
        browser.get(self.__url)
        for cookie in self.__cookies:
            browser.add_cookie(cookie)
