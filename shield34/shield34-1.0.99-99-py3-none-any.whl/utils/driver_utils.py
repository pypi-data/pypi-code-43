from robot.libraries.BuiltIn import BuiltIn


class DriverUtils:

    @staticmethod
    def get_current_driver():

        try:
            current_driver = BuiltIn().get_library_instance('SeleniumLibrary')._current_browser()
        except Exception as e:
            current_driver = None
        return current_driver


    @staticmethod
    def get_page_html():
        driver = DriverUtils.get_current_driver()
        page_source = ''
        try:
            page_source = driver.page_source
        except Exception as e:
            page_source = ''
        return page_source