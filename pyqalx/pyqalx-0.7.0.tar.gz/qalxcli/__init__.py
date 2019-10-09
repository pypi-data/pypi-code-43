from importlib import import_module
from os import getcwd
from pprint import pprint

import click
import sys
from click import ClickException

from pyqalx import Bot, QalxSession
from pyqalx.config import UserConfig, BotConfig, QalxConfigProfileNotFound, \
    QalxConfigFileNotFound


@click.group(chain=True)
@click.option(
    '-u', '--user-profile',
    help='User profile name in .qalx.',
    default="default"
)
@click.option(
    '-b', '--bot-profile',
    help='Bot profile name in .bots.',
    default="default"
)
@click.pass_context
def qalx(ctx, user_profile, bot_profile):
    """Command line interface to qalx."""
    ctx.ensure_object(dict)
    ctx.obj['USER_PROFILE'] = user_profile
    ctx.obj['BOT_PROFILE'] = bot_profile
    sys.path.append(getcwd())


@qalx.command("start-bot")
@click.option(
    '-p', '--processes',
    help='The number of workers to spawn in the bot.',
    default=1
)
@click.option(
    '--skip-ini/--no-skip-ini',
    help='Should the bot use the profiles on disk?',
    default=False
)
@click.option(
    '--add-queue/--no-add-queue',
    help="Should the bot try and create the queue if it doesn't exist?",
    default=True
)
@click.argument("target")
@click.pass_context
def start(ctx, target, processes, skip_ini, add_queue):
    """
    start the bot at TARGET.

    This is the import path with a colon followed by the variable name of the bot. e.g. `my_qalx.my_bot:bot`
    """
    bot_module_name, bot_variable_name = target.split(":")
    bot_module = import_module(bot_module_name)

    if bot_variable_name not in dir(bot_module):
        raise ClickException(f"{bot_variable_name} not found in {bot_module_name}.")
    else:
        bot = getattr(bot_module, bot_variable_name)
        if not isinstance(bot, Bot):
            raise ClickException(f"{bot_variable_name} isn't an instance of Bot.")
        click.echo(f"Starting {bot.name} reading from {bot.queue_name} with"
                   f" {processes} workers.")
        user_profile = ctx.obj.get("USER_PROFILE", "default")
        bot_profile = ctx.obj.get("BOT_PROFILE", "default")
        bot.start(user_profile_name=user_profile,
                  bot_profile_name=bot_profile,
                  processes=int(processes),
                  skip_ini=skip_ini,
                  add_queue=add_queue)


@qalx.command("terminate-bot")
@click.argument("name")
@click.pass_context
def terminate_bot(ctx, name):
    """shutdown the bot named NAME"""
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_kill = qalx_session.bot.find_one(name=name)
    qalx_session.bot.terminate(bot_to_kill)
    click.echo(f"Terminated {name}")


@qalx.command("stop-bot")
@click.argument("name")
@click.pass_context
def stop_bot(ctx, name):
    """stop the bot named NAME.

    All workers to stop pulling jobs from the queue.
    """
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_stop = qalx_session.bot.find_one(name=name)
    qalx_session.bot.stop(bot_to_stop)
    click.echo(f"Stopping {name}.")


@qalx.command("resume-bot")
@click.argument("name")
@click.pass_context
def resume_bot(ctx, name):
    """resume the bot named NAME.

    All workers to start pulling jobs from the queue.
    """
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_resume = qalx_session.bot.find_one(name=name)
    qalx_session.bot.resume(bot_to_resume)
    click.echo(f"Resuming {name}.")


@qalx.command("bot-info")
@click.argument("name")
@click.pass_context
def bot_info(ctx, name):
    """print info about the bot named NAME.

    """
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_info = qalx_session.bot.find_one(name=name)
    click.echo(pprint(bot_to_info))


@qalx.command("terminate-workers")
@click.argument("bot_name")
@click.argument("number")
@click.pass_context
def terminate_workers(ctx, bot_name, number):
    """terminate NUMBER of workers on bot named BOT_NAME."""
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_kill = qalx_session.bot.find_one(name=bot_name)
    if int(number) > len(bot_to_kill['workers']):
        raise ClickException(
            f"{number} is more than the number of workers on {bot_name} ({len(bot_to_kill['workers'])})")
    for n in range(int(number)):
        qalx_session.worker.terminate(bot_to_kill['workers'][n], bot_entity=bot_to_kill)
        click.echo(f"Terminated {n + 1} worker.")


@qalx.command('configure')
@click.option('--user/--no-user', default=True)
@click.option('--bot/--no-bot', default=True)
@click.argument('extra', nargs=-1)
@click.pass_context
def configure(ctx, user, bot, extra):
    """
    Configures the .qalx and .bots config files.
    Usage:

    `qalx configure` - configures user and bot default profiles

    `qalx --user-profile=dev configure` - configures dev user profile and
    default bot profile

    `qalx --bot-profile=dev configure --no-user` - only configures bot dev
    profile.  Doesn't configure user profile

    `qalx configure --no-bot customkey=customvalue customkey2=customvalue2`
    - configures user profile with two extra key/values pairs on the config
    """

    if not user and not bot:
        raise ClickException('`user` or `bot` must be specified otherwise no '
                             'config files can be created.  Either call '
                             'without any arguments or only use a '
                             'single `--no-user` or `--no-bot` switch')

    user_profile = ctx.obj["USER_PROFILE"]
    bot_profile = ctx.obj["BOT_PROFILE"]
    check_existing = []

    if user:
        check_existing.append((UserConfig, user_profile, 'user'),)
    if bot:
        check_existing.append((BotConfig, bot_profile, 'bot'))

    for ConfigClass, profile_name, config_type in check_existing:
        # If the profiles already exist we just exit.  It's up to the user
        # to make any changes manually to the profile file - otherwise we risk
        # parsing the file incorrectly and overwriting data the user wants to
        # keep
        try:
            ConfigClass().from_inifile(profile_name)
            config_path = ConfigClass.config_path()
            raise ClickException(f'`{profile_name}` profile for config stored '
                                 f'at `{config_path}` '
                                 f'already exists.  To make changes you must '
                                 f'edit the config file directly or specify a '
                                 f'`--no-{config_type}` flag')
        except (QalxConfigProfileNotFound, QalxConfigFileNotFound):
            # QalxConfigProfileNotFound: The specific profile could not be
            #                            found in the given ConfigClass file
            # QalxConfigFileNotFound: The specific file could not be found
            #                         for the given ConfigClass
            pass

    config_items = {}

    for item in extra:
        # Handles the user being able to pass in extra key/value pairs to write
        # to the config file
        split_item = item.split('=', 1)
        if len(split_item) != 2:
            raise ClickException(f'extra arguments must be in the format '
                                 f'`key=value`.  Got `{item}`')
        config_items[split_item[0].upper()] = split_item[1]

    if user:
        value = click.prompt('qalx Token', type=str)
        config_items['TOKEN'] = value
        UserConfig.configure(user_profile, config_items)
    if bot:
        BotConfig.configure(bot_profile)
