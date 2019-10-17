import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.init_fields()
        self.init_menu()
        self.create_user("dev", "dev", "123456")
        self.create_user("root", "root", "123456", True)

    @staticmethod
    def init_menu():
        from redmin.models import Menu, Domain, DomainMenu
        menu = Menu.objects.update_or_create(name="ROOT")[0]
        domains = list(Domain.objects.filter(app='redmin').all())
        sequence = 0
        for domain in domains:
            DomainMenu.objects.update_or_create(domain=domain, menu=menu)
            domain.sequence = sequence
            sequence += 5
        Domain.objects.bulk_update(domains, fields=['sequence'])

    @staticmethod
    def init_fields():
        from redmin.models import Field
        fields = list(Field.objects.filter(base__name="User"))
        for field in fields:
            flag = field.attribute in ['group', 'usename', 'title']
            field.formable = field.listable = flag
            field.list_editable = field.form_editable = False
        Field.objects.bulk_update(fields, fields=['formable', 'listable', 'list_editable', 'form_editable'])

        fields = list(Field.objects.filter(base__name="Field"))
        for field in fields:
            flag = field.attribute.endswith("able") or field.attribute.endswith("sequence")
            field.formable = field.list_editable = flag
            field.listable = field.attribute not in ['python_type', 'help_text', 'default', 'max_length', 'nullable', 'exportable', 'data_type', 'unique']
            if field.attribute == "group_sequence":
                field.sequence = 4

        Field.objects.bulk_update(fields, fields=['formable', 'listable', 'list_editable', 'sequence'])

        fields = list(Field.objects.filter(attribute="id"))
        for field in fields:
            field.listable = False
        Field.objects.bulk_update(fields, fields=['listable'])

    @staticmethod
    def create_user(group_name, username, password, super_user=False):
        from redmin.models import Group, User, GroupPermission, SuperPermissionModel, Domain
        root_group = Group.objects.update_or_create(name=group_name)[0]
        user = User.objects.filter(username=username).first()
        if not user:
            user = User(group=root_group, username=username, title=username)
            user.set_password(password)
            user.save()
            logger.info(f"root user created:username={username},password={password}")

        if super_user:
            domain = Domain.objects.filter(name=SuperPermissionModel.__name__).first()
            permission = GroupPermission.objects.filter(group=root_group, domain=domain).first()
            if not permission:
                GroupPermission.objects.create(
                    group=root_group,
                    domain=domain,
                    creatable=True,
                    savable=True,
                    removable=True,
                    cloneable=True,
                    exportable=True,
                    viewable=True,
                    listable=True,
                )
