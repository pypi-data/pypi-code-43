"""Instances of these classes contain a single row of validation information,
ready to be printed to the terminal at the conclusion of the app."""

# --- Standard Library Imports ------------------------------------------------
import abc
from collections import namedtuple
from itertools import groupby, count

# --- Third Party Imports -----------------------------------------------------
import click

# --- Intra-Package Imports ---------------------------------------------------
import rtm.main.config as config


class ValidatorOutput(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def print(self):
        return


def pretty_int_list(numbers) -> str:
    def as_range(iterable):
        """Convert list of integers to an easy-to-read string. Used to display the
    on the console the rows that failed validation."""
        list_int = list(iterable)
        if len(list_int) > 1:
            return f'{list_int[0]}-{list_int[-1]}'
        else:
            return f'{list_int[0]}'

    return ', '.join(as_range(g) for _, g in groupby(numbers, key=lambda n, c=count(): n-next(c)))


CellResult = namedtuple("CellResult", "row title comment")


class ValidationResult(ValidatorOutput):
    """Each validation function returns an instance of this class. Calling its
    print() function prints a standardized output to the console."""
    def __init__(self,
                 score,
                 title,
                 cli_explanation=None,
                 nonconforming_indices=None,
                 markup_explanation=None,
                 markup_type='body',  # other options: 'header', 'notes'
                 ):
        self._scores_and_colors = {'Pass': 'green', 'Warning': 'yellow', 'Error': 'red'}
        self.score = score
        self.title = title
        self._explanation = cli_explanation
        self.indices = nonconforming_indices
        self._comment = markup_explanation
        self.excel_type = markup_type

    @property
    def comment(self):
        if self._comment is None:
            return self._explanation
        return self._comment

    @property
    def indices(self):
        return self.__indices

    @indices.setter
    def indices(self, value):
        if value is not None:
            self.__indices = list(value)
        else:
            self.__indices = []

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, value):
        if value not in self._scores_and_colors:
            raise ValueError(f'{value} is an invalid score')
        self.__score = value

    def _get_color(self):
        return self._scores_and_colors[self.score]

    @property
    def rows(self):
        first_body_row = 1 + config.header_row  # this is the row # directly after the headers
        return [index + first_body_row for index in self.indices]

    def print(self) -> None:
        # --- Print Score in Color ------------------------------------------------
        click.secho(f"\t{self.score}", fg=self._get_color(), bold=True, nl=False)
        # --- Print Rule Title ----------------------------------------------------
        click.secho(f"\t{self.title.upper()}", bold=True, nl=False)
        # --- Print Explanation (and Rows) ----------------------------------------
        if self._explanation:

            click.secho(f' - {self._explanation}{pretty_int_list(self.rows)}', nl=False)
        click.echo()  # new line

    @property
    def title_and_comment(self):
        return f'{self.title.upper()}\n{self.comment}'
    # def highlight_output(self):
    #     cell_results = []
    #     for row in self.rows:
    #         cell_result = CellResult(row=row, title=self.title, comment=self._explanation)
    #         cell_results.append(cell_result)
    #     return cell_results


class OutputHeader(ValidatorOutput):
    """Given a field name, print a standardized header on the console."""

    def __init__(self, header_name):
        self.field_name = header_name

    def print(self) -> None:
        sym = '+'
        box_middle = f"{sym}  {self.field_name}  {sym}"
        box_horizontal = sym * len(box_middle)
        click.echo()
        click.secho(box_horizontal, bold=True)
        click.secho(box_middle, bold=True)
        click.secho(box_horizontal, bold=True)
        click.echo()


if __name__ == '__main__':
    pass
