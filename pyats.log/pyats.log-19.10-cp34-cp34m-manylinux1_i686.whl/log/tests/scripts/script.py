from pyats import aetest
from pyats.async_ import pcall
import logging

logger = logging.getLogger(__name__)


class Testcase(aetest.Testcase):

    @aetest.test
    def plain_messages(self):
        logger.info('new info messages')
        logger.critical('new critical messages')
        logger.debug('new debug messages')
        logger.warning('new warning messages')
        logger.error('new error messages')
        logger.error('')
        logger.info('''this is a multiple line\nmessage
and this line is a new line
another new line''')

    @aetest.test
    def exception_message(self):
        try:
            abcdef
        except:
            logger.exception('blah!')

    @aetest.test
    def pcall_exceptions(self):

        def func():
            aaa

        pcall(func)

if __name__ == '__main__':
    aetest.main()