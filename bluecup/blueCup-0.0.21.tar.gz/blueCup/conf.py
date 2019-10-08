from celery.schedules import crontab
from kombu import Exchange
from kombu import Queue
from nezha.utime import last_month

REDIS_URL = 'redis://**********'
CELERY_TIMEZONE = 'Asia/Shanghai'
BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXTENDED = True
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = None
CELERY_ACCEPT_CONTENT = ['json', 'json']
CELERY_INCLUDE = [
    'blueCup.task_inner_platform',
    'blueCup.task_notification',
    'blueCup.task_xinyan',
    'blueCup.third_interface_bill'
]

CELERY_TASK_ROUTES = {
    'blueCup.task_notification.*': {'queue': 'notification'},
    'blueCup.third_interface_bill.*': {'queue': 'third_interface_bill'},
    'blueCup.task_xinyan.*': {'queue': 'xinyan'},
    'blueCup.third_interface_bill.bill_someday_count': {'queue': 'bill_someday_statistic'},
    'blueCup.third_interface_bill.bill_someday_statistic': {'queue': 'bill_someday_statistic'}
}

CELERY_QUEUES = (
    Queue(name='notification', routing_key='task_notification.#',
          exchange=Exchange(name='notification', type='topic')),
    Queue(name='third_interface_bill', routing_key='third_interface_bill.#',
          exchange=Exchange(name='third_interface_bill', type='topic')),
    Queue(name='xinyan', routing_key='task_xinyan.#',
          exchange=Exchange(name='xinyan', type='topic')),
    Queue(name='bill_someday_count', routing_key='third_interface_bill.#',
          exchange=Exchange(name='bill_someday_count', type='topic')),
    Queue(name='bill_someday_statistic', routing_key='third_interface_bill.#',
          exchange=Exchange(name='bill_someday_statistic', type='topic')),
)

CELERY_TASK_DEFAULT_QUEUE = 'blueCup'

CELERY_TASK_ANNOTATIONS = {
    'send_email': {'rate_limit': '1/s'},
    'send_email_attach': {'rate_limit': '1/s'},
    'send_dingding_text': {'rate_limit': '1/s'},
    'send_dingding_markdown': {'rate_limit': '1/s'},
}

CELERYBEAT_SCHEDULE = {
    'corntab_bill_yesterday_count': {
        'task': 'bill_someday_count',
        'schedule': crontab(hour=9, minute=1),
        # 'schedule': crontab(),
        'args': (),
        'options': {'queue': 'bill_someday_statistic'}
    },
    'corntab_bill_yesterday_statistic': {
        'task': 'bill_someday_statistic',
        'schedule': crontab(hour=9, minute=1),
        'args': (),
        'options': {'queue': 'bill_someday_statistic'}
    },
    'corntab_bill_month_statistic': {
        'task': 'bill_someday_statistic',
        'schedule': crontab(day_of_month=1, hour=9, minute=1),
        'args': (),
        'kwargs': {
            'someday': last_month,
        },
        'options': {'queue': 'bill_someday_statistic'}
    },
}
