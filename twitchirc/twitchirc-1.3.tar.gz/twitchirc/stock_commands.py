#  Library to make crating bots for Twitch chat easier.
#  Copyright (c) 2019 Maciej Marciniak
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import typing

import twitchirc


def get_no_permission_generator(bot: twitchirc.Bot):
    def permission_error_handler(event, msg: twitchirc.ChannelMessage,
                                 command: twitchirc.Command,
                                 missing_permissions: typing.List[str]):
        del event
        if command is None:
            return
        bot.send(msg.reply(f"@{msg.user} You are missing permissions ({', '.join(missing_permissions)}) to use "
                           f"command {command.chat_command}."))

    bot.handlers['permission_error'].append(permission_error_handler)


def get_perm_command(bot: twitchirc.Bot):
    @bot.add_command(command='perm', forced_prefix=None, enable_local_bypass=True,
                     required_permissions=[twitchirc.PERMISSION_COMMAND_PERM])
    def command_perm(msg: twitchirc.ChannelMessage):
        p = twitchirc.ArgumentParser(prog='!perm', add_help=False)
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument('-a', '--add', metavar=('USER', 'PERMISSION'), nargs=2, dest='add')
        g.add_argument('-r', '--remove', metavar=('USER', 'PERMISSION'), nargs=2, dest='remove')
        g.add_argument('-l', '--list', metavar='USER', const=msg.user, default=None, nargs='?', dest='list')
        g.add_argument('-h', '--help', action='store_true', dest='help')
        args = p.parse_args(args=msg.text.split(' ')[1:])
        if args is None or args.help:
            usage = msg.reply(f'@{msg.user} {p.format_usage()}')
            bot.send(usage)
            return
        if args.add:
            if bot.check_permissions(msg, [twitchirc.PERMISSION_COMMAND_PERM_ADD], enable_local_bypass=False):
                bot.send(msg.reply(f"@{msg.user} You cannot use !perm -a, since you don't have"
                                   f"the {twitchirc.PERMISSION_COMMAND_PERM_ADD} permission"))
                return
            if args.add[0] not in bot.permissions:
                bot.permissions[args.add[0]] = []
            if args.add[1] not in bot.permissions[args.add[0]]:
                bot.permissions[args.add[0]].append(args.add[1])
                bot.send(msg.reply(f'@{msg.user} Given permission {args.add[1]} to user {args.add[0]}.'))
            else:
                bot.send(msg.reply(f'@{msg.user} User {args.add[0]} already has permission {args.add[1]}.'))
                return
        elif args.remove:
            if bot.check_permissions(msg, [twitchirc.PERMISSION_COMMAND_PERM_REMOVE], enable_local_bypass=False):
                bot.send(msg.reply(f"@{msg.user} You cannot use !perm -r, since you don't have"
                                   f"the {twitchirc.PERMISSION_COMMAND_PERM_REMOVE} permission"))
                return
            if args.remove[0] not in bot.permissions:
                bot.permissions[args.remove[0]] = []
            if args.remove[1] not in bot.permissions[args.remove[0]]:
                bot.send(msg.reply(f"@{msg.user} User {args.remove[0]} already "
                                   f"doesn't have permission {args.remove[1]}."))
                return
            else:
                bot.permissions[args.remove[0]].remove(args.remove[1])
                bot.send(msg.reply(f'@{msg.user} Removed permission {args.remove[1]} from user {args.remove[0]}.'))
                return
        elif args.list:
            if bot.check_permissions(msg, [twitchirc.PERMISSION_COMMAND_PERM_LIST]):
                bot.send(msg.reply(f"@{msg.user} You cannot use !perm -l, since you don't have"
                                   f"the {twitchirc.PERMISSION_COMMAND_PERM_LIST} permission"))
                return
            args.list = args.list.lower()
            if args.list not in bot.permissions:
                bot.permissions[args.list] = []
            if args.list == msg.user:
                output = ', '.join(bot.permissions.get_permission_state(msg))
                bot.send(msg.reply(f'You have permissions: {output}'))
            else:
                output = ', '.join(bot.permissions[args.list])
                bot.send(msg.reply(f'User {args.list} has permissions: {output}'))

            return


def get_quit_command(bot: twitchirc.Bot):
    @bot.add_command(command='quit', forced_prefix=None, enable_local_bypass=False,
                     required_permissions=[twitchirc.PERMISSION_COMMAND_QUIT])
    def command_quit(msg: twitchirc.ChannelMessage):
        bot.send(msg.reply('Quitting.'))
        bot.stop()


def get_part_command(bot: twitchirc.Bot):
    @bot.add_command(command='part', forced_prefix=None,
                     required_permissions=[twitchirc.PERMISSION_COMMAND_PART])
    def command_part(msg: twitchirc.ChannelMessage):
        p = twitchirc.ArgumentParser(prog='!part', add_help=False)
        p.add_argument('channel', metavar='CHANNEL', nargs='?', const=msg.channel, default=msg.channel)
        p.add_argument('-h', '--help', action='store_true', dest='help')
        args = p.parse_args(msg.text.split(' ')[1:])
        if args is None or args.help:
            usage = msg.reply(f'@{msg.user} {p.format_usage()}')
            bot.send(usage)
            return
        if args.channel == '':
            args.channel = msg.channel
        channel = args.channel.lower()
        if channel != msg.channel.lower() and bot.check_permissions(msg, [twitchirc.PERMISSION_COMMAND_PART_OTHER],
                                                                    enable_local_bypass=False):
            bot.send(msg.reply(f"Cannot part from channel {channel}: your permissions are not valid in that channel."))
            return
        if channel not in bot.channels_connected:
            bot.send(msg.reply(f'Not in {channel}'))
            return
        else:
            bot.send(msg.reply(f'Parting from {channel}'))
            m = twitchirc.ChannelMessage('Bye.', 'OUTGOING', channel)
            m.outgoing = True
            bot.send(m)
            bot.flush_single_queue(msg.channel)
            bot.part(channel)


def get_join_command(bot: twitchirc.Bot):
    @bot.add_command(command='join', forced_prefix=None, enable_local_bypass=False,
                     required_permissions=[twitchirc.PERMISSION_COMMAND_JOIN])
    def command_join(msg: twitchirc.ChannelMessage):
        chan = msg.text.split(' ')[1].lower()
        if chan in ['all']:
            bot.send(msg.reply(f'Cannot join #{chan}.'))
            return
        if chan in bot.channels_connected:
            bot.send(msg.reply(f'This bot is already in channel #{chan}.'))
        else:
            bot.send(msg.reply(f'Joining channel #{chan}.'))
            bot.join(chan)
