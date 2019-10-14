# -*- coding: utf-8 -*-
import os
import time
import keras
import traceback
import tensorflow as tf
from six import PY3
from tensorflow.python.framework import ops
from tensorflow.python.framework import graph_util
from tensorflow.python.framework.importer import import_graph_def
from tensorflow.python.framework import graph_util as tf_graph_util
from tensorflow.python.framework.errors_impl import NotFoundError
from tensorflow.python.saved_model import loader
from tensorflow.python.saved_model import constants
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model import signature_constants
from tensorflow.python.client import session
from tensorflow.python.lib.io import file_io
from tensorflow.python.platform import tf_logging as logging
from tensorflow.core.framework import graph_pb2
from tensorflow.core.framework import types_pb2
from tensorflow.core.framework import attr_value_pb2
from tensorflow.core.framework import node_def_pb2
from google.protobuf import text_format
from google.protobuf.message import DecodeError
from tflex.optimize import optimize_for_inference_2


class Converter(object):
    """
        Convert from a TensorFlow Frozen GraphDef, SavedModel
        or Keras Model into an EPU supported model.
    """

    def __init__(self,
                 graph_def,
                 model_name,
                 input_tensors,
                 output_tensors,
                 input_arrays_with_shape=None,
                 output_arrays=None):

        """Constructor for EPU Converter.

        Args:
          graph_def: Frozen TensorFlow GraphDef.
          input_tensors: List of input tensors.
          output_tensors: List of output tensors.
          input_arrays_with_shape: Tuple of strings representing input tensor names
            and list of integers representing input shapes
            (e.g., [("input" : [1, 299, 299, 3])]). Use only when graph cannot be loaded
              into TensorFlow and when `input_tensors` and `output_tensors` are
              None. (default None)
          output_arrays: List of output tensors to freeze graph with. Use only when
            graph cannot be loaded into TensorFlow and when `input_tensors` and
            `output_tensors` are None. (default None)

        Raises:
          ValueError: Invalid arguments.
        """

        self._graph_def = graph_def
        self._input_tensors = input_tensors
        self._output_tensors = output_tensors
        self._model_name = model_name

        # Attributes are used by models that cannot be loaded into TensorFlow.
        if not self._has_valid_tensors():
            if not input_arrays_with_shape or not output_arrays:
                raise ValueError(
                    "If input_tensors and output_tensors are None, both "
                    "input_arrays_with_shape and output_arrays must be defined.")
            self._input_arrays_with_shape = input_arrays_with_shape
            self._output_arrays = output_arrays

    @classmethod
    def from_session(cls, sess, input_tensors, output_tensors):
        """Creates an EPU Converter class from a TensorFlow Session.

            Args:
              sess: TensorFlow Session.
              input_tensors: List of input tensors. Type and shape are computed using
        `input.get_shape()` and `input.dtype`.
              output_tensors: List of output tensors (only .name is used from this).

            Returns:
              EPU Converter class.
        """
        graph_def = freeze_graph(sess, output_tensors)
        model_name = 'from_session_' + hex(id(sess))
        return cls(graph_def, model_name, input_tensors, output_tensors)

    @classmethod
    def from_frozen_graph(cls,
                          graph_def_file,
                          input_arrays,
                          output_arrays,
                          input_shapes=None):
        """Creates an EPU Converter class from a file containing a frozen GraphDef.

        Args:
          graph_def_file: Full filepath of file containing frozen GraphDef.
          input_arrays: List of input tensors to freeze graph with.
          output_arrays: List of output tensors to freeze graph with.
          input_shapes: Dict of strings representing input tensor names to list of
             integers representing input shapes (e.g., {"input" : [1, 299, 299, 3]}).
             Automatically determined when input shapes is None (e.g., {"input" :
               None}). (default None)

        Returns:
          EPU Converter class.

        Raises:
          IOError:
            File not found.
            Unable to parse input file.
          ValueError:
            The graph is not frozen.
            input_arrays or output_arrays is non-existent or contains an invalid tensor name.
            input_shapes is not correctly defined when required
        """
        if not input_arrays and output_arrays:
            raise ValueError("input_arrays and output_arrays are required.")
        with ops.Graph().as_default():
            with session.Session() as sess:
                # Read GraphDef from file.
                if not file_io.file_exists(graph_def_file):
                    raise IOError("File '{0}' does not exist.".format(graph_def_file))
                model_name = graph_def_file.split('/')[-1].split('.pb')[0]
                with file_io.FileIO(graph_def_file, "rb") as f:
                    file_content = f.read()

                try:
                    graph_def = graph_pb2.GraphDef()
                    graph_def.ParseFromString(file_content)
                except (text_format.ParseError, DecodeError):
                    try:
                        print("Ignore 'tcmalloc: large alloc warnings.")
                        if not isinstance(file_content, str):
                            if PY3:
                                file_content = file_content.decode("utf-8")
                            else:
                                file_content = file_content.encode("utf-8")
                        graph_def = graph_pb2.GraphDef()
                        text_format.Merge(file_content, graph_def)
                    except (text_format.ParseError, DecodeError):
                        raise IOError("Unable to parse input file '{}'.".format(graph_def_file))

                load_model_in_session = True
                try:
                    import_graph_def(graph_def, name="")
                except:
                    traceback.print_exc()
                    load_model_in_session = False

                if load_model_in_session:
                    # Check if graph is frozen.
                    if not is_frozen_graph(sess):
                        raise ValueError("Please freeze the graph using freeze_graph.py.")
                    # Get input and output tensors.
                    input_tensors = get_tensors_from_tensor_names(sess.graph, input_arrays)
                    output_tensors = get_tensors_from_tensor_names(sess.graph, output_arrays)
                    set_tensor_shapes(input_tensors, input_shapes)
                    return cls(sess.graph_def, model_name, input_tensors, output_tensors)
                else:
                    if not input_shapes:
                        raise ValueError("input_shapes must be defined for this model.")
                    if set(input_arrays) != set(input_shapes.keys()):
                        raise ValueError("input_shapes must contain a value for each item"
                                         "in input_array.")
                    input_arrays_with_shape = [(name, input_shapes[name]) for name in input_arrays]
                    return cls(graph_def,
                               model_name=model_name,
                               input_tensors=None,
                               output_tensors=None,
                               input_arrays_with_shape=input_arrays_with_shape,
                               output_arrays=output_arrays)

    @classmethod
    def from_saved_model(cls,
                         save_model_dir,
                         input_arrays=None,
                         input_shapes=None,
                         output_arrays=None,
                         tag_set=None,
                         signature_key=None):
        """Creates an EPU Converter class from a SavedModel.

        Args:
          saved_model_dir: SavedModel directory to convert.
          input_arrays: List of input tensors to freeze graph with. Uses input
            arrays from SignatureDef when none are provided. (default None)
          input_shapes: Dict of strings representing input tensor names to list of
            integers representing input shapes (e.g., {"input" : [1, 299, 299, 3]}).
            Automatically determined when input shapes is None (e.g., {"input" :
              None}). (default None)
          output_arrays: List of output tensors to freeze graph with. Uses output
            arrays from SignatureDef when none are provided. (default None)
          tag_set: Set of tags identifying the MetaGraphDef within the SavedModel to
            analyze. All tags in the tag set must be present. (default set("serve"))
          signature_key: Key identifying SignatureDef containing inputs and outputs.
            (default DEFAULT_SERVING_SIGNATURE_DEF_KEY)

        Returns:
          EPU Converter class.
        """
        if tag_set is None:
            tag_set = set([tag_constants.TRAINING])
        if signature_key is None:
            signature_key = signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY

        result = freeze_saved_model(save_model_dir, input_arrays, input_shapes,
                                    output_arrays, tag_set, signature_key)
        model_name = save_model_dir.split('/')[-2]
        return cls(graph_def=result[0], model_name=model_name, input_tensors=result[1], output_tensors=result[2])

    @classmethod
    def from_keras_model(cls,
                         model_file,
                         input_arrays=None,
                         input_shapes=None,
                         output_arrays=None):
        """Creates an EPU Converter class from a tf.keras model file.

        Args:
          model_file: Full filepath of HDF5 file containing the tf.keras model.
          input_arrays: List of input tensors to freeze graph with. Uses input
              arrays from SignatureDef when none are provided. (default None)
          input_shapes: Dict of strings representing input tensor names to list of
              integers representing input shapes (e.g., {"input" : [1, 299, 299, 3]}).
              Automatically determined when input shapes is None (e.g., {"input" :
              None}). (default None)
          output_arrays: List of output tensors to freeze graph with. Uses output
              arrays from SignatureDef when none are provided. (default None)

        Returns:
          EPU Converter class.
        """
        keras.backend.clear_session()
        keras.backend.set_learning_phase(False)
        keras_model = keras.models.load_model(model_file)
        sess = keras.backend.get_session()
        model_name = model_file.split('/')[-1].split('.pb')[0]
        # Get input and output tensors.
        if input_arrays:
            input_tensors = get_tensors_from_tensor_names(sess.graph, input_arrays)
        else:
            input_tensors = keras_model.inputs

        if output_arrays:
            output_tensors = get_tensors_from_tensor_names(sess.graph, output_arrays)
        else:
            output_tensors = keras_model.outputs
        set_tensor_shapes(input_tensors, input_shapes)

        graph_def = freeze_graph(sess, output_tensors)

        return cls(graph_def, model_name, input_tensors, output_tensors)

    def convert(self, save_path, device='/device:EPU:0', level=0, strict_padding=False, start_node_names=None,
                end_node_names=None):
        """Convert a TensorFlow GraphDef to an EPU supported GraphDef and save to `path_name` specified by user.

        Args:
          save_path: Pathname to save the successfully optimized GraphDef, e.g., models/resnet50.tflex.
          device: EPU devices assigned to the Conv2D, MaxPool and Pad ops, default is `/device:EPU:0`.
          level: Selection of different levels of optimization, e.g., Fundamental, BatchNormalization, EPU Core, EPU Advanced and Additional optimization,
          default level=0 means that all optimizations will be executed.
          strict_padding: EPU MaxPool only support padding is SAME or VALID(without remnant in W/H). If True is set, it will execute on the CPU.
          start_node_names: The starting nodes are set as the initial input nodes for optimization to flexibly control the starting position in the scope of optimization.
          end_node_names: The ending nodes are set as the last output nodes for optimization to flexibly control the ending position in the scope of optimization.
        Returns:
          Optimized GraphDef.
        """
        logging.set_verbosity(logging.INFO)
        input_arrays = self.get_input_arrays()
        output_arrays = self.get_output_arrays()
        try:
            tstart = time.time()
            new_graph_def = optimize_for_inference_2(self._graph_def, input_arrays, output_arrays,
                                                     device=device, step=level, strict_padding=strict_padding,
                                                     actual_input=start_node_names, actual_output=end_node_names)
            elapsed_time = time.time() - tstart

            # Add attribute information for input and output nodes.
            optimized_graph_def = graph_pb2.GraphDef()
            for node in new_graph_def.node:
                keys = [key for key in node.attr.keys()]
                if node.name in input_arrays:
                    if "_is_input" not in keys:
                        node.attr['_is_input'].CopyFrom(attr_value_pb2.AttrValue(b=True))
                if node.name in output_arrays:
                    if "_is_output" not in keys:
                        node.attr['_is_output'].CopyFrom(attr_value_pb2.AttrValue(b=True))
                new_node = node_def_pb2.NodeDef()
                new_node.CopyFrom(node)
                optimized_graph_def.node.extend([new_node])
            if os.path.isdir(save_path):
                save_path = save_path + self._model_name + '.tflex'
            elif save_path.split('/')[-1]:
                parentPath = os.path.dirname(os.path.abspath(save_path))
                if not os.path.exists(parentPath):
                    os.mkdir(parentPath)
            else:
                os.mkdir(save_path)
                save_path = save_path + self._model_name + '.tflex'
            with tf.gfile.FastGFile(save_path, mode='wb') as f:
                f.write(optimized_graph_def.SerializeToString())
            logging.info(
                "Convert %s successfully and optimization take %.5f s" % (self._model_name, elapsed_time))
            return optimized_graph_def
        except Exception as e:
            traceback.print_exc()
            logging.error('Convert %s Failure: %s' % (self._model_name, e))

    def _has_valid_tensors(self):
        """Checks if the input and output tensors have been initialized.

        Returns:
          Bool.
        """
        return self._input_tensors and self._output_tensors

    def get_input_arrays(self):
        """Returns a list of the names of the input tensors.

        Returns:
          List of strings.
        """
        if self._has_valid_tensors():
            return [tensor_name(tensor) for tensor in self._input_tensors]
        else:
            return [name for name, _ in self._input_arrays_with_shape]

    def get_output_arrays(self):
        """Returns a list of the names of the input tensors.

        Returns:
          List of strings.
        """
        if self._has_valid_tensors():
            return [tensor_name(tensor) for tensor in self._output_tensors]
        else:
            return [name for name, _ in self._input_arrays_with_shape]

    def _print(self):
        import_graph_def(self._graph_def, name='')
        for i, n in enumerate(self._graph_def.node):
            print("Name of the %i node - %s" % (i, n.name))

        print('input_tensors:', self._input_tensors)
        print('output_tensors:', self._output_tensors)

        output_arrays = [tensor_name(tensor) for tensor in self._output_tensors]
        input_arrays = [tensor_name(tensor) for tensor in self._input_tensors]
        print("input_arrays:", input_arrays)
        print("output_arrays:", output_arrays)

    def save_log(self, log_dir):
        with ops.Graph().as_default():
            with session.Session() as sess:
                import_graph_def(self._graph_def)
                writer = tf.summary.FileWriter(log_dir, sess.graph)
                writer.close()


