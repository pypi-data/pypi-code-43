from Requesters.InfinityRequester import InfinityRequester
from Requesters.InfinityScroller import InfinityScroller
from Requesters.Requester import Requester
from WebBrowser.WebAction.ActionScroll import ActionScroll


# call Requesters to get raw http response
requester = Requester(url="http://google.com")
response = requester.make_get_request({'q': 'ok'})

html = response.get_data()
status = response.get_status()
print("Status {0}\nData {1}".format(status, html))



# call Requesters with html running
requester = Requester(url="https://www.instagram.com/p/BtRzmCkA2sT/", run_html=True)
response = requester.make_get_request()

html = response.get_data()
status = response.get_status()
print("Status {0}\nData {1}".format(status, html))


# call InfinityScroller
scroll_action = ActionScroll()
scroller = InfinityScroller(url='https://www.instagram.com/thenintendoc/', actions=[scroll_action],scroll_pause=2)

html = scroller.scroll()
print(html)
while html is not None:
    html = scroller.scroll()
    print(html)


#call InfinityRequester
infinity_requester = InfinityRequester(url='https://www.instagram.com/thenintendoc/',
                                       parent_element='article',
                                       parent_element_classes=['FyNDV'],
                                       child_element='div',
                                       child_element_classes=['v1Nh3', 'kIKUG',  '_bz0w'],
                                       scroll_pause=2)

result = infinity_requester.make_get_request()
print(list(result.keys()))
