from shield34_reporter.auth.sdk_authentication import SdkAuthentication
from shield34_reporter.exceptions import Shield34PropertiesFileNotFoundException, \
    Shield34PropertiesSyntaxIncorrect, Shield34LoginFailedException
from .shield34_listener import Shield34Listener
from shield34_reporter.overrider.selenium_overrider import SeleniumOverrider
import robot


class RobotListener(object):

    ROBOT_LISTENER_API_VERSION = 3

    shield34_listener = Shield34Listener()

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        Shield34Listener.logger = robot.api.logger
        try:
            Shield34Listener.logger.console("Searching for shield34.ini file...")
            SdkAuthentication.login()
            Shield34Listener.logger.console("Logged in successfully to Shield34")
        except Shield34PropertiesFileNotFoundException as e:
            Shield34Listener.logger.warn(e)
        except Shield34PropertiesSyntaxIncorrect as e:
            Shield34Listener.logger.warn(e)
        except Shield34LoginFailedException as e:
            Shield34Listener.logger.warn(e)

    def start_suite(self, data, result):
        try:
            SeleniumOverrider.override()
            self.shield34_listener.on_suite_start(suite_name=data.name)
        except Shield34PropertiesFileNotFoundException as e:
            Shield34Listener.logger.warn(e)
        except Shield34PropertiesSyntaxIncorrect as e:
            Shield34Listener.logger.warn(e)
        except Shield34LoginFailedException as e:
            Shield34Listener.logger.warn(e)

    def end_suite(self, data, result):
        pass

    def start_test(self, test, result):
        try:
            self.shield34_listener.on_test_start(test_name=test.name, test_class_name=test.longname)
        except Shield34PropertiesFileNotFoundException as e:
            Shield34Listener.logger.warn(e)
        except Shield34PropertiesSyntaxIncorrect as e:
            Shield34Listener.logger.warn(e)
        except Shield34LoginFailedException as e:
            Shield34Listener.logger.warn(e)

    def end_test(self, data, result):
        try:
            if result.status == 'PASS':
                self.shield34_listener.on_test_success()
                self.shield34_listener.on_test_finish()

            elif result.status == 'FAIL':
                self.shield34_listener.on_test_failure(result)
                self.shield34_listener.on_test_finish()

            elif result.status == 'SKIPPED':
                self.shield34_listener.on_test_skipped()
                self.shield34_listener.on_test_finish()
        except Shield34PropertiesFileNotFoundException as e:
            Shield34Listener.logger.warn(e)
        except Shield34PropertiesSyntaxIncorrect as e:
            Shield34Listener.logger.warn(e)
        except Shield34LoginFailedException as e:
            Shield34Listener.logger.warn(e)


