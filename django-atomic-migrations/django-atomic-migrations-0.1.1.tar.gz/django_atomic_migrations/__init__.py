# -* encoding: utf-8 *-

name = "django_atomic_migrations"

from django.apps.config import AppConfig

def _monkey_patch():
    from django.db.migrations.executor import MigrationExecutor
    from django.db import transaction

    apply_migration = MigrationExecutor.apply_migration
    def _apply_migration(self, *args, **kwargs):
        with transaction.atomic():
            return apply_migration(self, *args, **kwargs)
    MigrationExecutor.apply_migration = _apply_migration

    unapply_migration = MigrationExecutor.unapply_migration
    def _unapply_migration(self, *args, **kwargs):
        with transaction.atomic():
            return unapply_migration(self, *args, **kwargs)
    MigrationExecutor.unapply_migration = _unapply_migration

    from django.db.migrations.recorder import MigrationRecorder
    MigrationRecorder.Migration._meta.unique_together = (('app', 'name'),)


class AtomicMigrations(AppConfig):
    name = "django_atomic_migrations"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._patched = False

    def ready(self) -> None:
        if not self._patched:
            _monkey_patch()
            self._patched = True