def is_frozen_graph(sess):
    """Determines if the graph is frozen.

    Determines if a graph has previously been frozen by checking for any
    operations of type Variable*. If variables are found, the graph is not frozen.

    Args:
      sess: TensorFlow Session.

    Returns:
      Bool.
    """
    for op in sess.graph.get_operations():
        if op.type.startswith("Variable") or op.type.endswith("VariableOp"):
            return False
    return True


def freeze_graph(sess, output_tensors):
    """Returns a frozen GraphDef.

    Freezes a graph with Variables in it. Otherwise the existing GraphDef is
    returned.

    Args:
      sess: TensorFlow Session.
      output_tensors: List of output tensors (only .name is used from this).

    Returns:
      Frozen GraphDef.
    """
    if not is_frozen_graph(sess):
        output_arrays = [tensor_name(tensor) for tensor in output_tensors]
        return graph_util.convert_variables_to_constants(
            sess, sess.graph_def, output_arrays)
    else:
        return sess.graph_def


def freeze_saved_model(saved_model_dir, input_arrays, input_shapes,
                       output_arrays, tag_set, signature_key):
    """Converts a SavedModel to a frozen graph.

    Args:
      saved_model_dir: SavedModel directory to convert.
      input_arrays: List of input tensors to freeze graph with. Uses input arrays
        from SignatureDef when none are provided.
      input_shapes: Dict of strings representing input tensor names to list of
        integers representing input shapes (e.g., {"input": : [1, 299, 299, 3]}).
        Automatically determined when input shapes is None (e.g., {"input" : None}).
      output_arrays: List of output tensors to freeze graph with. Uses output
        arrays from SignatureDef when none are provided.
      tag_set: Set of tags identifying the MetaGraphDef within the SavedModel to
        analyze. All tags in the tag set must be present.
      signature_key: Key identifying SignatureDef containing inputs and outputs.

    Returns:
      frozen_graph_def: Frozen GraphDef.
      input_tensors: List of input tensors for the graph.
      output_tensors: List of output tensors for the graph.

    Raises:
      ValueError:
        SavedModel doesn't contain a MetaGraphDef identified by tag_set.
        signature_key is not in the MetaGraphDef.
        assets/ directory is in the MetaGraphDef.
        input_shapes does not match the length of input_arrays.
        input_arrays or output_arrays are not valid.
    """
    # Read SignatureDef.
    meta_graph = get_meta_graph_def(saved_model_dir, tag_set)
    signature_def = get_signature_def(meta_graph, signature_key)
    inputs, outputs = get_inputs_outputs(signature_def)

    # Check SavedModel for assets directory.
    collection_def = meta_graph.collection_def
    if constants.ASSETS_KEY in collection_def:
        raise ValueError("SavedModels with assets/ directory are not supported.")

    graph = ops.Graph()
    with session.Session(graph=graph) as sess:
        loader.load(sess, meta_graph.meta_info_def.tags, saved_model_dir)

        # Gets input and output tensors.
        in_tensors = get_tensors(graph, inputs, input_arrays)
        out_tensors = get_tensors(graph, outputs, output_arrays)
        set_tensor_shapes(in_tensors, input_shapes)

        output_names = [node.split(":")[0] for node in outputs]
        frozen_graph_def = tf_graph_util.convert_variables_to_constants(
            sess, graph.as_graph_def(), output_names)

        return frozen_graph_def, in_tensors, out_tensors


