import logging

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db.models import EmailField, ManyToManyField
from django.utils.translation import gettext_lazy as _

from isc_common.auth.models.abstract_base_user import AbstractBaseUser
from isc_common.auth.models.usergroup import UserGroup
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class AbstractUser(AbstractBaseUser, AuditModel):
    username_validator = UnicodeUsernameValidator()

    username = CodeField(verbose_name=_('логин'), unique=True, validators=[username_validator], error_messages={'unique': _("Такой пользователь уже существует."), }, )
    first_name = NameField(verbose_name=_('имя'))
    last_name = NameField(verbose_name=_('фамилия'))
    email = EmailField(verbose_name=_('E-mail'), blank=True, null=True)
    middle_name = NameField(verbose_name=_('отчетво'))
    usergroup = ManyToManyField(UserGroup, verbose_name=_('группы'))


    @property
    def is_admin(self):
        res = False
        for group in self.usergroup.all():
            if group.is_admin:
                res = True
                break
        return res

    @property
    def is_develop(self):
        res = False
        for group in self.usergroup.all():
            if group.is_develop:
                res = True
                break
        return res

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def get_full_name(self):
        return f'{self.last_name.strip() if self.last_name else self.username} ' \
            f'{self.first_name.strip() if self.first_name else ""} ' \
            f'{self.middle_name.strip() if self.middle_name else ""}'

    @property
    def get_short_name(self):
        res = f'{self.last_name.strip() if self.last_name else self.username} ' \
            f'{self.first_name.strip()[0:1].upper() if self.first_name else ""} ' \
            f'{self.middle_name.strip()[0:1].upper() if self.middle_name else ""}'
        if res.strip() == "":
            res = self.username
        return res.strip()

    @property
    def get_short_name1(self):
        res = f'{self.first_name.strip()[0:1].upper() if self.first_name else ""} ' \
              f'{self.middle_name.strip()[0:1].upper() if self.middle_name else ""}'
        if res.strip() == "":
            res = self.username
        return res.strip()

    def user_short_name(self):
        return self.get_short_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
