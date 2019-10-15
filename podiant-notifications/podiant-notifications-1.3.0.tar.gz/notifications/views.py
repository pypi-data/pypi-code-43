from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from pubsub import channels
from .models import Notification


class NotificationListView(ListView):
    model = Notification

    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user
        )

    def get(self, request, *args, **kwargs):
        from django.http.response import HttpResponseBadRequest

        action = request.GET.get('action')
        if action == 'delete':
            self.get_queryset().delete()
        elif action == 'read':
            self.get_queryset().update(read=True)
        elif action:
            return HttpResponseBadRequest('Unknown or unspecified action')

        if action:
            channels.publish(
                'user.notifications',
                'update',
                username=request.user.username,
                badge=request.user.notifications.unread().count()
            )

        return super().get(request, *args, **kwargs)


class NotificationDetailView(DetailView):
    model = Notification

    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user
        )

    def get(self, request, *args, **kwargs):
        from django.http.response import HttpResponseBadRequest

        action = request.GET.get('action')
        self.object = self.get_object()

        if action == 'delete':
            self.object.delete()
        elif action == 'read':
            self.object.read = True
            self.object.save(update_fields=('read',))
        else:
            return HttpResponseBadRequest('Unknown or unspecified action')

        channels.publish(
            'user.notifications',
            'update',
            username=request.user.username,
            badge=request.user.notifications.unread().count()
        )

        return self.render_to_response(
            self.get_context_data(
                object=self.object
            )
        )
