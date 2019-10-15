from django.db import transaction


__version__ = '1.3.0'


@transaction.atomic()
def notify(
    user, template, summary=None, kind='info', actions=[], tags=[],
    send_email=True, sender_info=None, **context
):
    from .models import Notification, Sender
    from django.template.loader import render_to_string

    text = render_to_string(
        'notifications/%s.html' % template,
        context
    )

    if isinstance(sender_info, str):
        try:
            sender_obj = Sender.objects.get(
                name__iexact=sender_info.strip()
            )
        except Sender.DoesNotExist:
            sender_obj = Sender.objects.create(
                name=sender_info.lower().strip()
            )
    elif isinstance(sender_info, dict):
        try:
            assert 'name' in sender_info
        except AssertionError:
            raise Exception(
                'Sender invalid. Must be a dict with '
                'name and optionally verbose_name, url and icon.'
            )

        try:
            sender_obj = Sender.objects.get(
                name__iexact=sender_info['name'].strip()
            )
        except Sender.DoesNotExist:
            sender_obj = Sender(
                name=sender_info['name'].lower().strip()
            )

        if sender_info.get('verbose_name'):
            sender_obj.verbose_name = sender_info['verbose_name']

        if sender_info.get('url'):
            sender_obj.url = sender_info['url']

        if sender_info.get('icon'):
            sender_obj.icon = sender_info['icon']

        sender_obj.save()
    elif sender_info is None:
        sender_obj = None
    else:
        raise Exception(
            'Sender invalid. Must be a string or dict with '
            'name and optionally verbose_name, url and icon.'
        )

    notification = Notification.objects.create(
        user=user,
        sender=sender_obj,
        summary=summary or template.replace('_', ' ').capitalize(),
        text=text,
        kind=kind,
        email=send_email
    )

    for ordering, action in enumerate(actions):
        kind, text, url = action
        notification.actions.create(
            kind=kind,
            text=text,
            url=url,
            ordering=ordering
        )

    if isinstance(tags, dict):
        for tag, description in tags.items():
            notification.tags.create(
                slug=tag,
                description=description
            )
    else:
        for tag in sorted(set(tags)):
            notification.tags.create(slug=tag)

    transaction.on_commit(notification.send)
