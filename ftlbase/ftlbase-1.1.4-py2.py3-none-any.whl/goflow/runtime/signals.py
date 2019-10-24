import django.dispatch
from common.logger import Log

# Fired when a new ProcessInstance is created, starting a new Workflow

# Fired when a ProcessInstance is created, starting a Workflow Process Instance
workflow_process_instance_created = django.dispatch.Signal()
# Fired when a ProcessInstance is completed, ending a Workflow Process Instance
workflow_process_instance_completed = django.dispatch.Signal()

# Fired when some event happens during the life of a WorkItem
workflow_item_created = django.dispatch.Signal()
workflow_item_activated = django.dispatch.Signal(providing_args=["user"])
workflow_item_completed = django.dispatch.Signal()
workflow_item_forwarded = django.dispatch.Signal()

log = Log('goflow.runtime.signals')


def workflow_sender_log(sender, msg):
    if sender:
        obj = sender.wfobject()
        s = 'Workflow de {} pk: {}, Activity: {}, status: {}, ' \
            'sender: {}, sender.status: {}, ' \
            'instance: {}, instance.status: {}, '.format(obj.__class__.__name__, obj.pk, sender.activity, obj.status,
                                                         sender, sender.status,
                                                         sender.instance, sender.instance.status)

        log.event(s, sender)
        print(s)
    else:
        log.info(msg)
        print(msg)


def workflow_process_instance_created_log(sender, **kwargs):
    try:
        user = kwargs.get('user', None)
        name = user.username
    except:
        name = ''
    process_name = kwargs.get('process_name', None)

    s = 'process instance {}, created by user: {}, process: {}, item: {}'.format(process_name, name,
                                                                                 sender, sender.wfobject())

    log.event(s, sender)
    print('workflow_process_instance_created_log: ' + s)

    from goflow.runtime.models import Event
    Event.objects.create(name='activated by %s' % name, workitem=sender)


def workflow_process_instance_completed_log(sender, **kwargs):
    try:
        user = kwargs.get('user', None)
        name = user.username
    except:
        name = ''
    process_name = kwargs.get('process_name', None)
    item = kwargs.get('item', None)

    s = 'process {}, completed by user: {}, process instance: {}, item: {}'.format(process_name, name,
                                                                                   sender, sender.wfobject())

    log.event(s, sender)
    print('workflow_process_instance_completed_log: ' + s)

    from .models import Event
    Event.objects.create(name='completed by %s' % name, workitem=sender)


def workflow_item_activated_log(sender, **kwargs):
    try:
        user = kwargs.get('user', None)
        name = user.username
    except:
        name = ''
    subflow = kwargs.get('subflow', None)

    s = 'Activated: process: {}, workitem {} activity: {}, ' \
        'by user: {} => {}'.format(sender.instance.process.title, sender.pk, sender.activity.title, name, sender)
    if subflow:
        s = s + 'subflow {}'.format(subflow)

    log.event(s, sender)
    print('workflow_item_activated_log: ' + s)

    from .models import Event
    Event.objects.create(name='activated by %s' % name, workitem=sender)


def workflow_item_completed_log(sender, **kwargs):
    try:
        user = kwargs.get('user', None)
        name = user.username
    except:
        name = ''
    subflow = kwargs.get('subflow', None)

    s = 'Completed: process: {}, workitem {} activity: {}, ' \
        'by user: {} => {}'.format(sender.instance.process.title, sender.pk, sender.activity.title, name, sender)
    if subflow:
        s = s + 'subflow {}'.format(subflow)

    log.event(s, sender)
    print('workflow_item_completed_log: ' + s)

    from .models import Event
    Event.objects.create(name='completed by %s' % name, workitem=sender)


def workflow_item_forwarded_log(sender, **kwargs):
    try:
        user = kwargs.get('user', None)
        name = user.username
    except:
        name = ''
    target_activity = kwargs.get('target_activity', None)
    subflow = kwargs.get('subflow', None)

    s = 'Forwarded: process: {}, workitem {} activity: {} to activity: {}, ' \
        'by user: {} => {}'.format(sender.instance.process.title, sender.pk, sender.activity.title, target_activity.title,
                                   name, sender)
    if subflow:
        s = s + 'subflow {}'.format(subflow)

    log.event('workflow_item_forwarded_log: ' + s, sender)
    print('workflow_item_forwarded_log: ' + s)

    from .models import Event
    Event.objects.create(name=s, workitem=sender)
