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

import atexit
import sched
import select
import typing

import twitchirc  # Import self.


class Bot(twitchirc.Connection):
    def schedule_event(self, delay, priority, function, args: tuple, kwargs: dict):
        return self.scheduler.enter(delay, priority, function, args, kwargs)

    def schedule_event_absolute(self, time, priority, function, args: tuple, kwargs: dict):
        return self.scheduler.enterabs(time, priority, function, args, kwargs)

    def schedule_repeated_event(self, delay, priority, function, args: tuple, kwargs: dict):
        def run_event():
            function()
            self.scheduler.enter(delay, priority, run_event, args, kwargs)
        return self.scheduler.enter(delay, priority, run_event, args, kwargs)

    def run_commands_from_file(self, file_object):
        lines = file_object.readlines()
        user = 'rcfile'
        channel = 'rcfile'
        self._in_rc_mode = True
        for num, i in enumerate(lines):
            i: str = i.replace('\n', '')
            if i.startswith('@'):
                if i.startswith('@at'):
                    channel = i.replace('@at ', '')
                elif i.startswith('@as'):
                    user = i.replace('@as ', '')
                continue
            m = twitchirc.ChannelMessage(user=user, channel=channel, text=i)
            m.flags = {
                'badge-info': '',
                'badges': 'moderator/1',
                'display-name': 'RCFile',
                'id': '00000000-0000-0000-0000-{:0>12}'.format(num),
                'user-id': 'rcfile',
                'emotes': ''
            }
            self._call_command_handlers(m)
        self._in_rc_mode = False

    def __init__(self, address, username: str, password: typing.Union[str, None] = None, port: int = 6667,
                 no_connect=False, storage=None, no_atexit=False):
        """
        A bot class.

        :param address: Address to connect to
        :param username: Username to use
        :param password: Password if needed.
        :param port: Irc port.
        :param no_connect: Don't connect to the chat straight away
        :param storage: twitchirc.Storage compatible object to use as the storage.
        """
        super().__init__(address, port, no_atexit=True)
        self.scheduler = sched.scheduler()
        self._in_rc_mode = False
        if not no_connect:
            self.connect(username, password)
        self.username = username
        self._password = password
        self.commands: typing.List[twitchirc.Command] = []
        self.handlers: typing.Dict[str, typing.List[typing.Callable]] = {
            'pre_disconnect': [],
            'post_disconnect': [],
            'pre_save': [],
            'post_save': [],
            'start': [],
            'recv_join_msg': [],
            'recv_part_msg': [],
            'recv_ping_msg': [],
            'permission_error': [],
            'any_msg': [],
            'chat_msg': []
        }
        """
        A dict of handlers

        Available handlers:

        * pre_disconnect, args: ()
        * post_disconnect, args: ()
        * pre_save, args: ()
        * post_save, args: ()
        * start, args: ()
        * permission_error, args: (message, command, missing_permissions)
          -> message the ChannelMessage during which this permission_error was triggered.
          -> command the Command object that triggered it.
             WARN: `command` can be None if `check_permissions` was called (not `check_permissions_from_command`).
          -> missing_permissions permissions that are missing to run the command.
        * any_msg, args: (message)
        * chat_msg, args: (message)
        """

        self.prefix = '!'
        self.storage = storage
        self.on_unknown_command = 'ignore'
        """
        Action to take when an unknown command is encountered.
        Warning: This doesn't apply to commands with a forced prefix.

        Available handlers:

        * ignore - ignore it (default)
        * warn - print a warning to stdout
        * chat_message - send a chat message saying that the command is invalid.
        """
        self.permissions = twitchirc.PermissionList()
        if no_atexit:
            @atexit.register
            def close_self():
                try:
                    self.stop()
                except:
                    pass

    def add_command(self, command: str,
                    forced_prefix: typing.Optional[str] = None,
                    enable_local_bypass: bool = True,
                    required_permissions: typing.List[str] = []) \
            -> typing.Callable[[typing.Callable[[twitchirc.ChannelMessage],
                                                typing.Any]], twitchirc.Command]:
        # I'm sorry if you are reading this definition
        # here's a better version
        #  -> ((twitchirc.ChannelMessage) -> Any) -> Command
        """
        Add a command to the bot.
        This function is a decorator.

        :param command: Command to be registered.
        :param forced_prefix: Force a prefix to on this command. This is useful when you can change the prefix in the
        bot.
        :param enable_local_bypass: If False this function will ignore the permissions
        `twitchirc.bypass.permission.local.*`. This is useful when creating a command that can change global settings.
        :param required_permissions: Permissions required to run this command.
        :return: The `function` parameter. This is for using this as a decorator.
        """

        def decorator(func: typing.Callable) -> twitchirc.Command:
            cmd = twitchirc.Command(chat_command=command,
                                    function=func, forced_prefix=forced_prefix, parent=self,
                                    enable_local_bypass=enable_local_bypass)
            cmd.permissions_required.extend(required_permissions)
            self.commands.append(cmd)
            return cmd

        return decorator

    def check_permissions(self, message: twitchirc.ChannelMessage, permissions: typing.List[str],
                          enable_local_bypass=True):
        """
        Check if the user has the required permissions to run a command

        :param message: Message received.
        :param permissions: Permissions required.
        :param enable_local_bypass: If False this function will ignore the permissions
        `twitchirc.bypass.permission.local.*`. This is useful when creating a command that can change global settings.
        :return: A list of missing permissions.

        NOTE `permission_error` handlers are called if this function would return a non empty list.
        """
        missing_permissions = []
        if message.user not in self.permissions:
            missing_permissions = permissions
        else:
            perms = self.permissions.get_permission_state(message)
            if twitchirc.GLOBAL_BYPASS_PERMISSION in perms or \
                    (enable_local_bypass
                     and twitchirc.LOCAL_BYPASS_PERMISSION_TEMPLATE.format(message.channel) in perms):
                return []
            for p in permissions:
                if p not in perms:
                    missing_permissions.append(p)
        if missing_permissions:
            self.call_handlers('permission_error', message, None, missing_permissions)
        return missing_permissions

    def check_permissions_from_command(self, message: twitchirc.ChannelMessage,
                                       command: twitchirc.Command):
        """
        Check if the user has the required permissions to run a command

        :param message: Message received.
        :param command: Command used.
        :return: A list of missing permissions.

        NOTE `permission_error` handlers are called if this function would return a non empty list.
        """
        missing_permissions = []
        if message.user not in self.permissions:
            missing_permissions = command.permissions_required
        else:
            perms = self.permissions.get_permission_state(message)
            if twitchirc.GLOBAL_BYPASS_PERMISSION in perms or \
                    (
                            command.enable_local_bypass
                            and (twitchirc.LOCAL_BYPASS_PERMISSION_TEMPLATE.format(message.channel) in perms)
                    ):
                return []
            for p in command.permissions_required:
                if p not in perms:
                    missing_permissions.append(p)
        if missing_permissions:
            self.call_handlers('permission_error', message, command, missing_permissions)
        return missing_permissions

    def _call_command_handlers(self, message: twitchirc.ChannelMessage):
        if message.text.startswith(self.prefix):
            was_handled = False
            if ' ' not in message.text:
                message.text += ' '
            for handler in self.commands:
                if callable(handler.matcher_function) and handler.matcher_function(message, handler):
                    handler(message)
                    was_handled = True
                if message.text.startswith(self.prefix + handler.ef_command):
                    handler(message)
                    was_handled = True
            if not was_handled:
                self._do_unknown_command(message)
        else:
            self._call_forced_prefix_commands(message)

    def _call_forced_prefix_commands(self, message):
        for handler in self.commands:
            if handler.forced_prefix is None:
                continue
            elif message.text.startswith(handler.ef_command):
                handler(message)

    def _do_unknown_command(self, message):
        if self.on_unknown_command == 'warn':
            twitchirc.warn(f'Unknown command {message!r}')
        elif self.on_unknown_command == 'chat_message':
            msg = message.reply(f'Unknown command {message.text.split(" ", 1)[0]!r}')
            self.send(msg, msg.channel)
        elif self.on_unknown_command == 'ignore':
            # Just ignore it.
            pass
        else:
            raise Exception('Invalid handler in `on_unknown_command`. Valid options: warn, chat_message, '
                            'ignore.')

    def run(self):
        """
        Connect to the server if not already connected. Process messages received.
        This function includes an interrupt handler that automatically calls :py:meth:`stop`.

        :return: nothing.
        """
        try:
            self._run()
        except KeyboardInterrupt:
            print('Got SIGINT, exiting.')
            self.stop()
            return

    def _select_socket(self):
        sel_output = select.select([self.socket], [], [], 0.1)
        return bool(sel_output[0])

    def _run_once(self):
        if self.socket is None:  # self.disconnect() was called.
            return False
        if not self._select_socket():  # no data in socket, assume all messages where handled last time and return
            return True
        twitchirc.info('Receiving.')
        self.receive()
        twitchirc.info('Processing.')
        self.process_messages(100, mode=2)  # process all the messages.
        twitchirc.info('Calling handlers.')
        for i in self.receive_queue.copy():
            twitchirc.info('<', repr(i))
            self.call_handlers('any_msg', i)
            if isinstance(i, twitchirc.PingMessage):
                self.force_send('PONG {}\r\n'.format(i.host))
                if i in self.receive_queue:
                    self.receive_queue.remove(i)
                continue
            elif isinstance(i, twitchirc.ReconnectMessage):
                return 'RECONNECT'
            elif isinstance(i, twitchirc.ChannelMessage):
                self.call_handlers('chat_msg', i)
                self._call_command_handlers(i)
            if i in self.receive_queue:  # this check may fail if self.part() was called.
                self.receive_queue.remove(i)
        if not self.channels_connected:  # if the bot left every channel, stop processing messages.
            return False
        self.flush_queue(max_messages=100)
        return True

    def _run(self):
        if self.socket is None:
            self.connect(self.username, self._password)
        self.hold_send = False
        self.call_handlers('start')
        while 1:
            run_result = self._run_once()
            if run_result is False:
                twitchirc.info('brk')
                break
            if run_result == 'RECONNECT':
                self.disconnect()
                self.connect(self.username, self._password)
            self.scheduler.run(blocking=False)

    def call_handlers(self, event, *args):
        """
        Call handlers for `event`

        :param event: The event that happened. See `handlers`
        :param args: Arguments to give to the handler.

        :return: nothing.
        """
        if event not in ['any_msg', 'chat_msg']:
            twitchirc.info(f'Calling handlers for event {event!r} with args {args!r}')
        for h in self.handlers[event]:
            h(event, *args)

    def disconnect(self):
        """
        Disconnect from the server.

        :return: nothing.
        """
        self.call_handlers('pre_disconnect')
        super().disconnect()
        self.call_handlers('post_disconnect')

    def stop(self):
        """
        Stop the bot and disconnect.
        This function force saves the `storage` and disconnects using :py:meth:`disconnect`

        :return: nothing.
        """
        if self.socket is None:  # Already disconnected.
            return
        self.call_handlers('pre_save')
        self.storage.save(is_auto_save=False)
        self.call_handlers('post_save')
        self.disconnect()

    def send(self, message: typing.Union[str, twitchirc.ChannelMessage], queue='misc') -> None:
        """
        Send a message to the server.

        :param message: message to send
        :param queue: Queue for the message to be in. This will be automaticcally overriden if the message is a
        ChannelMessage. It will be set to `message.channel`.

        :return: nothing

        NOTE The message will not be sent instantely and this is intended. If you would send lots of messages Twitch
        will not forward any of them to the chat clients.
        """
        if self._in_rc_mode:
            if isinstance(message, twitchirc.ChannelMessage):
                twitchirc.log('rc', f'[OUT/{message.channel}, {queue}] {message.text}')
            else:
                twitchirc.log('rc', f'[OUT/?, {queue}] {message}')
        else:
            super().send(message, queue)
