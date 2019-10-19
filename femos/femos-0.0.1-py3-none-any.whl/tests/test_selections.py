from random import random

from femos.selections import get_two_size_tournament_parent_selection


def test_two_size_tournament_parent_selection():
    number_of_individuals = 30
    individual_values = [0] * 30

    for index in range(number_of_individuals):
        individual_values[index] = random()

    selected_parents = get_two_size_tournament_parent_selection(individual_values, number_of_individuals)

    assert len(selected_parents) == number_of_individuals
    for element in selected_parents:
        assert type(element) is int
        assert 0 <= element <= (number_of_individuals - 1)
