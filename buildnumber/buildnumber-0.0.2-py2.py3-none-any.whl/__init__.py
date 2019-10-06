from buildnumber import objects, utils


def main():
    cli = utils.CLI()
    command = cli.get_command()
    if cli.contains("-f"):
        filename = cli.get("-f")
    else:
        filename = "Buildfile"

    if command == "increment":
        name = cli.get_or_default(command, "default")
        bf = objects.Buildfile(filename)
        bf.increment(name)
        if not cli.contains("-dry_run"):
            bf.save()
        print(bf.get(name))

    elif command == "init":
        name = cli.get_or_default(command, "default")
        bf = objects.Buildfile(filename)
        bf.set(name, "0")
        bf.save()
        print(bf.get(name))

    else:
        bf = objects.Buildfile(filename)
        name = cli.get_or_default(command, "default")
        print(bf.get(name))
