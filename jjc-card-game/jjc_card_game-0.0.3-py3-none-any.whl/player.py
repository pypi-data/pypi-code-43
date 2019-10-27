"""Player class"""

import collections
import functools
import click


class Player:
    """
    Objects of this class represent a single game player.

    Stores the player's index, name, latest card and win/loss record
    through the game. Has methods for determining round winner/loser and
    for calculating score for current or any round.
    """

    def __init__(self, index, name=None):
        """

        :param index: int - zero-indexed number
        :param name: str - optional player name
        """
        self.index = index
        self.name = name
        self.card = None
        self._results = []

    @property
    def number(self):
        """Player's unique number for printing purposes"""
        return self.index + 1

    @staticmethod
    def points_earned(status):
        """Return dictionary of values for winning/losing a round."""
        points = {'w': 2, 'n': 0, 'p': -1}
        return points[status]

    @property
    def str_points_earned_this_round(self):
        """
        Return string - points earned in latest round.

        Used by scoreboard at end of round.
        String is prepended with '-' or '+'.
        """
        pts = self.points_earned(self.round_status)
        pts = str(pts)
        if len(pts) == 1:
            pts = '+' + pts
        return pts  # self.points_earned(self.round_status)

    @property
    def round_status(self):
        """Return str - single character representing the win/loss status
        of latest round."""
        return self._results[-1]

    @functools.lru_cache()
    def get_score(self, round_num):
        """Return int - cummulative score for a given round number."""
        if round_num == 0:
            return 0
        else:
            result = self._results[round_num - 1]  # round_status from this round_num
            points = self.points_earned(result)  # points gained or lost this round_num
            return max(0, self.get_score(round_num - 1) + points)  # return score

    @property
    def score(self):
        """Return int - cummulative score as of latest round."""
        round_num = len(self._results)
        return self.get_score(round_num)

    def determine_round_status(self, all_cards_from_this_round):
        """
        Determine player's win/loss status this round

        Win, penalty, or neutral
        """
        if self.card.rank[0] == 'p':
            self._results.append('p')  # penalty
        elif self.card == sorted(all_cards_from_this_round)[-1]:
            self._results.append('w')  # check_for_winner
        else:
            self._results.append('n')  # n/a

    def print_round_summary(self):
        """Print player's win/neutral/penalty status this round"""
        RoundSummary = collections.namedtuple("RoundSummary", 'txt color bold')
        round_summaries = {
            'w': RoundSummary(f'{self} wins the round!', 'green', True),
            'n': RoundSummary(f'{self} gains no points', None, False),
            'p': RoundSummary(f'{self} is penalized!', 'red', True),
        }
        rs = round_summaries[self.round_status]
        click.secho(rs.txt, fg=rs.color, bold=rs.bold)

    def __repr__(self):
        if self.name is None:
            return f"Player {self.number}"
        return f"Player {self.number} ({self.name})"
