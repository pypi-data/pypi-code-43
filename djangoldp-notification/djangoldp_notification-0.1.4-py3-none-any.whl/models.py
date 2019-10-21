import logging
from threading import Thread

import requests
from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from oidc_provider.models import Token
from django.urls import NoReverseMatch

from djangoldp.fields import LDPUrlField
from djangoldp.models import Model

from django.template import loader
from .permissions import InboxPermissions


class Notification(Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='inbox', on_delete=models.deletion.CASCADE)
    author = LDPUrlField()
    object = LDPUrlField()
    type = models.CharField(max_length=255)
    summary = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    unread = models.BooleanField(default=True)

    class Meta(Model.Meta):
        owner_field = 'user'
        ordering = ['-date']
        permission_classes = [InboxPermissions]
        anonymous_perms = ['add']
        authenticated_perms = ['inherit']
        owner_perms = ['view', 'change', 'control']

    def __str__(self):
        return '{}'.format(self.type)


class Subscription(Model):
    object = models.URLField()
    inbox = models.URLField()

    def __str__(self):
        return '{}'.format(self.object)


# --- SUBSCRIPTION SYSTEM ---
@receiver(post_save, dispatch_uid="callback_notif")
def send_notification(sender, instance, **kwargs):
    if sender != Notification:
        threads = []
        try:
            urlContainer = settings.BASE_URL + Model.container_id(instance)
            urlResource = settings.BASE_URL + Model.resource_id(instance)
        except NoReverseMatch:
            return

        for subscription in Subscription.objects.filter(models.Q(object=urlResource)|models.Q(object=urlContainer)):
            process = Thread(target=send_request, args=[subscription.inbox, urlResource])
            process.start()
            threads.append(process)


def send_request(target, object_iri):
    try:
        req = requests.post(target,
                            json={"@context": "https://cdn.happy-dev.fr/owl/hdcontext.jsonld",
                                  "object": object_iri, "type": "update"},
                            headers={"Content-Type": "application/ld+json"})
    except:
        logging.error('Djangoldp_notifications: Error with request')
    return True


@receiver(post_save, sender=Notification)
def send_email_on_notification(sender, instance, created, **kwargs):
    if created and instance.summary and settings.JABBER_DEFAULT_HOST and instance.user.email:
        try:
            if instance.author.startswith(settings.SITE_URL):
                who = str(Model.resolve_id(instance.author.replace(settings.SITE_URL,'')))
            else:
                who = requests.get(instance.author).json()['name']
        except:
            who = "Unknown Person"

        try:
            if instance.object.startswith(settings.SITE_URL):
                where = str(Model.resolve_id(instance.object.replace(settings.SITE_URL,'')))
            else:
                where = requests.get(instance.object).json()['name']
        except:
            where = "Unknown place"

        if(who == where):
            where = "has sent you a private message"
        else:
            where = "mention you on " + where

        html_message = loader.render_to_string(
            'email.html',
            {
                'on': settings.JABBER_DEFAULT_HOST,
                'instance': instance,
                'author': who,
                'object': where
            }
        )

        send_mail(
            'Notification on ' + settings.JABBER_DEFAULT_HOST,
            instance.summary,
            settings.EMAIL_HOST_USER or "noreply@" + settings.JABBER_DEFAULT_HOST,
            [instance.user.email],
            fail_silently=True,
            html_message=html_message
        )
