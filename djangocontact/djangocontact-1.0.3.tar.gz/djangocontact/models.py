from django.db import models
from .validators import validate_subject


""" Start EmailModel here."""
# Start receive email model here.
class EmailModel(models.Model):
    email      = models.EmailField(max_length=55, blank=False, null=False)
    full_name     = models.CharField(max_length=20, blank=False, null=False)
    content       = models.TextField(max_length=250, blank=False, null=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    # str methode here.
    def __str__(self):
        return self.full_name

    # meta class here.
    class Meta:
        ordering = ['pk']
        verbose_name = "Email"
        verbose_name_plural = "Emails"