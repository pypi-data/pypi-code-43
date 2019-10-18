from __future__ import absolute_import

import os
from datetime import datetime

from celery import Celery, shared_task
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail

log = get_task_logger(__name__)

# set the default Django settings module for the 'celery' program.
# from wac_bpm import tasks
# ### Celery / ViewFlow
# * instalar RabbitMQ broker ```$ sudo apt-get install rabbitmq-server```
# * instalar celery ```(env) alugarImovel$ pip install celery```
# * Rodar celery em um terminal
# ```alugarImovel$ celery -A ftlbase worker -l info```
# * e o django em outro
# * rodar o servidor ```alugarImovel$ ./manage.py runserver 0.0.0.0:8000```

# Como fazer o genérico
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alugarImovel.settings')

app = Celery('common')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.config_from_object('django.conf:settings')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}.'.format(self.request))


# @app.task(bind=True, default_retry_delay=30 * 60)
@shared_task(bind=True)
def email_user(self, users, subject, message, from_email=None, html_message=None):
    debug = True

    if debug:
        log.info('email_user => EMAIL USER')
        log.info('email_user - self =>', self)
        log.info('email_user - users =>', users)
        log.info('email_user - subject =>', subject)
        log.info('email_user - message =>', message)
        log.info('email_user - from_email =>', from_email)
        log.info('email_user - html_message =>', html_message)

    if hasattr(users, 'email'):
        if debug:
            log.info('email_user = hasattr =>hasattr')
        recipient_list = [u.email for u in users]
    else:
        if debug:
            log.info('email_user = else =>else')
        recipient_list = [u for u in users]

    # if debug:
    log.info('email_user: antes')

    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list,
              html_message=html_message)

    # if debug:
    log.info('email_user: depois')

    return subject


# @app.on_after_finalize.connect
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # from imovel.form import ContratoAdmReport
    from celery.schedules import crontab_parser

    minuto = '*/10'
    hora = 12
    expira = 10

    # log.info('setup_periodic_tasks min=%s, hora=%s, expira=%s' % (minuto, hora, expira))
    if True:
        log.info('setup_periodic_tasks ------- TCHAU')
        return

    log.info('setup_periodic_tasks, antes if', '*/10', crontab_parser(60).parse('*/10'))
    # Calls test('hello') every 60 seconds.
    # sender.add_periodic_task(schedule=120.0, sig=test.s('hello'), name='Hello', expires=10)

    # Executes every Monday morning at 7:30 a.m.
    if False:  # Desativado até resolver o problema do Celery Beat
        sender.add_periodic_task(
            schedule=crontab(minute=50, hour=13, day_of_week=1),
            sig=test.s('Minuto %s, Hora %s!' % (minuto, hora)),
            expires=expira,
        )

        sender.add_periodic_task(
            schedule=crontab(minute='*/4', hour=hora + 1),
            sig=test.s('Minuto %s, Hora %s!' % (minuto, hora + 1)),
            expires=expira,
        )

        sender.add_periodic_task(
            schedule=crontab(minute='*/10', ),  # hour=hora + 2),
            sig=test.s('Minuto %s, Hora %s!' % (minuto, hora + 2)),
            expires=expira,
        )

        sender.add_periodic_task(
            schedule=crontab(minute=minuto, hour=hora + 3),
            sig=test.s('Minuto %s, Hora %s!' % (minuto, hora + 3)),
            expires=expira,
        )

        sender.add_periodic_task(
            schedule=crontab(minute=minuto, hour=hora + 4),
            sig=test.s('Minuto %s, Hora %s!' % (minuto, hora + 4)),
            expires=expira,
        )

    log.info('setup_periodic_tasks', minuto, hora, expira)

    # Contrato de Administração Vencidos
    # Executes every morning at 07h
    # sender.add_periodic_task(
    #     schedule=crontab(hour=14, minute=40),
    #     # schedule=60,
    #     sig=relatorio_contratos_adm_vencidos.s(),
    #     name='Contratos de Administração Vencidos', expires=10,
    # )


@app.task(bind=True)
def test(self, arg):
    print('vars(self)', vars(self))
    print(arg, datetime.now())
    # return arg


def relatorio_email_user(users, subject, queryset, template_name="table"):
    """
    Envia relatório por email

    :param users: lista de emails que receberão o relatório
    :param subject: Assunto
    :param queryset: Queryset que será passada ao template com os registros já filtrados
    :param template_name: Template de geração do relatório
    :return:
    """
    from django.template import Template, Context
    from django.template.loader import render_to_string

    try:
        subject = settings.EMAIL_SUBJECT_PREFIX + subject
    except Exception:
        pass

    task = None

    try:
        dictionary = {'queryset': queryset, 'users': users, 'site': settings.SITE_URL}
        ctx = Context(dictionary)
        t = Template(subject)
        subject = t.render(ctx)
        message = render_to_string(template_name + '.txt', dictionary)
        html_message = render_to_string(template_name + '.html', dictionary)
        # u = users
        # log.info('relatorio_email_user: antes')
        task = email_user.delay(users=users, subject=subject, message=message, html_message=html_message)
        # log.info('relatorio_email_user: depois')
    except Exception as v:
        log.info('relatorio_email_user: %s', subject)

    return task
