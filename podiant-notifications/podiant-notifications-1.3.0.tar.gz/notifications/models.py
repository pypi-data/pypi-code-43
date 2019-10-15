from django.db import models
from pubsub import channels
from .querysets import NotificationQuerySet


class Sender(models.Model):
    name = models.CharField(max_length=50, unique=True)
    verbose_name = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField('URL', max_length=255, null=True, blank=True)
    icon = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):  # pragma: no cover
        return self.verbose_name or self.name.replace(
            '-', ' '
        ).replace(
            '_', ' '
        ).capitalize()


class Notification(models.Model):
    user = models.ForeignKey(
        'auth.User',
        related_name='notifications',
        on_delete=models.CASCADE
    )

    sender = models.ForeignKey(
        Sender,
        related_name='notifications',
        on_delete=models.SET_NULL,
        null=True
    )

    text = models.TextField()
    summary = models.CharField(max_length=255)
    kind = models.CharField(max_length=20, db_index=True)
    sent = models.DateTimeField(auto_now_add=True)
    email = models.BooleanField(default=True)
    read = models.BooleanField(default=False, db_index=True)

    objects = NotificationQuerySet.as_manager()

    def __str__(self):  # pragma: no cover
        return self.summary

    def send(self):
        channels.publish(
            'user.notifications',
            'create',
            self.kind,
            username=self.user.username,
            notification={
                'text': '' + self.text,
                'summary': '' + self.summary,
                'kind': self.kind
            },
            badge=self.user.notifications.unread().count()
        )

        channels.publish(
            'user.messages',
            'create',
            self.kind,
            username=self.user.username,
            kind=self.kind,
            text=self.summary
        )

    class Meta:
        ordering = ('-sent',)
        get_latest_by = 'sent'


class Tag(models.Model):
    notification = models.ForeignKey(
        Notification,
        related_name='tags',
        on_delete=models.CASCADE
    )

    slug = models.SlugField(max_length=100)
    description = models.CharField(max_length=100, null=True)

    def __str__(self):  # pragma: no cover
        return self.description or self.slug

    class Meta:
        unique_together = ('slug', 'notification')


class Action(models.Model):
    notification = models.ForeignKey(
        Notification,
        related_name='actions',
        on_delete=models.CASCADE
    )

    kind = models.CharField(max_length=20, db_index=True)
    text = models.CharField(max_length=100)
    url = models.URLField(max_length=512)
    ordering = models.PositiveIntegerField(default=0)

    def __str__(self):  # pragma: no cover
        return self.text

    class Meta:
        ordering = ('ordering',)
        unique_together = ('url', 'notification')


class UserPreference(models.Model):
    user = models.ForeignKey(
        'auth.User',
        related_name='notification_preferences',
        on_delete=models.CASCADE
    )

    tag = models.SlugField(max_length=100)
    email = models.BooleanField()

    class Meta:
        unique_together = ('tag', 'user')
