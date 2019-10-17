from bs4 import BeautifulSoup

from Requesters.InfinityScroller import InfinityScroller
from WebBrowser.WebAction.ActionScroll import ActionScroll


class InfinityRequester:

    def __init__(self, url,parent_element, parent_element_classes, child_element, child_element_classes,
                 url_classes=None, registration=None, scroll_pause=3):
        """

           :param url: resourse
           :param parent_element: tag name
           :param parent_element_classes: list of classes
           :param child_element: tag name
           :param child_element_classes: list of classes
           :param registration: IRegistration instance
       """


        self.__scroller = InfinityScroller(url='https://www.instagram.com/thenintendoc/', actions=[ActionScroll()], registration=registration, scroll_pause=scroll_pause)

        self.__url = url
        self.__parent_element=parent_element
        self.__parent_element_classes=parent_element_classes
        self.__child_element=child_element
        self.__child_element_classes=child_element_classes
        self.__url_classes = url_classes


    def __get_elements(self, html_content):
        """

        :param html_content: html of load page
        :return: dictionary {'url': html_child_content,...}
        """

        result = dict()

        soup = BeautifulSoup(html_content, 'html.parser')

        parent = soup.find(self.__parent_element, {'class': self.__parent_element_classes})

        childs = parent.find_all(self.__child_element, {'class': self.__child_element_classes})

        # url extraction
        for child in childs:
            url = child.find('a', {'class': self.__url_classes})

            # TODO if not find exceptions
            if not url:
                continue
            if not url['href']:
                continue
            # check is part

            result[url['href']] = child

        return result


    def make_get_request(self):
        """

        :return: dictionary {'url': html_child_content,...}
        """

        html_content = self.__scroller.scroll()
        elements = dict()

        while html_content is not None:

            elements.update(
                self.__get_elements(html_content)
            )

            html_content = self.__scroller.scroll()

            print("Scrolling...")

        return elements