def get_meta_graph_def(saved_model_dir, tag_set):
    """Validate saved_model and extract MetaGraphDef.

    Args:
      saved_model_dir: saved_model path to convert.
      tag_set: Set of tag(s) of the MetaGraphDef to load.

    Returns:
      The meta_graph_def used for epu conversion.

    Raises:
      ValueError: No valid MetaGraphDef for given tag_set.
    """
    with session.Session(graph=ops.Graph()) as sess:
        return loader.load(sess, tag_set, saved_model_dir)


def get_signature_def(meta_graph, signature_key):
    """Get the signature def from meta_graph with given signature_key.

    Args:
      meta_graph: meta_graph_def.
      signature_key: signature_def in the meta_graph_def.

    Returns:
      The signature_def used for epu conversion.

    Raises:
      ValueError: Given signature_key is not valid for this meta_graph.
    """
    signature_def_map = meta_graph.signature_def
    signature_def_keys = set(signature_def_map.keys())
    logging.info(
        "The given SavedModel MetaGraphDef contains SignatureDefs with the "
        "following keys: %s", signature_def_keys)
    if signature_key not in signature_def_keys:
        raise ValueError("No '{}' in the SavedModel\'s SignatureDefs. Possible "
                         "values are '{}'.".format(signature_key,
                                                   ",".join(signature_def_keys)))
    return signature_def_map[signature_key]


