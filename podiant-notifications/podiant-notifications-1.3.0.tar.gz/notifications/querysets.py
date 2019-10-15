from django.db.models import QuerySet


class NotificationQuerySet(QuerySet):
    def unread(self):
        return self.filter(read=False)

    def read(self):
        return self.filter(read=True)
