"""Print utilities available to several modules"""

import click
from prettytable import PrettyTable


def indent(string):
    """Return an indented string."""
    indent_char_count = 4
    return ' '*indent_char_count + str(string)


def print_header(header_txt):
    """Print the supplied header centered and in all-caps"""
    terminal_width = click.get_terminal_size()[0]
    header_width = len(header_txt)
    header_str = header_txt.center(header_width + 6, ' ')
    click.echo()
    click.echo(header_str.upper().center(terminal_width, '+'))


def print_scoreboard(round_number, players, print_names=False):
    """
    Print a pretty scoreboard.

    :param round_number: int
    :param players: list of Player objects
    :param print_names: bool - in/excludes player names from scoreboard
    :return:
    """

    # --- setup ---------------------------------------------------------------
    sb = PrettyTable()
    sb.add_column("Player Number", [player.number for player in players])
    if print_names:
        sb.add_column("Player Name", [player.name for player in players])
    if round_number >= 1:
        sb.add_column("Previous Score", [player.get_score(round_number - 1) for player in players])
        sb.add_column('+/-', [player.str_points_earned_this_round for player in players])
        sb.add_column("New Score", [player.score for player in players])
    else:
        sb.add_column("Score", [player.score for player in players])

    # --- print ---------------------------------------------------------------
    click.echo()
    click.echo(sb)


if __name__ == '__main__':
    help(print_scoreboard)
