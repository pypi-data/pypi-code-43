# Imports from python.
from itertools import groupby
from io import BytesIO
from operator import itemgetter
import os


# Imports from Django.
from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.management.utils import parse_apps_and_model_labels
from django.db import DEFAULT_DB_ALIAS
from django.db import connections
# from django.db import router
from django.db import transaction


# Imports from other dependencies.
import crayons
from rest_framework.utils import model_meta


# Imports from civic_utils.
from civic_utils.conf import settings as civic_utils_settings
from civic_utils.management.helpers import ALLOWED_SERIALIZER_FORMATS
from civic_utils.management.helpers import FORMAT_EXTENSION_MAP
from civic_utils.management.helpers import TEMP_DIR
from civic_utils.models import CivicBaseModel
from civic_utils.utils.aws import get_bucket


NATURAL_KEY_SEPARATOR = '___'

S3_FIXTURE_BUCKET = civic_utils_settings.AWS_S3_BUCKET

S3_FIXTURE_ROOT_PATH = civic_utils_settings.FIXTURE_ROOT_PATH


def flatten_natural_key(model_dict, natural_key_fields):
    return NATURAL_KEY_SEPARATOR.join([
        model_dict[field] for field in natural_key_fields
    ])


def get_nk_fieldnames(model_klass, relation_fieldname):
    relation_field = model_klass._meta.get_field(relation_fieldname)

    if relation_field.is_relation and issubclass(model_klass, CivicBaseModel):
        return [
            f"{relation_field.name}__{nk_field}"
            for nk_field
            in relation_field.related_model.get_natural_key_fields()
        ]

    return []


