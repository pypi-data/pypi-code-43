import logging



def is_tf_one(tf):
    return tf.__version__[0] == '1'

def dep(name: str):
    if dep_dict[name] is None:
        dep_dict[name] = dep_list[name]()
    return dep_dict[name]


def import_tf():
    import warnings
    warnings.filterwarnings('ignore', category=FutureWarning)
    try:
        import tensorflow as tf
    except ImportError:
        raise ImportError("Tensorflow required for this functions. Try: pip3 install tensorflow")
    tf.get_logger().setLevel(logging.ERROR)
    #from syncvtools.utils.tf_record.tf_record_decoder import TfExampleDecoder
    if is_tf_one(tf):
        logging.debug("Enabling eager execution")
        tf.enable_eager_execution()
    else:
        logging.debug("Patching new tensorflow with backcompatibility")
        tf.FixedLenFeature = tf.io.FixedLenFeature
        tf.VarLenFeature = tf.io.VarLenFeature
    return tf

def import_tf_obj_det_decoder():
    from syncvtools.utils.tf_record.tf_record_decoder import TfExampleDecoder
    return TfExampleDecoder

dep_list = {'tf':import_tf, 'tf_obj_det_decoder': import_tf_obj_det_decoder}
dep_dict = dict(zip(dep_list.keys(),[None]*len(dep_list)))

