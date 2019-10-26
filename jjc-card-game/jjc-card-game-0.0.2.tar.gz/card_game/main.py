"""
Command line interface for game.

Collects setup info from user, but it is game.py that controlls the game
logic and flow.
"""

import click
from card_game.game import Game
from card_game.print_utils import indent


@click.command()
@click.option(
    '--auto-draw', '-d',
    is_flag=True,
    help='For faster gameplay, cards are dealt automatically.'
    )
@click.option('--skip-rules', '-s', is_flag=True, help='Skip the rules explanation.')
@click.argument('player-names', nargs=-1)
def cli(auto_draw, skip_rules, player_names):
    """This is a fun card game playerd by drawing a card and comparing their relative values."""

    # --- intro ---------------------------------------------------------------
    click.clear()
    click.echo('\nWelcome to this really fun card game!')

    # --- player info ---------------------------------------------------------
    if len(player_names) in [2, 3, 4]:
        # user entered appropriate number of names as arguments
        players = list(player_names)
        click.echo('\nHere are the player names you entered:')
        for player in players:
            click.echo(indent(player))
    elif len(player_names) == 0:
        # user didn't enter player names as arguments.ppppppppppppppppp
        # Now ask player for player count and names
        players = get_player_info()
    else:
        # user entered either 1 or >4 names as arguments
        click.echo("\nI see you entered a number of player names outside the allowed range (2 - 4)")
        players = get_player_info()

    # --- explain rules -------------------------------------------------------
    rules = (
        '\nRULES:',
        'We play with a 52 card deck plus 4 additional penalty cards.',
        'The game is played over a series of rounds.',
        'Every round, each player draws one card.',
        'The player who drew the highest card earns 2 points.',
        'Any player who drew a penalty card loses 1 point.',
        'Your score can never drop below 0 points.',
        'You win if you reach at least 21 points and lead by 2.',
    )
    if not skip_rules:
        click.echo('\n'.join(rules))

    # --- play ----------------------------------------------------------------
    click.echo()
    click.pause()
    pause = not auto_draw
    game = Game(players, manual_draw=pause, pause_at_round_end=True)
    game.play()

    # --- outro ---------------------------------------------------------------
    if click.confirm('\nWould you like to play again?'):
        cli()
    else:
        click.echo('Thank you for playing.\n')


def get_player_info():
    """
    Collect info on 2-4 players (player count and optionally player names)

    Runs only if user did not supply 2-4 as initial cli arguments.
    """
    player_count = click.prompt('\nHow many players are playing today?', type=click.IntRange(2, 4))
    click.echo(f'\nOk, {player_count} players. You may now name the players if you wish.')
    if click.confirm('Name players?'):
        click.echo("\nOk, let's name the players.")
        players = [
            click.prompt(f"Name of Player {index + 1}", type=click.STRING)
            for index in range(player_count)
        ]
        click.echo('Got it!')
        return players
    else:
        return player_count