def get_tensors(graph, signature_def_tensor_names=None,
                user_tensor_names=None):
    """Gets the tensors associated with the tensor names.

    Either signature_def_tensor_names or user_tensor_names should be provided. If
    the user provides tensors, the tensors associated with the user provided
    tensor names are provided. Otherwise, the tensors associated with the names in
    the SignatureDef are provided.

    Args:
      graph: GraphDef representing graph.
      signature_def_tensor_names: Tensor names stored in either the inputs or
        outputs of a SignatureDef. (default None)
      user_tensor_names: Tensor names provided by the user. (default None)

    Returns:
      List of tensors.

    Raises:
      ValueError:
        signature_def_tensors and user_tensor_names are undefined or empty.
        user_tensor_names are not valid.
    """
    tensors = []
    if user_tensor_names:
        # Sort the tensor names.
        user_tensor_names = sorted(user_tensor_names)

        tensors = get_tensors_from_tensor_names(graph, user_tensor_names)
    elif signature_def_tensor_names:
        tensors = [
            graph.get_tensor_by_name(name)
            for name in sorted(signature_def_tensor_names)
        ]
    else:
        # Throw ValueError if signature_def_tensors and user_tensor_names are both
        # either undefined or empty.
        raise ValueError(
            "Specify either signature_def_tensor_names or user_tensor_names")

    return tensors


