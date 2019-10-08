tigdef _get_nn_spec(spec):
    if spec.WhichOneof('Type') == 'neuralNetwork':
        nn_spec = spec.neuralNetwork
    elif spec.WhichOneof('Type') == 'neuralNetworkClassifier':
        nn_spec = spec.neuralNetworkClassifier
    elif spec.WhichOneof('Type') == 'neuralNetworkRegressor':
        nn_spec = spec.neuralNetworkRegressor
    else:
        raise ValueError('Specification must contain a neural network')
    return nn_spec

def _dead_code_elimination(spec):
    """
    dead_code_elimination: Remove unused layers from Specification
    """
    uses = {}

    nn_spec = _get_nn_spec(spec)
    nn_layers = nn_spec.layers

    # Add output node as uses
    for _output in spec.description.output:
        uses[_output.name] = 1

    # Add all input nodes as uses
    for _layer in nn_layers:
        for _input in _layer.input:
            uses[_input] = uses.get(_input, 0) + 1
    
    layers_to_delete = []
    for _layer in reversed(nn_layers):
        is_used = False
        for _output in _layer.output:
            # If output is used, cannot remove current layer
            if _output in uses:
                is_used = True
                continue
            
            # If no output from current node is used
            # Remove the layer and decrement use count for all the inputs
            if is_used == False:
                layers_to_delete.append(_layer)
                for _input in _layer.input:
                    uses[_input] -= 1
                    if uses[_input] == 0:
                        del uses[_input]
    
    # delete layers to be removed
    for _layer in layers_to_delete:
        nn_layers.remove(_layer)
    

# Optimize ML Model Spec
def optimize_mlmodel(spec):
    passes = [_dead_code_elimination]

    for p in passes:
        p(spec)
