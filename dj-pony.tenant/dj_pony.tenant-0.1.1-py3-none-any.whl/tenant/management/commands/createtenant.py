from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from dj_pony.tenant.helpers import create_tenant


class Command(BaseCommand):
    help = "Creates a new Tenant"

    def handle(self, *args, **options):
        name = input("Enter the Tenant name: ")
        slug = input("Enter the Tenant slug: (%s)" % slugify(name))
        domain = input("Enter the Tenant site: (localhost:8000)")

        # TODO: This doesnt appear to care about the length of the string.
        if not slug:
            slug = slugify(name)

        if not domain:
            domain = "localhost:8000"

        with transaction.atomic():
            create_tenant(name, slug, {}, [domain])

            self.stdout.write(
                self.style.SUCCESS("Successfully created Tenant %s" % name)
            )
