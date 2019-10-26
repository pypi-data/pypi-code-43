"""Game class"""

import click
import operator
from card_game.cards import CardDeck
from card_game.player import Player
from card_game.print_utils import indent, print_header, print_scoreboard


class Game:
    """
    This class controls the flow of the game.

    Instantiates 2-4 Player objects, then executes the game, one round at
    a time. Each round, a shuffled card deck is generated, and a card drawn
    for each player. The Player objects check for round check_for_winner and hold
    state for their current card and win/loss record. Rounds are played
    until the Game object finds a game check_for_winner.
    """

    def __init__(self, players, manual_draw=False, pause_at_round_end=False):
        """
        :param players: either an integer (player count), or a list of
            strings (of player names).
        :param manual_draw: if True, game waits for user input for each
            card draw.
        :param pause_at_round_end: if True, game waits for user input at
            the end of each round.
        """

        if isinstance(players, int):
            self.players = [Player(player_index) for player_index in range(players)]
            self.players_have_names = False
        elif isinstance(players, list):
            self.players = [
                Player(player_number, player_name)
                for player_number, player_name in enumerate(players)
            ]
            self.players_have_names = True
        else:
            raise TypeError
        self._manual_draw = manual_draw
        self._round_end_pause = pause_at_round_end

    def play(self):
        """
        Play a series of rounds until a winner emerges.

        :return: None
        """

        round_number = 0
        winner = None
        while not winner:
            round_number += 1
            winner = self.play_a_round(round_number)
        print_header('game end')
        click.secho(f'\n{winner} wins the game! Well done!!!', fg='green', bold=True)

    def play_a_round(self, round_number):
        """
        Play a single round.

        Print round number as header. Generate shuffled deck. Call card
        draw method for each player. Player objects evaluate and store
        their win or loss. Print same win or loss. Print scoreboard.

        :param round_number:  int. Ensures the round header and scoreboard
            print correctly.
        :return: Player object (game winner) if game end; else None. This
            is used by the play method to bring the game to an end.
        """

        # --- get a shuffled deck ---------------------------------------------
        deck = CardDeck()
        round_header = f'round {round_number}'
        print_header(round_header)
        click.echo(f'\nThe deck has been shuffled. Here we go!')

        # --- draw cards ------------------------------------------------------
        for player in self.players:
            self.draw_card(player, deck)

        # --- assign points ---------------------------------------------------
        cards = [player.card for player in self.players]
        for player in self.players:
            player.determine_round_status(cards)

        # --- print round summary ---------------------------------------------
        click.echo()
        for player in self.players:
            player.print_round_summary()
        print_scoreboard(round_number, self.players, self.players_have_names)

        # -- Pause after each round -------------------------------------------
        winner = self.check_for_winner()
        if not winner and self._round_end_pause:
            click.echo()
            click.pause()
        return winner

    def draw_card(self, player, deck):
        """
        Draw a card for a single player

        Depending on Game instance arguments, wait for user input. Print
        player info and card drawn.

        :param player: Player object
        :param deck: Deck object
        :return: None
        """

        if self._manual_draw:
            click.pause(info=f"\n{player}, press any key to draw a card...")
        else:
            click.echo(f'\n{player} draws...')
        player.card = deck.draw_card()
        click.echo(indent(player.card))

    def check_for_winner(self):
        """
        Check for game check_for_winner.

        :return: Player object (check_for_winner) if game end; else None
        """
        players = sorted(self.players, key=operator.attrgetter('score'))  # players sorted by score
        if players[-1].score >= 21 and players[-1].score - players[-2].score >= 2:
            return players[-1]
        else:
            return None


if __name__ == "__main__":
    help(Game)
