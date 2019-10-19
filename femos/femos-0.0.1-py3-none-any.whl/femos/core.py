from random import uniform


def get_random_numbers(quantity, lower_threshold, upper_threshold):
    numbers = []
    for index in range(quantity):
        numbers.append(uniform(lower_threshold, upper_threshold))

    return numbers


def get_number_of_nn_weights(input_nodes, hidden_layers_nodes, output_nodes):
    grouped_nodes = [input_nodes] + hidden_layers_nodes + [output_nodes]

    total = 0
    for index in range(len(grouped_nodes) - 1):
        total += grouped_nodes[index] * grouped_nodes[index + 1]

    return total


def get_next_population(population, phenotype_strategy, evaluation_strategy, parent_selection_strategy,
                        mutation_strategy, offspring_selection_strategy):
    phenotypes = map(phenotype_strategy, population)
    phenotypes_values = evaluation_strategy(list(phenotypes))

    parent_indices = parent_selection_strategy(phenotypes_values)
    parents = map(lambda parent_index: population[parent_index], parent_indices)

    mutated_parents = map(mutation_strategy, parents)
    offspring = offspring_selection_strategy(population, list(mutated_parents))

    return offspring


def get_evolved_population(initial_population, phenotype_strategy, evaluation_strategy, parent_selection_strategy,
                           mutation_strategy, offspring_selection_strategy, number_of_epochs):
    tmp_population = initial_population

    for number_of_epochs in range(number_of_epochs):
        tmp_population = get_next_population(tmp_population, phenotype_strategy, evaluation_strategy,
                                             parent_selection_strategy, mutation_strategy, offspring_selection_strategy)

    return tmp_population
