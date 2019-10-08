# coding: utf-8

from celery.schedules import crontab

REDIS_URL = 'redis://47.102.132.18/6'
CELERY_TIMEZONE = 'Asia/Shanghai'
BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 3600 * 24
CELERY_ACCEPT_CONTENT = ['json', 'json']
CELERY_INCLUDE = [
    'morn_bell.third_interface_bill',
]

CELERY_TASK_DEFAULT_QUEUE = 'blueCup'

CELERYBEAT_SCHEDULE = {
    'corntab_third_interface_bill': {
        'task': 'bill_yesterday_count',
        'schedule': crontab(),
        'args': (),
        'options': {'queue': 'blueCup'}
    }
}
