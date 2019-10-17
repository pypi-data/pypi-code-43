from rye.base_executable import Executable


class Task(Executable):
    def __init__(self, name, environment, commands, global_lock):
        super().__init__(name, global_lock=global_lock)
        self.name = name
        self.environment = environment
        command_lists = []
        if isinstance(commands, str):
            command_lists = [commands.split()]
        else:
            for command in commands:
                command_lists.append(
                    command.split() if isinstance(command, str) else command
                )
        self.commands = command_lists

    def __repr__(self):
        return f"<Task {self.name} {self.environment.name}>"

    async def run(self):
        await self.environment.wait()
        if not self.environment.is_good():
            self.writer.write("skipping because dependency failed to build")
            self.set_bad()
            return

        for command in self.commands:
            await self.run_command(command, self.environment.env())
        self.set_done()
