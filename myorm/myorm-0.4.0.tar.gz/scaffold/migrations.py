import sys

from app import Migration

migration = Migration()

commands = {
    'run': migration.run_migrations,
    'create': migration.create_migrations
}

commands.get(sys.argv[1])()
