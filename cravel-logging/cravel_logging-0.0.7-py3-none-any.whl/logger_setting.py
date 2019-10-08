import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class logger_setting:
    def __init__(self, filepath, Appname):
        self.LOGGING['handlers']['logfile']['filename'] = filepath
        self.LOGGING['loggers'][Appname] = {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        }
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format' : "[cid: %(cid)s][%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
        },
        'handlers': {
            'logfile': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'debug.log'),
                'filters': ['correlation'],
                'maxBytes': 50000,
                'backupCount': 2,
                'formatter': 'standard',
            },
            'console':{
                'level':'INFO',
                'class':'logging.StreamHandler',
                'filters': ['correlation'],
                'formatter': 'standard'
            },
        },
        'filters': {
            'correlation': {
                '()': 'cid.log.CidContextFilter'
                },
        },
        'loggers': {
            'django': {
                'handlers':['console'],
                'propagate': True,
                'level':'WARN',
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }