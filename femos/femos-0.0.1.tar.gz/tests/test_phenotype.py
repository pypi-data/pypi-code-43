from numpy import ndarray, array

from femos.core import get_number_of_nn_weights
from femos.genotypes import SimpleGenotype
from femos.phenotypes import Phenotype


def test_phenotype_get_phenotype_for_genotype():
    input_nodes = 4
    hidden_layers_nodes = [6, 8]
    output_nodes = 3

    number_of_nn_weights = get_number_of_nn_weights(input_nodes, hidden_layers_nodes, output_nodes)
    weight_lower_threshold = -1
    weight_upper_threshold = 1

    random_simple_genotype = SimpleGenotype.get_random_genotype(number_of_nn_weights, weight_lower_threshold,
                                                                weight_upper_threshold)

    phenotype = Phenotype.get_phenotype_from_genotype(random_simple_genotype, input_nodes, hidden_layers_nodes,
                                                      output_nodes)

    assert type(phenotype) is Phenotype
    assert len(phenotype.layers) == 3
    assert phenotype.input_nodes == input_nodes
    assert phenotype.hidden_layers_nodes == hidden_layers_nodes
    assert phenotype.output_nodes == output_nodes

    for element in phenotype.layers:
        assert type(element) is ndarray


def test_phenotype_get_prediction():
    input_nodes = 4
    hidden_layers_nodes = [6, 8]
    output_nodes = 3

    number_of_nn_weights = get_number_of_nn_weights(input_nodes, hidden_layers_nodes, output_nodes)
    weight_lower_threshold = -1
    weight_upper_threshold = 1

    random_simple_genotype = SimpleGenotype.get_random_genotype(number_of_nn_weights, weight_lower_threshold,
                                                                weight_upper_threshold)

    phenotype = Phenotype.get_phenotype_from_genotype(random_simple_genotype, input_nodes, hidden_layers_nodes,
                                                      output_nodes)

    input_values = array([[1, 0, 0, -1]])

    prediction = Phenotype.get_prediction(phenotype, input_values)

    assert type(prediction) is ndarray
    assert prediction.shape == (1, 3)
