import click

from pdbfairy.commands import find_interactions, compare_interactions


@click.group()
def main():
    pass


main.command()(find_interactions.find_interactions)
main.command()(compare_interactions.compare_interactions)


if __name__ == '__main__':
    main()
