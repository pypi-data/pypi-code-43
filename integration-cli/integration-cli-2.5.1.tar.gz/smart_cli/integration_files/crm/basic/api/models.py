from django.db import models
from django.urls import reverse
from integration_utils.fields import UTF8JSONField


class Credential(models.Model):
    login = models.CharField(max_length=255, blank=True, null=True, default=None)
    main_user = models.CharField(max_length=255, default='main_name', blank=True, null=True)
    user_id = models.IntegerField()
    platform_id = models.CharField(max_length=100)
    client_service_id = models.CharField(max_length=100)

    class Meta:
        pass

    def __str__(self):
        return f"{self.login} - user_id:{self.user_id}, client_service_id:{self.client_service_id}"

    def get_absolute_url(self):
        return reverse('credential-detail', kwargs={"pk": self.pk})
