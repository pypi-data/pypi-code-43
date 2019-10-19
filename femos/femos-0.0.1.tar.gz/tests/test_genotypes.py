from femos.genotypes import SimpleGenotype, UncorrelatedOneStepSizeGenotype, UncorrelatedNStepSizeGenotype


def test_simple_genotype_get_random_genotype():
    number_of_nn_weights = 20
    weight_lower_threshold = -1
    weight_upper_threshold = 1

    random_simple_genotype = SimpleGenotype.get_random_genotype(number_of_nn_weights, weight_lower_threshold,
                                                                weight_upper_threshold)

    assert type(random_simple_genotype) is SimpleGenotype
    assert len(random_simple_genotype.weights) == 20
    for element in random_simple_genotype.weights:
        assert weight_lower_threshold <= element <= weight_upper_threshold


def test_simple_genotype_get_random_genotypes():
    number_of_genotypes = 20

    random_simple_genotypes = SimpleGenotype.get_random_genotypes(number_of_genotypes, 20, -1, 1)
    assert len(random_simple_genotypes) == number_of_genotypes
    for element in random_simple_genotypes:
        assert type(element) is SimpleGenotype


def test_simple_genotype_get_mutated_genotype():
    number_of_nn_weights = 20
    weight_lower_threshold = -1
    weight_upper_threshold = 1
    mutation_mean = 0
    mutation_standard_deviation = 0.2

    random_simple_genotype = SimpleGenotype.get_random_genotype(number_of_nn_weights, weight_lower_threshold,
                                                                weight_upper_threshold)
    mutated_simple_genotype = SimpleGenotype.get_mutated_genotype(random_simple_genotype, 0, 0.3)

    assert random_simple_genotype != mutated_simple_genotype
    assert len(mutated_simple_genotype.weights) == number_of_nn_weights

    for index in range(number_of_nn_weights):
        assert random_simple_genotype.weights[index] != mutated_simple_genotype.weights[index]


def test_uncorrelated_one_step_size_genotype_get_random_genotype():
    number_of_nn_weights = 20
    weight_lower_threshold = -1
    weight_upper_threshold = 1
    mutation_step_size_lower_threshold = -0.3
    mutation_step_size_upper_threshold = 0.3

    random_uoss_genotype = UncorrelatedOneStepSizeGenotype.get_random_genotype(number_of_nn_weights,
                                                                               weight_lower_threshold,
                                                                               weight_upper_threshold,
                                                                               mutation_step_size_lower_threshold,
                                                                               mutation_step_size_upper_threshold)

    assert type(random_uoss_genotype) is UncorrelatedOneStepSizeGenotype
    assert len(random_uoss_genotype.weights) == number_of_nn_weights
    for element in random_uoss_genotype.weights:
        assert weight_lower_threshold <= element <= weight_upper_threshold
    assert random_uoss_genotype.mutation_step_size >= mutation_step_size_lower_threshold
    assert random_uoss_genotype.mutation_step_size <= mutation_step_size_upper_threshold


def test_uncorrelated_one_step_size_genotype_get_random_genotypes():
    number_of_genotypes = 20
    number_of_nn_weights = 20
    weight_lower_threshold = -1
    weights_upper_threshold = 1
    mutation_step_size_lower_threshold = -0.3
    mutation_step_size_upper_threshold = 0.3

    random_uoss_genotypes = UncorrelatedOneStepSizeGenotype.get_random_genotypes(number_of_genotypes,
                                                                                 number_of_nn_weights,
                                                                                 weight_lower_threshold,
                                                                                 weights_upper_threshold,
                                                                                 mutation_step_size_lower_threshold,
                                                                                 mutation_step_size_upper_threshold)

    assert len(random_uoss_genotypes) == number_of_genotypes
    for element in random_uoss_genotypes:
        assert type(element) is UncorrelatedOneStepSizeGenotype