def get_inputs_outputs(signature_def):
    """Get inputs and outputs from SignatureDef.

    Args:
      signature_def: SignatureDef in the meta_graph_def for conversion.

    Returns:
      The inputs and outputs in the graph for conversion.
    """
    inputs_tensor_info = signature_def.inputs
    outputs_tensor_info = signature_def.outputs
    logging.info("input tensors info: ")
    log_tensor_details(inputs_tensor_info)
    logging.info("output tensors info: ")
    log_tensor_details(outputs_tensor_info)

    def gather_names(tensor_info):
        return [tensor_info[key].name for key in tensor_info]

    inputs = gather_names(inputs_tensor_info)
    outputs = gather_names(outputs_tensor_info)
    return inputs, outputs


def log_tensor_details(tensor_info):
    """Log tensor details: name, shape, and type."""
    for key in tensor_info:
        val = tensor_info[key]
        dtype = types_pb2.DataType.Name(val.dtype)
        if val.tensor_shape.unknown_rank:
            shape = "unknown_rank"
        else:
            dims = [str(dim.size) for dim in val.tensor_shape.dim]
            shape = "({})".format(", ".join(dims))

        logging.info("Tensor's key in saved_model's tensor_map: %s", key)
        logging.info(" tensor name: %s, shape: %s, type: %s", val.name, shape,
                     dtype)


