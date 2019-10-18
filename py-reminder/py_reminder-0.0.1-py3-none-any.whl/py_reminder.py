import functools
import os
import json
import sys
from pathlib import Path
from socket import gethostname
import logging

from datetime import datetime
from timeit import default_timer as timer

from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

HOME_PATH = str(Path.home())
CONFIG_PATH = HOME_PATH + '/.config'
CONFIG = CONFIG_PATH + '/py_reminder.json'


def config(address, password, smtp, port, default_to=''):
    if CONFIG_PATH not in os.listdir(HOME_PATH):
        os.system('mkdir "%s"' % CONFIG_PATH)
    with open(CONFIG, 'w') as f:
        json.dump({'ADDRESS': address, 'PASSWORD': password, 'SMTP': smtp, 'PORT': port, 'TO': default_to}, f)


def send_email(time_start, task, error='', to=''):
    with open(CONFIG) as json_data_file:
        config = json.load(json_data_file)

    s = SMTP(host=config['SMTP'], port=config['PORT'])
    s.starttls()
    s.login(config['ADDRESS'], config['PASSWORD'])
    print(s)
    
    msg = MIMEMultipart()
    msg['From'] = formataddr(['PyReminder', config['ADDRESS']])
    if to:
        msg['To'] = to
    else:
        msg['To'] = config['TO']
    
    common = 'Task: %s\nTime: %s\nMachine: %s\nTime Usage: %.2f mins\nStatus: ' % (task, datetime.now().strftime('%Y-%m-%d %H:%M'), gethostname(), (timer() - time_start) / 60)
    if error:
        msg['X-Priority'] = '2'
        message = common + 'Error! Please check! \n\n%s' % (error)
        msg['Subject'] = '[PyReminder] Error for %s' % task
    else:
        message = common + 'Complete!'
        msg['Subject'] = '[PyReminder] Completion for %s' % task
       
    msg.attach(MIMEText(message, 'plain'))
    s.send_message(msg)
    del msg


def monitor(task='Your Task', to=''):
    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            print("Inside decorator")
            logger = logging.Logger('catch_all')
            ts = timer()
            try:
                value = func(*args, **kwargs)
                send_email(time_start=ts, task=task, error='', to=to)
                return value
            except Exception as e:
                logger.error(e, exc_info=True)
                send_email(time_start=ts, task=task, error='%s\n%s\n%s' % sys.exc_info(), to=to)
        return wrapper_decorator
    return decorator

# import time
# @monitor(task='test')
# def foo():
#     print('inside foo')
#     time.sleep(1)
#     t = 1/0
#     print('inside foo')
# foo()