def test_uncorrelated_one_step_size_genotype_mutation():
    number_of_nn_weights = 20
    weight_lower_threshold = -1
    weights_upper_threshold = 1
    mutation_step_size_lower_threshold = -0.3
    mutation_step_size_upper_threshold = 0.3
    mutation_tau1 = 0.01

    random_uoss_genotype = UncorrelatedOneStepSizeGenotype.get_random_genotype(number_of_nn_weights,
                                                                               weight_lower_threshold,
                                                                               weights_upper_threshold,
                                                                               mutation_step_size_lower_threshold,
                                                                               mutation_step_size_upper_threshold)

    mutated_random_uoss_genotype = UncorrelatedOneStepSizeGenotype.get_mutated_genotype(random_uoss_genotype,
                                                                                        mutation_tau1)

    assert random_uoss_genotype != mutated_random_uoss_genotype
    assert len(mutated_random_uoss_genotype.weights) == number_of_nn_weights

    for index in range(number_of_nn_weights):
        assert random_uoss_genotype.weights[index] != mutated_random_uoss_genotype.weights[index]


def test_uncorrelated_n_step_size_genotype_get_random_genotype():
    number_of_nn_weights = 20
    weight_lower_threshold = -1
    weight_upper_threshold = 1
    mutation_step_size_lower_threshold = -0.3
    mutation_step_size_upper_threshold = 0.3

    random_unss_genotype = UncorrelatedNStepSizeGenotype.get_random_genotype(number_of_nn_weights,
                                                                             weight_lower_threshold,
                                                                             weight_upper_threshold,
                                                                             mutation_step_size_lower_threshold,
                                                                             mutation_step_size_upper_threshold)

    assert type(random_unss_genotype) is UncorrelatedNStepSizeGenotype
    assert len(random_unss_genotype.weights) == number_of_nn_weights
    assert len(random_unss_genotype.mutation_step_sizes) == number_of_nn_weights

    for element in random_unss_genotype.weights:
        assert weight_lower_threshold <= element <= weight_upper_threshold

    for element in random_unss_genotype.mutation_step_sizes:
        assert mutation_step_size_lower_threshold <= element <= mutation_step_size_upper_threshold


def test_uncorrelated_n_step_size_genotype_get_random_genotypes():
    number_of_genotypes = 20
    number_of_nn_weights = 20
    weight_lower_threshold = -1
    weight_upper_threshold = 1
    mutation_step_size_lower_threshold = -0.3
    mutation_step_size_upper_threshold = 0.3

    random_unss_genotypes = UncorrelatedNStepSizeGenotype.get_random_genotypes(number_of_genotypes,
                                                                               number_of_nn_weights,
                                                                               weight_lower_threshold,
                                                                               weight_upper_threshold,
                                                                               mutation_step_size_lower_threshold,
                                                                               mutation_step_size_upper_threshold)

    assert len(random_unss_genotypes) == number_of_genotypes
    for element in random_unss_genotypes:
        assert type(element) is UncorrelatedNStepSizeGenotype


def test_uncorrelated_n_step_size_genotype_mutation():
    number_of_nn_weights = 20
    weight_lower_threshold = -1
    weight_upper_threshold = 1
    mutation_step_size_lower_threshold = -0.3
    mutation_step_size_upper_threshold = 0.3
    mutation_tau1 = 0.01
    mutation_tau2 = 0.1

    random_unss_genotype = UncorrelatedNStepSizeGenotype.get_random_genotype(number_of_nn_weights,
                                                                             weight_lower_threshold,
                                                                             weight_upper_threshold,
                                                                             mutation_step_size_lower_threshold,
                                                                             mutation_step_size_upper_threshold)

    mutated_random_unss_genotype = UncorrelatedNStepSizeGenotype.get_mutated_genotype(random_unss_genotype,
                                                                                      mutation_tau1, mutation_tau2)

    assert random_unss_genotype != mutated_random_unss_genotype
    assert len(mutated_random_unss_genotype.weights) == number_of_nn_weights

    for index in range(number_of_nn_weights):
        assert random_unss_genotype.weights[index] != mutated_random_unss_genotype.weights[index]
