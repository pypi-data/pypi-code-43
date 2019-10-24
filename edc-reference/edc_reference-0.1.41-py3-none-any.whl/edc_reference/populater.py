import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style
from tqdm import tqdm

from .reference import ReferenceUpdater
from .site_reference import site_reference_configs, SiteReferenceConfigError

style = color_style()


class PopulaterAttributeError(Exception):
    pass


class DryRunDummy:
    def __init__(self, **kwargs):
        pass


class Populater:

    reference_updater_cls = ReferenceUpdater

    def __init__(
        self,
        names=None,
        exclude_names=None,
        skip_existing=None,
        dry_run=None,
        delete_existing=None,
    ):
        self.skip_existing = skip_existing
        self.delete_existing = delete_existing
        names = names or list(site_reference_configs.registry)
        exclude_names = [n.strip() for n in exclude_names or []]
        self.names = self.verify_names(
            [n.strip() for n in names if n not in exclude_names]
        )
        self.dry_run = dry_run

    @property
    def reference_model_cls(self):
        return django_apps.get_model("edc_reference.reference")

    def summarize(self):
        for name in self.names:
            reference_model = site_reference_configs.get_reference_model(name=name)
            reference_model_cls = django_apps.get_model(reference_model)
            count = reference_model_cls.on_site.filter(model=name).count()
            sys.stdout.write(f" * {name}: {count} records\n")

    def populate(self):
        """Populates or re-populates model `Reference` for the
        current site.
        """
        if self.dry_run:
            self.reference_updater_cls = DryRunDummy
        sys.stdout.write(style.MIGRATE_HEADING(f"Populating reference model.\n"))
        sys.stdout.write(f" - Current site is {settings.SITE_ID}\n")
        sys.stdout.write(
            f" - found {len(site_reference_configs.registry)} reference names in registry.\n"
        )
        sys.stdout.write(
            f" - running for {len(self.names)} selected reference names.\n"
        )
        if self.skip_existing:
            sys.stdout.write(f" - skipping reference names with existing references\n")
        if self.dry_run:
            sys.stdout.write(
                f" - This is a dry run. No data will be created/modified.\n"
            )

        if self.delete_existing:
            self.delete_existing_references()

        self.update_references()

        sys.stdout.write(f"Done (Site {settings.SITE_ID}).\n")

    def update_references(self):
        """Create or Update all Reference instances for
        model names from this sites reference_configs.
        """
        for name in self.names:
            qs = self.get_queryset(name)
            total = qs.count()
            for model_obj in tqdm(qs, total=total, desc=name):
                try:
                    self.reference_updater_cls(model_obj=model_obj)
                except SiteReferenceConfigError as e:
                    if "Model not registered" in str(e):
                        pass
                    else:
                        raise

    def delete_existing_references(self):
        """Delete existing `Reference` model instances for
        model names from this sites reference_configs.
        """
        sys.stdout.write(f" * deleting existing records ... \r")
        if not self.dry_run:
            for name in self.names:
                self.reference_model_cls.on_site.filter(model=name).delete()
        sys.stdout.write(f" * deleting existing records ... done.\n")

    def verify_names(self, names):
        """Returns a list of model names from the sites
        reference_configs.

        Format is `app_label.model_name` or
        `app_label.model_name.panel_name`.
        """
        names_registered = []
        names_not_registered = []
        for name in [name for name in names if not self.skip(name=name)]:
            try:
                site_reference_configs.get_config(name=name)
            except SiteReferenceConfigError as e:
                if "Model not registered" in str(e):
                    names_not_registered.append(name)
                else:
                    raise
            else:
                names_registered.append(name)
        sys.stdout.write(f" - registered models are {', '.join(names_registered)}\n")
        if names_not_registered:
            sys.stdout.write(
                style.ERROR(
                    f" - unregistered models are {','.join(names_not_registered)}\n"
                )
            )
        return names_registered

    def get_queryset(self, name=None):
        """Returns a QuerySet filter for this site given the
        `app_label.model_name` or `app_label.model_name.panel_name`.
        """
        try:
            app_label, model_name, panel_name = name.split(".")
        except ValueError:
            panel_name = None
            app_label, model_name = name.split(".")
        model_cls = django_apps.get_model(app_label, model_name)
        if panel_name:
            qs = model_cls.on_site.filter(panel__name=panel_name)
        else:
            qs = model_cls.on_site.all()
        return qs

    def skip(self, name=None):
        if self.skip_existing:
            reference_model = site_reference_configs.get_reference_model(name=name)
            reference_model_cls = django_apps.get_model(reference_model)
            return reference_model_cls.on_site.filter(model=name).exists()
        return False
