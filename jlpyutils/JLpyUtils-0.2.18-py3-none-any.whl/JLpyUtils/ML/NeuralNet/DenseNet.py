"""
functions related to a keras implementation of a generic dense neural network
"""
try:
    import tensorflow as __tf__
    __pooling_layer__ = __tf__.keras.layers.MaxPool2D
    __loss__= __tf__.keras.losses.MSE
    __optimizer__ = __tf__.keras.optimizers.Adam
except:
    __loss__= None
    __optimizer__ = None 


def model(n_features,
             n_labels,
             batch_size = None ,
             initial_dense_unit_size = 'auto',
             layers_per_group =  1,
             dense_scaling_factor = 2,
             activation = 'elu',
             final_activation = 'elu',
             batch_norm_rate = None,
             dropout_layer_rate = None,
             dropout_rate = 0.5,
             loss= __loss__,
             learning_rate = 0.001,
             optimizer= __optimizer__,
             metrics=['mae','accuracy']):
    """
    Build a keras-based Dense Neural Net computational graph (model) which can be fit to a given dataset
    
    Arguments:
    ---------
        n_features: number of features (columns) in the data
        n_labels: number of labels you are trying to predict
        initial_dense_unit_size: number of units in the first dense layer. 
            - If 'auto' then this will be set equal to n_features
        layers_per_group: how many DenseNet layers of the same dimension stacked back to back before each dense scaling operation 
        dense_scaling_factor: the multiplicative factor the dense net units will be decreased by for each group of Dense layers
        activation: activation function to be used (i.e. 'elu', 'relu')
            - Note: layers.activation-style functions may be passed, however these typically result in users being unable to save the models due to some bugs in keras
        final_activation: the final activation function used before.
            - If regression, use 'elu' or 'relu'
            - If classificaiton, use 'softmax'
        batch_norm_rate: The rate at which a batch norm layer will be inserted. i.e. for a value of 2, a batch norm layer will be inserted on every other group of dense layers
        dropout_layer_rate: similar to batch_norm_rate, this defines the how often a dropout layer is inserted into a given group of layers
        dropout_rate: the number of nodes to be dropped in a given dropout layer
        loss: the loss function to be used
            - If regression, use 'mse', 'mae', or some other keras based regression loss function
            - If classification, use 'categorical_crossentropy' for multi-class problems, or 'binary_crossentropy' for binary classificaiton problems. Note that the labels should always be in values of 0 & 1 (for the case of multi-class, you should one-hot encode the labels)
        learning_rate: the learning rate the be used by the optimizer
        optimizer: the optimizer to be used
        metrics: list of additional metrics to be output.
    Returns:
    --------
        model
    """
    
    import tensorflow as tf
    import tensorflow.keras as keras
    import tensorflow.keras.layers as layers
    import numpy as np
    
    from . import utils

    keras.backend.clear_session()
    
    model_dict = {}
    model_dict['inputs'] = layers.Input(shape= [n_features], 
                                        batch_size= batch_size,
                                        dtype = tf.float32,
                                        name = 'inputs')
    g = 0 #group index
    idx_dict = {'batch_norm_rate':0,
                'dropout_layer_rate':0}

    #define function to apply batch norm and dropouts at appropriate group iteratation
    BatchNorm_Dropout_dict = {'batch_norm_rate':    batch_norm_rate,
                              'dropout_layer_rate': dropout_layer_rate,
                              'dropout_rate':       dropout_rate}

    #intialize units
    if initial_dense_unit_size == 'auto' or initial_dense_unit_size == 'n_features': 
        units = n_features
    else:
        units = initial_dense_unit_size

    while units > n_labels:
        gl=0
        for gl in range(layers_per_group):  #group layer index
            name = 'G'+str(g)+'_L'+str(gl)+'_Dense'
            model_dict[name]= layers.Dense(units,  
                                           kernel_initializer='glorot_uniform', 
                                           bias_initializer='zeros',
                                           name = name,
                                           activation = activation
                                          )(model_dict[list(model_dict.keys())[-1]])
            gl+=1 
            
            #add batch norm and/or dropout layers
            model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl = utils.Apply_BatchNorm_Dropouts(model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl)

        units = units/dense_scaling_factor
        g+=1

    gl=0
    name = 'outputs'
    model_dict[name] = layers.Dense(n_labels,
                                       activation = final_activation,
                                       name = name
                                      )(model_dict[list(model_dict.keys())[-1]])

    model = keras.Model(inputs = model_dict['inputs'],
                       outputs = model_dict['outputs'])
    
    model.compile(loss=loss,
                  optimizer=optimizer(lr=learning_rate),
                  metrics=metrics)
    
    return model


def model_dict(n_features,
                 n_labels,
                 initial_dense_unit_size = 'auto',
                 layers_per_group =  1,
                 dense_scaling_factor = 2,
                 activation =  'elu',
                 final_activation = 'elu',
                 batch_norm_rate = None,
                 dropout_layer_rate = None,
                 dropout_rate = 0.5,
                 loss=  __loss__,
                 learning_rate = 0.001,
                 optimizer= __optimizer__,
                 metrics=['mse','mae','accuracy']):
    
    import tensorflow as tf
    import tensorflow.keras as keras
    import tensorflow.keras.layers as layers
    import numpy as np
    
    assert(type(n_features)==int), 'n_features must be of type int'
    assert(type(n_labels)==int), 'n_labels must be of type int'
    
    model_dict = {}
    model_dict['model'] = model
    
    model_dict['param_grid'] = {'n_features': [n_features],
                                   'n_labels': [n_labels],
                                   'batch_size' : [None], #pass batch size on fit
                                   'layers_per_group': [1,2],
                                   'initial_dense_unit_size' : [n_features, 2*n_features],
                                   'dense_scaling_factor': [1.5, 2, 3, 5],
                                   'activation': ['elu', 'relu'], 
                                   'final_activation': [final_activation],
                                   'batch_norm_rate': [None, 1, 2],
                                   'dropout_layer_rate': [None, 1, 2],
                                   'dropout_rate': [0.1,0.5],
                                   'loss': [loss],
                                   'learning_rate': [0.001],
                                   'optimizer':[optimizer],
                                   'metrics': [metrics]}
    return model_dict