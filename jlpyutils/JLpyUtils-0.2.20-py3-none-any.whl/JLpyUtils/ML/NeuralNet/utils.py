
def Apply_BatchNorm_Dropouts(model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl):
    import tensorflow as tf
    import tensorflow.keras as keras
    import tensorflow.keras.preprocessing
    import tensorflow.keras.layers as layers
    
    for [layer_name, key, layer] in [['BatchNorm', 'batch_norm_rate' ,
                                      layers.BatchNormalization(name = 'G'+str(g)+'_L'+str(gl)+'_'+'BatchNorm')], 
                                     ['Dropout'  , 'dropout_layer_rate', 
                                      layers.Dropout(BatchNorm_Dropout_dict['dropout_rate'],
                                                     name = 'G'+str(g)+'_L'+str(gl+1)+'_'+'Dropout')]]:
        if BatchNorm_Dropout_dict[key]!=None:
            if idx_dict[key] % BatchNorm_Dropout_dict[key] == 0:
                name = 'G'+str(g)+'_L'+str(gl)+'_'+layer_name
                model_dict[name] = layer(model_dict[list(model_dict.keys())[-1]])
                idx_dict[key]=0
            idx_dict[key]+=1
            gl+=1
    return model_dict, BatchNorm_Dropout_dict, idx_dict, g, gl


def load_model(filepath, custom_objects=None, compile=True):
    """
    Loads a model saved via `save_model`.

    Arguments:
        filepath: One of the following:
            - String, path to the saved model
            - `h5py.File` object from which to load the model
        custom_objects: Optional dictionary mapping names
            (strings) to custom classes or functions to be
            considered during deserialization.
        compile: Boolean, whether to compile the model
            after loading.

    Returns:
        A Keras model instance. If an optimizer was found
        as part of the saved model, the model is already
        compiled. Otherwise, the model is uncompiled and
        a warning will be displayed. When `compile` is set
        to False, the compilation is omitted without any
        warning.

    Raises:
        ImportError: if loading from an hdf5 file and h5py is not available.
        IOError: In case of an invalid savefile.
    """
    import tensorflow.keras as keras
    model = keras.models.load_model(filepath, custom_objects=custom_objects, compile = compile)
    
    return model

def save_model(model, filepath, overwrite=True, include_optimizer=True, save_format=None):
    """
    Saves a model as a TensorFlow SavedModel or HDF5 file.

    The saved model contains:
        - the model's configuration (topology)
        - the model's weights
        - the model's optimizer's state (if any)

    Thus the saved model can be reinstantiated in
    the exact same state, without any of the code
    used for model definition or training.

    Arguments:
        model: Keras model instance to be saved.
        filepath: One of the following:
          - String, path where to save the model
          - `h5py.File` object where to save the model
        overwrite: Whether we should overwrite any existing model at the target
          location, or instead ask the user with a manual prompt.
        include_optimizer: If True, save optimizer's state together.
        save_format: Either 'tf' or 'h5', indicating whether to save the model
          to Tensorflow SavedModel or HDF5. The 'tf' option is currently disabled,
          and will be enabled when Keras SavedModel export is no longer
          experimental. (The experimental function is
          tf.keras.experimental.export_saved_model).

    Raises:
        ImportError: If save format is hdf5, and h5py is not available.
    """
    import tensorflow.keras as keras
    keras.models.save_model(model, filepath, overwrite=overwrite, include_optimizer=include_optimizer, save_format=save_format)