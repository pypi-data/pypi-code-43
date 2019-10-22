import asyncio
import getpass

from sqlalchemy.engine.url import URL

from aio_manager import Command


class CreateSuperuser(Command):
    """
    Создать учетную запись супер-пользователя
    """

    _app = None

    def __init__(self, app):
        super().__init__('create_superuser', app)

    @staticmethod
    async def _get_dsn(config):
        if config.get('dsn'):
            dsn = config['dsn']
        else:
            dsn = URL(
                drivername=config.setdefault('driver', 'asyncpg'),
                host=config.setdefault('host', 'localhost'),
                port=config.setdefault('port', 5432),
                username=config.setdefault('user', 'postgres'),
                password=config.setdefault('password', ''),
                database=config.setdefault('database', 'postgres'),
            )
        return dsn

    async def _create_superuser(self, **kwargs):
        gino_config = self._app['config'].get('gino', {})

        dsn = await self._get_dsn(gino_config)

        await self._app['db'].set_bind(
            dsn,
            echo=gino_config.setdefault('echo', False),
            min_size=gino_config.setdefault('pool_min_size', 5),
            max_size=gino_config.setdefault('pool_max_size', 10),
        )
        await self._app['auth'].get_user_model().create(**kwargs)

    def run(self, app, args):
        self._app = app

        loop = asyncio.get_event_loop()

        if not args.password:
            args.password = getpass.getpass()

        loop.run_until_complete(self._create_superuser(**{
            'username': args.username,
            'password': args.password,
        }))

    def configure_parser(self, parser):
        super().configure_parser(parser)
        parser.add_argument('--username', type=str, required=True, metavar='USERNAME',
                            help='Superuser login (username)')
        parser.add_argument('-p', '--password', type=str, metavar='PASSWORD')
