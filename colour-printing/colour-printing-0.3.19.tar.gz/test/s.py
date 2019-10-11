from colour_printing.config import CPConfig, Term
from colour_printing import Fore, Back, Mode
from colour_printing.custom import PrintMe

cp = CPConfig("{time} {flag} {message}")


class C(object):
    @cp.wrap
    def info(self):
        self.time = Term(Fore.CYAN, default='1')
        self.flag = Term(default='IN')
        self.message = Term()


log = PrintMe(cp)

log.info('123')
log.error('123')
log.warning('123')
log.success('123')
log.debug('123',flag='debug',time='6666')
