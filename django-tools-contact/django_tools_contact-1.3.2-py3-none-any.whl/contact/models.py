from django.db import models
from django.utils.translation import gettext as _


class ContactInformation(models.Model):
    """
    This model will store the comapny places to be shown in a contact page
    """

    name = models.CharField(_('name'), max_length=255)
    address = models.TextField(_('address'))
    phone_number = models.CharField(
        _('phone number'),
        max_length=255,
        help_text=_("If there are more than one, separate them with commas"),
    )
    email = models.EmailField(_('email'))
    latitude = models.DecimalField(_('latitude'), max_digits=11, decimal_places=8)
    longitude = models.DecimalField(_('longitude'), max_digits=11, decimal_places=8)

    class Meta:
        verbose_name = _("Contact information")
        verbose_name_plural = _("Contact informations")

    def __str__(self):
        return self.name

    def get_phone_number(self):
        """
        Returns the phone_number in a list form.
        """
        return [phone.strip() for phone in self.phone_number.split(',')]


class ContactRequest(models.Model):
    """
    This model will manage the requests from the contact form
    """

    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    name = models.CharField(_('name'), max_length=255)
    email = models.EmailField(_('email'))
    phone_number = models.CharField(_('phone number'), max_length=255)
    message = models.TextField(_('message'))
    contacted = models.BooleanField(_('contacted'), default=False)

    class Meta:
        verbose_name = _("Contact request")
        verbose_name_plural = _("Contact requests")

    def __str__(self):
        return self.name

    @property
    def contact_information(self):
        if self.email and self.phone_number:
            return _("{email} or {phone_number}").format(
                email=self.email,
                phone_number=self.phone_number
            )
        if self.email:
            return self.email
        return self.phone_number