class Command(BaseCommand):
    help = 'Installs the named fixture(s) in the database.'
    help = (
        "Import Civic data fixtures (either from a known S3 bucket location "
        "or a known local directory). "
    )

    def add_arguments(self, parser):
        # parser.add_argument(
        #     'args', metavar='fixture', nargs='+', help='Fixture labels.'
        # )
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help=(
                "Nominates a specific database to load fixtures into. "
                "Defaults to the 'default' database."
            ),
        )
        # parser.add_argument(
        #     '--ignorenonexistent', '-i', action='store_true', dest='ignore',
        #     help=(
        #         "Ignores entries in the serialized data for fields that "
        #         "do not currently exist on the model."
        #     ),
        # )
        parser.add_argument(
            '-e', '--exclude', action='append', default=[],
            help=(
                "An app_label or app_label.ModelName to exclude. "
                "Can be set multiple times."
            ),
        )
        parser.add_argument(
            '--format', default='json',
            help=(
                "Format of  zed data to be loaded. "
                "Defaults to the format of files in the specified source "
                "directory (if one and only one format exists at that path)."
            ),
        )
        parser.add_argument(
            '-l', '--local',
            action='store_true',
            dest='load_locally',
            help=(
                "Load fixtures from a local directory, rather than from S3."
            ),
        )
        parser.add_argument(
            '-t', '--test',
            action='store_true',
            dest='test_mode',
            help=(
                "Test mode: Only show what would change by loading fixtures "
                "(without making any changes to the database yet)."
            )
        )
        parser.add_argument(
            '-f', '--filename',
            default='export',
            dest='input_filename',
            help=(
                "Specifies filenames from which the fixtures are loaded. "
                "Defaults to 'export.json' (or 'export.xml', or other "
                "extensions based on the specified format). "
                "Useful if you want to store different versions of the same "
                "models' fixtures."
                "Note that this argument only sets the filename without file "
                "extension (as that is automatically configured) and without "
                "directory (as that is a known location, either on your local "
                "system or in an S3 bucket)."
            )
        )

    def handle(self, *fixture_labels, **options):
        # self.ignore = options['ignore']
        self.using = options['database']
        self.verbosity = options['verbosity']
        self.excluded_models, self.excluded_apps = parse_apps_and_model_labels(
            options['exclude']
        )
        self.format = options['format']
        self.load_locally = options['load_locally']
        self.test_mode = options['test_mode']
        self.input_filename = options['input_filename']

        if not self.load_locally:
            self.bucket = get_bucket(S3_FIXTURE_BUCKET)

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if self.format not in ALLOWED_SERIALIZER_FORMATS:
            try:
                serializers.get_serializer(self.format)
            except serializers.SerializerDoesNotExist:
                pass

                raise CommandError("Unknown serialization format: %s" % format)

        self.stdout.write("")
        self.stdout.write(crayons.magenta('Civic Data Importer', bold=True))
        self.stdout.write("")

        self.loadable_models = [
            (app_config, model_klass)
            for app_config in apps.get_app_configs()
            for model_klass in app_config.get_models()
            if issubclass(model_klass, CivicBaseModel)
        ]

        self.fixtures_to_load = self.find_fixtures()

        self.fixture_app_order = self.sort_fixture_imports()

        self.stdout.write('')
        self.stdout.write((
            "The following types and counts of models will be imported "
            f"({len(self.fixtures_to_load)} model types):"
        ))
        self.stdout.write('')

        self.fixtures_by_model = dict(
            (fixture['model_klass'], fixture)
            for fixture in self.fixtures_to_load
        )

        self.fixtures_to_create = {}
        self.fixtures_to_update = {}

        for model_config in self.fixture_app_order:
            (
                manager,
                fixtures_to_create,
                models_to_update,
                fields_to_update,
                post_create_manytomanys,
                post_update_manytomanys,
            ) = self.prepare_model_creation_and_updates(model_config)

            model_verbose_name = model_config._meta.verbose_name

            if not self.test_mode:
                with transaction.atomic(using=self.using):
                    if fixtures_to_create:
                        created_instance_count = len(fixtures_to_create)
                        created_plural = 's' if created_instance_count != 1 else ''
                        creating_message = (
                            f"Saving {created_instance_count} new "
                            f"{model_verbose_name} instance{created_plural}:"
                        )

                        self.stdout.write(
                            crayons.white(creating_message, bold=True),
                            ending='\r'
                        )
                        self.stdout.flush()

                        # Bulk-create new models.
                        manager.bulk_create(fixtures_to_create)

                        self.stdout.write('{} {}'.format(
                            crayons.white(creating_message, bold=True),
                            crayons.green("Done.", bold=True)
                        ))

                    if models_to_update:
                        updated_instance_count = len(models_to_update)
                        updated_plural = 's' if updated_instance_count != 1 else ''
                        updating_message = (
                            f"Saving {updated_instance_count} updated "
                            f"{model_verbose_name} instance{updated_plural}:"
                        )

                        self.stdout.write(
                            crayons.white(updating_message, bold=True),
                            ending='\r'
                        )
                        self.stdout.flush()

                        # Bulk-update existing (but stale) models.
                        manager.bulk_update(models_to_update, fields_to_update)

                        self.stdout.write('{} {}'.format(
                            crayons.white(updating_message, bold=True),
                            crayons.green("Done.", bold=True)
                        ))

                    self.stdout.write("")

            self.fixtures_to_create.setdefault(manager, fixtures_to_create)
            self.fixtures_to_update.setdefault(manager, models_to_update)

        # Close the DB connection -- unless we're still in a transaction. This
        # is required as a workaround for an edge case in MySQL: if the same
        # connection is used to create tables, load data, and query, the query
        # can return incorrect results. See Django #7572, MySQL #37735.
        if transaction.get_autocommit(self.using):
            connections[self.using].close()

    def find_fixtures(self):
        input_extension = FORMAT_EXTENSION_MAP[self.format]
        input_pattern = f"{self.input_filename}.{input_extension}"

        if not self.load_locally:
            all_remote_fixtures = self.bucket.objects.filter(
                Prefix=f'{S3_FIXTURE_ROOT_PATH}/'
            )
            root_path_length = len(S3_FIXTURE_ROOT_PATH)

            # The fixtures we'll attempt to load will be one level below the
            # 'S3_FIXTURE_ROOT_PATH' directory (in folders named for the models
            # they represent).
            # Within these model-specific folders, the fixtures we'll evaluate
            # must have the filename we're looking for -- which is the value of
            # 'input_pattern' as calculated above.
            matching_fixtures = [
                dict(
                    filename=fixture_file.key,
                    model_slug=os.path.split(
                        fixture_file.key
                    )[0][root_path_length:].strip(os.path.sep),
                ) for fixture_file in all_remote_fixtures
                if os.path.split(fixture_file.key)[1] == input_pattern
                and fixture_file.key[:root_path_length] == S3_FIXTURE_ROOT_PATH
            ]
        else:
            temporary_dir_subdirectories = [
                os.path.join(TEMP_DIR, item_path)
                for item_path in os.listdir(TEMP_DIR)
                if os.path.isdir(os.path.join(TEMP_DIR, item_path))
            ]
            matching_fixtures = [
                dict(
                    filename=os.path.join(subdirectory, input_pattern),
                    model_slug=subdirectory[len(TEMP_DIR):].strip(os.path.sep),
                )
                for subdirectory in temporary_dir_subdirectories
                if os.path.isfile(os.path.join(subdirectory, input_pattern))
            ]

        model_slug_map = dict(
            (model_klass._meta.model_name, (app_config, model_klass))
            for (app_config, model_klass) in self.loadable_models
        )

        # Add app and model configurations to fixture context.
        full_context_matching_fixtures = [
            dict(
                app_config=model_slug_map[fixture_config['model_slug']][0],
                model_klass=model_slug_map[fixture_config['model_slug']][1],
                **fixture_config,
            )
            for fixture_config in matching_fixtures
            if fixture_config['model_slug'] in model_slug_map
        ]

        # Filter out fixtures that have been explicitly excluded.
        finalized_matching_fixtures = [
            fixture_config for fixture_config in full_context_matching_fixtures
            if fixture_config['app_config'] not in self.excluded_apps
            and fixture_config['model_klass'] not in self.excluded_models
        ]

        return finalized_matching_fixtures

    def sort_fixture_imports(self):
        app_sorted_fixtures = sorted(
            self.fixtures_to_load,
            key=lambda x: x['app_config'].name
        )

        to_import_list = dict(
            (app_config, [model_cfg['model_klass'] for model_cfg in group])
            for app_config, group in groupby(
                app_sorted_fixtures,
                itemgetter('app_config')
            )
        )

        return serializers.sort_dependencies(to_import_list.items())

    def load_fixture(self, fixture_config):
        if not self.load_locally:
            s3_fileobj = self.bucket.Object(key=fixture_config['filename'])
            with BytesIO(s3_fileobj.get()['Body'].read()) as fixture_input:
                deserialized_data = fixture_config['model_klass'].deserialize(
                    self.format,
                    fixture_input
                )

        with open(fixture_config['filename'], 'rb') as fixture_input:
            deserialized_data = fixture_config['model_klass'].deserialize(
                self.format,
                fixture_input
            )

        return deserialized_data

    def prepare_model_creation_and_updates(self, model_config):
        fixture_config = self.fixtures_by_model[model_config]
        fixture_models = self.load_fixture(fixture_config)

        model_klass = fixture_config['model_klass']

        model_manager = model_klass._default_manager
        model_metadata = model_meta.get_field_info(model_klass)

        nk_fields = model_klass.get_natural_key_fields()

        pk_field = model_klass._meta.pk.name

        compared_fields = ['updated', *nk_fields]

        existing_instance_fields = model_manager.values(
            pk_field,
            *compared_fields
        )
        fixture_model_dicts = [
            {
                '_instance': fixture_instance,
                **fixture_instance.object.__dict__,
                **dict(
                    list(*zip(
                        get_nk_fieldnames(model_klass, relation_fieldname),
                        natural_key_parts
                    ))
                    for relation_fieldname, natural_key_parts
                    in fixture_instance.m2m_data.items()
                ),
                **dict(
                    list(*zip(
                        get_nk_fieldnames(model_klass, relation_fieldname),
                        natural_key_parts
                    ))
                    for relation_fieldname, natural_key_parts
                    in fixture_instance.deferred_fields.items()
                ),
            }
            for fixture_instance in fixture_models
        ]
        fixture_instance_fields = [
            {
                '_instance': fixture_dict['_instance'],
                **{
                    field_name: fixture_dict[field_name]
                    for field_name in compared_fields
                }
            }
            for fixture_dict in fixture_model_dicts
        ]

        existing_summary = {
            flatten_natural_key(instance, nk_fields): instance['updated']
            for instance in existing_instance_fields
        }
        existing_natural_key_id_map = {
            flatten_natural_key(instance, nk_fields): instance[pk_field]
            for instance in existing_instance_fields
        }
        fixture_summary = {
            flatten_natural_key(instance, nk_fields): instance['updated']
            for instance in fixture_instance_fields
        }
        fixture_model_instances = {
            flatten_natural_key(instance, nk_fields): instance['_instance']
            for instance in fixture_instance_fields
        }

        only_existing = existing_summary.keys() - fixture_summary.keys()
        only_fixture = fixture_summary.keys() - existing_summary.keys()
        overlapping_instances = set(
            fixture_summary.keys()
        ).intersection(existing_summary.keys())

        existing_newer = []
        fixture_newer = []
        equal_age = []

        for natural_key in overlapping_instances:
            existing_updated_date = existing_summary[natural_key]
            fixture_updated_date = fixture_summary[natural_key]

            if existing_updated_date > fixture_updated_date:
                existing_newer.append(natural_key)
            elif existing_updated_date < fixture_updated_date:
                fixture_newer.append(natural_key)
            else:
                equal_age.append(natural_key)


        self.stdout.write('')
        self.stdout.write(crayons.yellow(
            f"[{model_klass._meta.label}]",
            bold=True
        ))
        self.stdout.write('')
        self.stdout.write(f"-   Only in database: {len(only_existing)}")
        self.stdout.write(
            f"-   In both; database newer: {len(existing_newer)}"
        )
        self.stdout.write(f"-   In both; equal age: {len(equal_age)}")
        self.stdout.write(crayons.cyan(
            f"-   * In both; fixture newer: {len(fixture_newer)}", bold=True
        ))
        self.stdout.write(crayons.cyan(
            f"-   * Only in fixture: {len(only_fixture)}", bold=True
        ))
        self.stdout.write('')

        total_modifications = len(fixture_newer) + len(only_fixture)
        if total_modifications > 0:
            self.stdout.write(crayons.cyan(
                f"    * Total to be saved: {total_modifications}", bold=True
            ))
            self.stdout.write('')

        current_related_model_keys = {}
        for related_field_name in model_metadata.relations.keys():
            related_field = model_klass._meta.get_field(related_field_name)
            related_model = related_field.related_model

            raw_related_values = related_model._default_manager.values(
                related_model._meta.pk.name,
                *related_model.get_natural_key_fields()
            )

            current_related_model_keys[related_field.name] = dict((
                flatten_natural_key(
                    related_instance,
                    related_model.get_natural_key_fields()
                ),
                related_instance[related_model._meta.pk.name]
            )  for related_instance in raw_related_values)

        fixtures_to_be_created = []
        models_to_be_updated = []
        fields_used_in_update = set()

        if fixture_newer:
            models_needing_update = model_manager.filter(
                **{f"{pk_field}__in": [
                    existing_natural_key_id_map[natural_key]
                    for natural_key in fixture_newer
                ]}
            )
        else:
            models_needing_update = model_manager.none()

        existing_id_instance_map = {
            getattr(instance, pk_field): instance
            for instance in models_needing_update
        }

        # Calculate which fields we can and should update on this model.
        allowed_update_fields = [
            field_config.name
            for field_config in model_klass._meta.get_fields()
            # 1. No auto-created (reverse-direction relational) fields.
            if not field_config.auto_created
            # 2. No primary keys.
            and not field_config.primary_key
            # 3. No fields used to calculate PKs.
            and field_config.name
            not in model_klass.get_natural_key_definition()
        ]

        for instance_key, instance_data in fixture_model_instances.items():
            if instance_key in only_fixture:
                evaluated = self.evaluate_deferred(
                    model_klass,
                    current_related_model_keys,
                    instance_data
                )
                fixtures_to_be_created.append(evaluated)
            elif instance_key in fixture_newer:
                updated_instance = self.evaluate_deferred(
                    model_klass,
                    current_related_model_keys,
                    instance_data
                )
                current_pk = existing_natural_key_id_map[instance_key]
                current_instance = existing_id_instance_map[current_pk]

                apply_instance_update = False

                for field_to_update in allowed_update_fields:
                    current_value = getattr(current_instance, field_to_update)
                    updated_value = getattr(updated_instance, field_to_update)

                    if current_value != updated_value:
                        apply_instance_update = True
                        fields_used_in_update.add(field_to_update)
                        setattr(
                            current_instance,
                            field_to_update,
                            updated_value
                        )

                if apply_instance_update:
                    models_to_be_updated.append(current_instance)

        return (
            model_manager,
            fixtures_to_be_created,
            models_to_be_updated,
            list(fields_used_in_update),
            [],  # Post-create M2Ms.
            [],  # Post-edit M2Ms.
        )

    def evaluate_deferred(self, model_klass, related_id_maps, instance):
        for deferred_field, natural_key in instance.deferred_fields.items():
            related_field = model_klass._meta.get_field(deferred_field)
            rel_nk_parts = related_field.related_model.get_natural_key_fields()
            rel_nk_values = dict(zip(rel_nk_parts, natural_key))

            flat_natural_key = flatten_natural_key(rel_nk_values, rel_nk_parts)

            if deferred_field not in related_id_maps:
                raise ValueError(
                    "Could not find natural-key to ID mapping for "
                    f"'{deferred_field}' field."
                )
            elif flat_natural_key not in related_id_maps[deferred_field]:
                self.stdout.write('{}{}'.format(
                    crayons.red('WARNING: ', bold=True),
                    (
                        "No match was found for field "
                        f"'{deferred_field}' and natural key "
                    )
                ))
                self.stdout.write(f"         '{natural_key}' when creating or modifying ")
                self.stdout.write(
                    f"         a(n) '{model_klass._meta.label}' "
                    "model instance."
                )
                self.stdout.write('')
                self.stdout.write("         Records of this relationship may be lost.")
                self.stdout.write('')
                continue

            pk_for_relation = related_id_maps[deferred_field][flat_natural_key]

            setattr(instance.object, f"{deferred_field}_id", pk_for_relation)

        return instance.object
