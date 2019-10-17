from WebBrowser.WebAction.IAction import IAction


class ActionScroll(IAction):

    def make_action(self, browser):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")