def set_tensor_shapes(tensors, shapes):
    """Sets Tensor shape for each tensor if the shape is defined.

    Args:
      tensors: TensorFlow ops.Tensor.
      shapes: Dict of strings representing input tensor names to list of
        integers representing input shapes (e.g., {"input": [1, 299, 299, 3]}).

    Raises:
      ValueError:
        `shapes` contains an invalid tensor.
        `shapes` contains an invalid shape for a valid tensor.
    """
    if shapes:
        tensor_names_to_tensor = {tensor_name(tensor): tensor for tensor in tensors}
        for name, shape in shapes.items():
            if name not in tensor_names_to_tensor:
                raise ValueError("Invalid tensor \'{}\' found in tensor shapes "
                                 "map.".format(name))
            if shape is not None:
                tensor = tensor_names_to_tensor[name]
                try:
                    tensor.set_shape(shape)
                except ValueError as error:
                    message = ("The shape of tensor '{0}' cannot be changed from {1} to "
                               "{2}. {3}".format(name, tensor.get_shape(), shape,
                                                 str(error)))
                    raise ValueError(message)


def get_tensors_from_tensor_names(graph, tensor_names):
    """Gets the Tensors associated with the `tensor_names` in the provided graph.

    Args:
      graph: TensorFlow Graph.
      tensor_names: List of strings that represent names of tensors in the graph.

    Returns:
      A list of Tensor objects in the same order the names are provided.

    Raises:
      ValueError:
        tensor_names contains an invalid tensor name.
    """
    # Get the list of all of the tensors.
    tensor_name_to_tensor = {
        tensor_name(tensor): tensor for op in graph.get_operations()
        for tensor in op.values()
    }

    # Get the tensors associated with tensor_names.
    tensors = []
    invalid_tensors = []
    for name in tensor_names:
        tensor = tensor_name_to_tensor.get(name)
        if tensor is None:
            invalid_tensors.append(name)
        else:
            tensors.append(tensor)

    # Throw ValueError if any user input names are not valid tensors.
    if invalid_tensors:
        raise ValueError("Invalid tensors '{}' were found.".format(
            ",".join(invalid_tensors)))
    return tensors


def tensor_name(x):
    return x.name.split(":")[0]
