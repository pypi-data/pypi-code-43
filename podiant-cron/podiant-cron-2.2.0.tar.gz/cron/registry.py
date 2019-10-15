from logging import getLogger
from .helpers import get_scheduler


class Registry(object):
    def __init__(self):
        self.__registry = {}

    def register(self, func, queue_name, cron_string):
        if func not in self.__registry:
            self.__registry[func] = {
                'queue_name': queue_name,
                'cron_string': cron_string
            }

            logger = getLogger('podiant.cron')
            logger.debug(
                'Registered job \'%s\' with cron string \'%s\'' % (
                    func.__name__,
                    cron_string
                )
            )

        return self.__registry[func]

    def schedule(self, queue_name=None):
        scheduler = get_scheduler(queue_name)
        logger = getLogger('podiant.cron')

        for func, settings in self.__registry.items():
            cs = settings['cron_string']
            qn = settings['queue_name']
            scheduler.cron(
                cs,
                func=func,
                queue_name=qn
            )

            logger.debug(
                'Scheduled job \'%s\' with cron string \'%s\'' % (
                    func.__name__,
                    cs
                )
            )


jobs = Registry()
