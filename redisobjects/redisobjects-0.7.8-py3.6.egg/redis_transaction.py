class RedisTransaction:
    def __init__(self, connection):
        self.connection = connection
        self.commands = []

    async def execute(self, command, *params):
        self.commands.append((command, *params))

    async def commit(self):
        if len(self.commands) == 0:
            return True
        if len(self.commands) == 1:
            return await self.connection.execute(*self.commands[0])
        await self.connection.execute('multi')
        for command in self.commands:
            await self.connection.execute(*command)
        return await self.connection.execute('exec')

    async def discard(self):
        self.commands.clear()
