from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from dj_pony.tenant.helpers import create_tenant
from argparse import ArgumentParser
import ulid
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = "Creates a new Tenant"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--name', action='store', required=True)
        parser.add_argument('--slugify-name', action='store_true')
        parser.add_argument('--slug', action='store')
        parser.add_argument('--domain', action='store')
        parser.add_argument('--extra-data', action='store')
        parser.add_argument('--user', action='store')
        # parser.add_argument('--ulid', action='store')

    def handle(self, *args, **options):
        create_tenant_args: list = []
        name: str = options['name']
        slugify_name: bool = options['slugify-name']
        slug = options['slug']
        domain = options['domain']
        extra_data = options['extra-data']
        username: str = options['user']
        # _ulid = options['ulid']
        # ----------------------------------------
        ulid_fields = [
            # _ulid
        ]
        if slugify_name:
            slug = slugify(name)
        else:
            ulid_fields.append(slug)
        if None in ulid_fields:
            tenant_ulid = ulid.new()
            if slug is None:
                slug = tenant_ulid
            # if _ulid is None:
            #     _ulid = tenant_ulid
        # ----------------------------------------
        if domain is None:
            domain = 'localhost:8000'
        # ----------------------------------------
        if extra_data is None:
            extra_data = {}
        # ----------------------------------------
        if username is not None:
            user = User.objects.get(username=username)
        else:
            user = None
        # ----------------------------------------
        create_tenant_args.append(name)
        create_tenant_args.append(slug)
        create_tenant_args.append(extra_data)
        create_tenant_args.append([domain])
        # create_tenant_args.append(_ulid)
        create_tenant_args.append(user)
        # ----------------------------------------
        with transaction.atomic():
            create_tenant(*create_tenant_args)
            self.stdout.write(
                self.style.SUCCESS("Successfully created Tenant %s" % name)
            )
