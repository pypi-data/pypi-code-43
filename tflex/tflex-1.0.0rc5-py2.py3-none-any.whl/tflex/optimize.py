# coding=utf-8
# pylint: disable=g-bad-file-header
# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""Removes parts of a graph that are only needed for training.

There are several common transformations that can be applied to GraphDefs
created to train a model, that help reduce the amount of computation needed when
the network is used only for inference. These include:

 - Removing training-only operations like checkpoint saving.

 - Stripping out parts of the graph that are never reached.

 - Removing debug operations like CheckNumerics.

 - Folding batch normalization ops into the pre-calculated weights.

 - Fusing common operations into unified versions.

This script takes a frozen GraphDef file (where the weight variables have been
converted into constants by the freeze_graph script) and outputs a new GraphDef
with the optimizations applied.

An example of command-line usage is:

bazel build tensorflow/python/tools:optimize_for_inference && \
bazel-bin/tensorflow/python/tools/optimize_for_inference \
--input_graph=some_graph_def.pb \
--output_graph=/tmp/optimized_graph.pb \
--input_names=Mul \
--output_names=softmax

"""

from __future__ import absolute_import
from __future__ import division

import collections
import math
import re
import time
import numpy as np

from tensorflow.core.framework import attr_value_pb2
from tensorflow.core.framework import graph_pb2
from tensorflow.core.framework import node_def_pb2
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import tensor_util
from tensorflow.python.platform import flags as flags_lib
from tensorflow.python.platform import tf_logging
from tensorflow.python.tools import strip_unused_lib

from tensorflow.core.framework import tensor_pb2
from tensorflow.python.framework import tensor_shape
import inspect

flags = flags_lib
FLAGS = flags.FLAGS

# Support folding two types of batch norm ops:
# BatchNormWithGlobalNormalization and FusedBatchNorm.  The two types only
# differ in input order and attribute names, so we've collected their
# differences up front.
INPUT_ORDER = {  # Order of inputs for BatchNormWithGlobalNormalization.
    "BatchNormWithGlobalNormalization": ["conv_op", "mean_op", "var_op", "beta_op", "gamma_op"],
    # Order of inputs for FusedBatchNorm.
    "FusedBatchNorm": ["conv_op", "gamma_op", "beta_op", "mean_op", "var_op"],  # Order of inputs for FusedBatchNormV2.
    "FusedBatchNormV2": ["conv_op", "gamma_op", "beta_op", "mean_op", "var_op"]}
# Name of the attribute epsilon value is stored in.
EPSILON_ATTR = {"BatchNormWithGlobalNormalization": "variance_epsilon", "FusedBatchNorm": "epsilon",
                "FusedBatchNormV2": "epsilon"}

step_dict = {}
step_dict['base_optimize'] = set()
step_dict['base_optimize'].add('placeholder_modify')
step_dict['base_optimize'].add('strip_unused_reserve_input_node_shape')
step_dict['base_optimize'].add('remove_training_nodes')
step_dict['base_optimize'].add('append_identity_output')
step_dict['base_optimize'].add('fold_multiple_relus')
step_dict['base_optimize'].add('standardize_leakyRelu')
step_dict['base_optimize'].add('clear_map')
step_dict['base_optimize'].add('standardize_concat')

step_dict['BN_optimize'] = set()
step_dict['BN_optimize'].add('standardize_batchNorm')
step_dict['BN_optimize'].add('merge_bias_BN')
step_dict['BN_optimize'].add('fold_batch_norms')

step_dict['EPU_core_optimize'] = set()
step_dict['EPU_core_optimize'].add('merge_pad')
step_dict['EPU_core_optimize'].add('remove_reshape_before_matmul')
step_dict['EPU_core_optimize'].add('replace_matmul_to_conv2d')
step_dict['EPU_core_optimize'].add('add_conv2D_before_BN')
step_dict['EPU_core_optimize'].add('add_to_bias')
step_dict['EPU_core_optimize'].add('remove_add_ensue_bias')
step_dict['EPU_core_optimize'].add('fold_conv2d_bias_relu')
step_dict['EPU_core_optimize'].add('fold_conv2depu_mul')
step_dict['EPU_core_optimize'].add('fuse_second_input_ops_2')
step_dict['EPU_core_optimize'].add('pad_depthwise')
step_dict['EPU_core_optimize'].add('pad_slice_conv2d2')
step_dict['EPU_core_optimize'].add('reshape_conv2d_weights')
step_dict['EPU_core_optimize'].add('move_const_to_epu')
step_dict['EPU_core_optimize'].add('fp32_to_fp16')
step_dict['EPU_core_optimize'].add('modify_pad_maxpool')

step_dict['EPU_advanced_optimize'] = set()
step_dict['EPU_advanced_optimize'].add('replace_avgpool_to_conv2d')
step_dict['EPU_advanced_optimize'].add('replace_concat_v1')
step_dict['EPU_advanced_optimize'].add('replace_depthwise_to_conv2d')

step_dict['EPU_make_op_async_optimize'] = set()
step_dict['EPU_make_op_async_optimize'].add('make_op_async')

global global_node_dict, global_next_node_dict, global_son_dict, global_father_dict
global_node_dict, global_next_node_dict, global_son_dict, global_father_dict = {}, {}, {}, {}


def find_father(node_name, ignored_names=None):
    if global_father_dict.get(node_name) is None:
        global_father_dict[node_name] = set()
        for input_name in global_node_dict[node_name].input:
            this_input_name = node_name_from_input(input_name)
            if ignored_names is not None and this_input_name in ignored_names:
                continue
            global_father_dict[node_name].add(this_input_name)
            global_father_dict[node_name] |= find_father(this_input_name, ignored_names=ignored_names)
    return global_father_dict[node_name]


def find_son(node_name):
    if global_son_dict.get(node_name) is None:
        global_son_dict[node_name] = set()
        for next_name in global_next_node_dict[node_name]:
            global_son_dict[node_name].add(next_name)
            global_son_dict[node_name] |= find_son(next_name)
    return global_son_dict[node_name]


def refresh_dict(input_graph_def, output_node_names=None):
    global global_node_dict, global_next_node_dict, global_son_dict, global_father_dict
    global_node_dict, global_next_node_dict, global_son_dict, global_father_dict = {}, {}, {}, {}
    for node in input_graph_def.node:
        if node.name not in global_node_dict.keys():
            global_node_dict[node.name] = node
        else:
            raise ValueError("Duplicate node names detected for ", node.name, node.op, global_node_dict[node.name].op)
    use_node_names = set()
    for node_name in global_output_node_names if output_node_names is None else output_node_names:
        use_node_names.add(node_name)
        use_node_names |= find_father(node_name)
    pre_input_graph_def = graph_pb2.GraphDef()
    pre_input_graph_def.node.extend([global_node_dict[name] for name in use_node_names])
    global_node_dict = {}
    for node in pre_input_graph_def.node:
        global_node_dict[node.name] = node
        if global_next_node_dict.get(node.name) is None:
            global_next_node_dict[node.name] = []
        for name in node.input:
            name = node_name_from_input(name)
            if global_next_node_dict.get(name) is None:
                global_next_node_dict[name] = []
            global_next_node_dict[name].append(node.name)
    for name in use_node_names:
        find_son(name)
    return pre_input_graph_def


def pre_and_post(func):
    def wrapper(*args, **kwargs):
        func_name = str(func).split(' ')[1]
        init_len = len(args[0].node)
        input_graph = refresh_dict(args[0])
        args = tuple([input_graph] + list(args[1:]))
        pre_len = len(args[0].node)
        if global_step is None or func_name in global_step:
            init_res = func(*args, **kwargs)
            print(func_name, init_len, pre_len, len(init_res.node))
            return init_res
        tf_logging.warning("The function %s don't need to run" % (func_name))
        return input_graph

    return wrapper


def skip_one_node(skip_node_name, replace_node_name):
    """
    use replace_node_name to replace skip_node_name
    :param skip_node_name:
    :param replace_node_name:
    :return:
    """
    for name in global_next_node_dict[skip_node_name]:
        this_node = global_node_dict[name]
        # regular_input=[node_name_from_input(input_name) for input_name in this_node.input]
        # this code may have a bug, but I don't know how to fix it conveniently
        regular_input = [input_name for input_name in this_node.input]
        this_node.input[regular_input.index(skip_node_name)] = replace_node_name


new_2_old_map = {}


def optimize_for_inference_2(input_graph_def, input_node_names, output_node_names, placeholder_type_enum=None,
                             device='/device:EPU:0', graph_type='resnet', step=0, channel_threshold=1024,
                             strict_padding=False, actual_input=None, actual_output=None):
    extend_names = set()
    refresh_dict(input_graph_def, output_node_names=output_node_names)

    # 1.auto complete the actual_output node
    if actual_output is not None:
        test_father_set = set()
        for output_name in actual_output:
            global_father_dict.clear()
            test_father_set |= find_father(output_name, ignored_names=actual_input)
            test_father_set.add(output_name)
        for test_name in test_father_set:
            if test_name in actual_output:
                continue
            flag = False
            for next_name in global_next_node_dict[test_name]:
                if next_name not in test_father_set:
                    flag = True
                    break
            if flag:
                tf_logging.warning('We must add the node (%s) into the actual_output' % (test_name))
                actual_output.append(test_name)
    # 2.use the actual_input and actual_output node to check the graph whether can be transformed
    # refresh_dict(input_graph_def, output_node_names=output_node_names)
    if actual_output is not None and actual_input is not None:
        all_son_set = set()
        for input_name in actual_input:
            if global_son_dict.get(input_name) is not None:
                all_son_set |= global_son_dict[input_name]
        for output_name in actual_output:
            if output_name not in all_son_set:
                raise Exception("Node (", output_name, ") don't have a legal input")
    refresh_dict(input_graph_def, output_node_names=output_node_names)
    if actual_output is not None:
        extend_names_1 = set()
        extend_names_2 = set()
        for name in output_node_names:
            extend_names_1 |= global_father_dict[name]
            extend_names_1.add(name)
        for name in actual_output:
            extend_names_2 |= global_father_dict[name]
            extend_names_2.add(name)
        extend_names |= (extend_names_1 - extend_names_2)
    if actual_input is not None:
        extend_names_1 = set()
        extend_names_2 = set()
        for name in actual_input:
            extend_names_2 |= global_father_dict[name]
        for name in input_node_names:
            extend_names_1 |= global_father_dict[name]
            extend_names.add(name)
        extend_names |= (extend_names_2 - extend_names_1)
    node_extend = [global_node_dict[name] for name in extend_names]
    result_graph = optimize_for_inference(input_graph_def, input_node_names if actual_input is None else actual_input,
                                          output_node_names if actual_output is None else actual_output,
                                          placeholder_type_enum, device, graph_type, step, channel_threshold,
                                          strict_padding)

    result_graph.node.extend(node_extend)
    if actual_output is not None:
        for node in result_graph.node:
            if node.name in actual_output:
                node.name += '_actual_output'
        for name in actual_output:
            cast_node = create_node_Cast(name, SrcT='DT_HALF', DstT='DT_FLOAT')
            cast_node.input.append(name + '_actual_output')
            result_graph.node.extend([cast_node])
            skip_one_node(name, name + '_actual_output')
    if actual_input is not None:
        result_graph = create_new_graph(result_graph, actual_input,
                                        [node for node in input_graph_def.node if node.name in actual_input])
    print(len(result_graph.node), len(node_extend))
    return result_graph


def optimize_for_inference(input_graph_def, input_node_names, output_node_names, placeholder_type_enum=None,
                           device='/device:EPU:0', graph_type='resnet', step=0, channel_threshold=1024,
                           strict_padding=False):
    """Applies a series of inference optimizations on the input graph.
        1) Pad and slice the nodes to make Conv2DEPU's input and output channels multiples of 32;
        2) Fold Batch Normalization ops into Conv2DEPU op;
        3) Reshape the weights to Conv2DEPU;
        4) Create a zero const op that will be the default second_input to Conv2DEPU;
        5) Fuse the shortcut output as 'second_input' parameter to Conv2DEPU;
        6) Move all const op input to Conv2DEPU on EPU.
    Args:
      input_graph_def: A GraphDef containing a training model.
      input_node_names: A list of names of the nodes that are fed inputs during
        inference.
      output_node_names: A list of names of the nodes that produce the final
        results.
      placeholder_type_enum: The AttrValue enum for the placeholder data type, or
          a list that specifies one value per input node name.
      toco_compatible: Boolean, if True, only runs optimizations that result in
        TOCO compatible graph operations (default=False).
      device: device for placing conv2d, MaxPool, Pad ops.
      graph_type: supports 'resnet' and 'yolo'.

    Returns:
      An optimized version of the input graph.
    """

    global global_output_node_names, global_input_node_names, global_device, global_step, global_channel_threshold
    global_output_node_names = output_node_names
    global_input_node_names = input_node_names
    global_device = device
    global_channel_threshold = channel_threshold
    global_step = set()
    step_names = ['base_optimize', 'BN_optimize', 'EPU_core_optimize', 'EPU_advanced_optimize',
                  'EPU_make_op_async_optimize']
    step = len(step_names) if step == 0 else step
    for step_name in step_names[:step]:
        global_step |= step_dict[step_name]

    ensure_graph_is_valid(input_graph_def)
    optimized_graph_def = input_graph_def

    optimized_graph_def = placeholder_modify(optimized_graph_def, input_node_names, placeholder_type_enum)
    optimized_graph_def = strip_unused_reserve_input_node_shape(optimized_graph_def, input_node_names,
                                                                output_node_names, placeholder_type_enum)
    optimized_graph_def = remove_training_nodes(optimized_graph_def, output_node_names)
    optimized_graph_def = standardize_concat(optimized_graph_def)
    if step > 2:
        check_graph_legality(optimized_graph_def)
    optimized_graph_def = append_identity_output(optimized_graph_def, output_node_names)
    optimized_graph_def = fold_multiple_relus(optimized_graph_def)
    optimized_graph_def = standardize_leakyRelu(optimized_graph_def)
    optimized_graph_def = standardize_batchNorm(optimized_graph_def)
    optimized_graph_def = merge_bias_BN(optimized_graph_def)
    optimized_graph_def = replace_avgpool_to_conv2d(optimized_graph_def)
    optimized_graph_def = remove_reshape_before_matmul(optimized_graph_def)
    optimized_graph_def = replace_matmul_to_conv2d(optimized_graph_def)
    optimized_graph_def = replace_depthwise_to_conv2d(optimized_graph_def)
    optimized_graph_def = merge_pad(optimized_graph_def)
    optimized_graph_def = add_conv2D_before_BN(optimized_graph_def)
    optimized_graph_def = fold_batch_norms(optimized_graph_def)
    optimized_graph_def = add_to_bias(optimized_graph_def)
    optimized_graph_def = remove_add_ensue_bias(optimized_graph_def)
    optimized_graph_def = fold_conv2d_bias_relu(optimized_graph_def)
    optimized_graph_def = fold_conv2depu_mul(optimized_graph_def)
    optimized_graph_def = fuse_second_input_ops_2(optimized_graph_def)
    optimized_graph_def = pad_depthwise(optimized_graph_def)
    optimized_graph_def = pad_slice_conv2d2(optimized_graph_def)
    optimized_graph_def = replace_concat_v1(optimized_graph_def)
    optimized_graph_def = reshape_conv2d_weights(optimized_graph_def)
    optimized_graph_def = move_const_to_epu(optimized_graph_def)
    optimized_graph_def = modify_pad_maxpool(optimized_graph_def, graph_type=graph_type, strict_padding=strict_padding)
    optimized_graph_def = fp32_to_fp16(optimized_graph_def)
    optimized_graph_def = make_op_async(optimized_graph_def)
    ensure_graph_is_valid(optimized_graph_def)
    optimized_graph_def = clear_map(optimized_graph_def)
    return optimized_graph_def


@pre_and_post
def standardize_concat(input_graph_def):
    for node in global_node_dict.values():
        if node.op != 'Concat':
            continue
        init_input = [name for name in node.input]
        node.op = 'ConcatV2'
        for i in range(len(init_input) - 1):
            node.input[i] = init_input[i + 1]
        node.input[-1] = init_input[0]
        node.attr['Tidx'].CopyFrom(attr_value_pb2.AttrValue(type='DT_INT32'))
        insert_map_info(node.name, 'ConcatV2', node.name, 'Concat', 'standardize_concat')
    return input_graph_def


@pre_and_post
def replace_depthwise_to_conv2d(input_graph_def):
    """
    Substitude the depthwise conv2d with the normal conv2d in CPU
    :param input_graph_def:
    :return:
    """

    nodes_to_extend = []
    for n in global_node_dict.values():
        # 1. Find the depthwise cond2d op
        if n.op != 'DepthwiseConv2dNative':
            continue
        weights_op = global_node_dict[n.input[1]]
        # 2. Create the new conv2d op
        conv_op = node_def_pb2.NodeDef()
        conv_op.CopyFrom(n)
        conv_op.op = 'Conv2D'
        conv_op.name = n.name + '_conv2D'
        nodes_to_extend.append(conv_op)
        # 3. Modify the weights op
        weights = values_from_const(weights_op)
        w_shape = weights.shape
        if w_shape[2] > global_channel_threshold:
            print('larger than', global_channel_threshold, ', continue')
            continue
        new_weights = np.zeros([w_shape[0], w_shape[1], w_shape[2], w_shape[2]], dtype=weights.dtype)
        for i in range(w_shape[-2]):
            new_weights[:, :, i, i] = weights[:, :, i, 0]
        new_w_tensor = tensor_util.make_tensor_proto(new_weights)
        weights_op.attr['value'].CopyFrom(attr_value_pb2.AttrValue(tensor=new_w_tensor))

        # 4. Skip nodes and rewire
        skip_one_node(n.name, conv_op.name)
        insert_map_info(conv_op.name, 'Conv2D', n.name, 'DepthwiseConv2dNative', 'replace_depthwise_to_conv2d')
    input_graph_def.node.extend(nodes_to_extend)
    return input_graph_def


@pre_and_post
def replace_avgpool_to_conv2d(input_graph_def):
    node_extend = []
    for avgpool_node in global_node_dict.values():
        if avgpool_node.op != 'AvgPool':
            continue
        input_channel = use_bfs_find_input_channel(avgpool_node.name)[1]
        if input_channel > global_channel_threshold:
            print('this avgpool_node', avgpool_node.name, 'input channel is', input_channel, 'bigger than',
                  global_channel_threshold)
            continue
        strides = [each for each in avgpool_node.attr['strides'].list.i]
        ksize = [each for each in avgpool_node.attr['ksize'].list.i]
        padding = avgpool_node.attr['padding'].s
        T = avgpool_node.attr['T'].type
        each_weight_value = 1.0 / (ksize[1] * ksize[2])
        weight_value = np.zeros([ksize[1], ksize[2], input_channel, input_channel])
        for i in range(input_channel):
            weight_value[:, :, i, i] = each_weight_value
        copy_weight_node = create_node_Const(avgpool_node.name + '_weight', weight_value.astype(np.float32))
        copy_conv2d_node = create_node_Conv2D(avgpool_node.name + '_conv2d',
                                              [avgpool_node.input[0], copy_weight_node.name], T, padding, strides)
        skip_one_node(avgpool_node.name, copy_conv2d_node.name)
        insert_map_info(copy_conv2d_node.name, copy_conv2d_node.op, avgpool_node.name, 'AvgPool',
                        'replace_avgpool_to_conv2d')
        node_extend.extend([copy_conv2d_node, copy_weight_node])
    input_graph_def.node.extend(node_extend)
    return input_graph_def


@pre_and_post
def replace_concat_v1(input_graph_def):
    def expand_concat_in_input_of_concat_node(concat_node):
        input_nodes = [global_node_dict[name] for name in concat_node.input]
        print('concat_node.name =', concat_node.name, '; its axis =', input_nodes[-1].attr['value'].tensor.int_val[0])
        repaired_input_names = []
        fix_flag = False
        for node in input_nodes:
            if node.op[:6] == 'Concat':
                expand_concat_in_input_of_concat_node(node)
                fix_flag = True
                repaired_input_names.extend(node.input[:-1])
            else:
                repaired_input_names.append(node.name)

        if fix_flag:
            for i in range(len(repaired_input_names)):
                if i < len(concat_node.input):
                    concat_node.input[i] = repaired_input_names[i]
                else:
                    concat_node.input.append(repaired_input_names[i])
            concat_node.attr['N'].CopyFrom(attr_value_pb2.AttrValue(i=len(repaired_input_names) - 1))

    flag = True
    while flag:
        flag = False
        for pool_node in global_node_dict.values():
            if not pool_node.op.__contains__('Pool'):
                continue
            concat_node = global_node_dict[pool_node.input[0]]
            if concat_node.op[:6] != 'Concat':
                continue
            copy_concat_node = node_def_pb2.NodeDef()
            copy_concat_node.CopyFrom(concat_node)
            copy_concat_node.name = concat_node.name + '_pre_' + pool_node.op
            for i in range(len(copy_concat_node.input) - 1):
                input_node = global_node_dict[copy_concat_node.input[i]]
                copy_pool_node = node_def_pb2.NodeDef()
                copy_pool_node.CopyFrom(pool_node)
                copy_pool_node.name = input_node.name + '_' + pool_node.op
                copy_pool_node.input[0] = input_node.name
                copy_concat_node.input[i] = copy_pool_node.name
                input_graph_def.node.extend([copy_pool_node])
            input_graph_def.node.extend([copy_concat_node])
            skip_one_node(pool_node.name, copy_concat_node.name)
            flag = True
            input_graph_def = refresh_dict(input_graph_def)
            break
    for concat_node in global_node_dict.values():
        if concat_node.op[:6] != 'Concat':
            continue
        expand_concat_in_input_of_concat_node(concat_node)
    input_graph_def = refresh_dict(input_graph_def)
    flag = True
    while flag:
        flag = False
        for concat_node in global_node_dict.values():
            if concat_node.op[:6] != 'Concat':
                continue
            node_extend = []
            for name in concat_node.input:
                node = node_from_map(global_node_dict, name)
            input_infos = [[name, use_bfs_find_input_channel(name)[1]] for name in concat_node.input[:-1]]
            next_nodes = [node_from_map(global_node_dict, next_node_name) for next_node_name in
                          global_next_node_dict[concat_node.name]]
            if False in [next_node.op.__contains__('Conv2D') for next_node in next_nodes]:
                continue
            for next_node in next_nodes:
                weight_node = node_from_map(global_node_dict, next_node.input[1])
                weight_value = values_from_const(weight_node)
                start = 0
                conv2depu_nodes = ["const_zero"]
                for i in range(len(input_infos)):
                    copy_weight_node = node_def_pb2.NodeDef()
                    copy_weight_node.CopyFrom(weight_node)
                    copy_weight_node.name = weight_node.name + '_' + str(i)
                    copy_value = weight_value[:, :, start:start + input_infos[i][1], :]
                    copy_weight_node.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                        tensor=tensor_util.make_tensor_proto(copy_value, copy_value.dtype.type, copy_value.shape)))
                    start += input_infos[i][1]
                    copy_conv2dEPU_node = node_def_pb2.NodeDef()
                    copy_conv2dEPU_node.CopyFrom(next_node)
                    copy_conv2dEPU_node.name = next_node.name + '_' + str(i)
                    copy_conv2dEPU_node.input[0] = input_infos[i][0]
                    copy_conv2dEPU_node.input[1] = copy_weight_node.name
                    copy_conv2dEPU_node.input[3] = conv2depu_nodes[-1]
                    copy_conv2dEPU_node.attr['second_input_en'].CopyFrom(attr_value_pb2.AttrValue(b=i != 0))
                    if i < len(input_infos) - 1:
                        copy_conv2dEPU_node.input[2] = "const_zero"
                        copy_conv2dEPU_node.attr['bias_en'].CopyFrom(attr_value_pb2.AttrValue(b=False))
                        copy_conv2dEPU_node.attr['relu'].CopyFrom(attr_value_pb2.AttrValue(b=False))
                    conv2depu_nodes.append(copy_conv2dEPU_node.name)
                    node_extend.append(copy_weight_node)
                    node_extend.append(copy_conv2dEPU_node)
                skip_one_node(next_node.name, conv2depu_nodes[-1])
                insert_map_info(conv2depu_nodes[-1], node_extend[-1].op, next_node.name, next_node.op,
                                'replace_concat_v1')
            input_graph_def.node.extend(node_extend)
            input_graph_def = refresh_dict(input_graph_def)
            flag = True
            break
    return input_graph_def


@pre_and_post
def standardize_leakyRelu(input_graph_def):
    node_extends = []
    for max_node in global_node_dict.values():
        if max_node.op != 'Maximum':
            continue
        mul_node = node_from_map(global_node_dict, max_node.input[0])
        init_node = node_from_map(global_node_dict, max_node.input[1])
        if mul_node.op != 'Mul':
            continue
        alpha_node = node_from_map(global_node_dict, mul_node.input[0])
        if node_name_from_input(mul_node.input[1]) != init_node.name:
            continue
        if alpha_node.op != 'Const':
            continue
        alpha_value = values_from_const(alpha_node)
        leaky_node = node_def_pb2.NodeDef()
        leaky_node.op = 'LeakyRelu'
        leaky_node.name = max_node.name + '_LeakyRelu'
        leaky_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_FLOAT'))
        leaky_node.attr['alpha"'].CopyFrom(attr_value_pb2.AttrValue(f=alpha_value))
        leaky_node.input.append(max_node.input[1])
        skip_one_node(max_node.name, leaky_node.name)
        insert_map_info(leaky_node.name, 'LeakyRelu', max_node.name, max_node.op, 'standardize_leakyRelu')
        node_extends.append(leaky_node)
    input_graph_def.node.extend(node_extends)
    return input_graph_def


@pre_and_post
def add_to_bias(input_graph_def):
    for add_node in global_node_dict.values():
        if add_node.op != 'Add':
            continue
        if add_node.attr['T'].type in [3]:
            continue
        one_node, two_node = [node_from_map(global_node_dict, add_node.input[i]) for i in range(2)]
        if two_node.op != 'Const':
            one_node, two_node = two_node, one_node
        if two_node.op != 'Const' or one_node.op != 'Conv2D':
            continue
        add_node.op = 'BiasAdd'
        add_node.input[0] = one_node.name
        add_node.input[1] = two_node.name
    return input_graph_def


@pre_and_post
def remove_add_ensue_bias(input_graph_def):
    for biasAdd_node in global_node_dict.values():
        if biasAdd_node.op != 'BiasAdd':
            continue
        next_names = global_next_node_dict[biasAdd_node.name]
        if len(next_names) != 1:
            continue
        add_node = global_node_dict[next_names[0]]
        if add_node.op not in ['BiasAdd', 'Add']:
            continue
        if add_node.input[0] == biasAdd_node.name:
            add_value_name = add_node.input[1]
        else:
            add_value_name = add_node.input[0]
        if global_node_dict[add_value_name].op != 'Const':
            continue
        bias_value_node = global_node_dict[biasAdd_node.input[1]]
        bias_value = values_from_const(bias_value_node)
        add_value = values_from_const(global_node_dict[add_value_name])
        new_value = bias_value + add_value
        bias_value_node.attr["value"].CopyFrom(attr_value_pb2.AttrValue(
            tensor=tensor_util.make_tensor_proto(new_value, new_value.dtype.type, new_value.shape)))
        skip_one_node(add_node.name, biasAdd_node.name)
        insert_map_info(biasAdd_node.name, biasAdd_node.op, add_node.name, add_node.op, 'remove_add_ensue_bias')
    return input_graph_def


@pre_and_post
def placeholder_modify(input_graph_def, input_node_names, placeholder_type_enum):
    if placeholder_type_enum is None:
        placeholder_type_enum = [-1] * len(input_node_names)
        for node in input_graph_def.node:
            if node.name in input_node_names:
                attr_keys = node.attr.keys()
                placeholder_type_enum[input_node_names.index(node.name)] = node.attr[
                    'dtype'].type if 'dtype' in attr_keys else node.attr['T'].type
    return input_graph_def


@pre_and_post
def clear_map(input_graph_def):
    for name in list(new_2_old_map.keys()):
        if global_node_dict.get(name) is None:
            new_2_old_map.pop(name)

    def sort_node(node_names, test_name=None):
        res = []
        if test_name is None:
            if len(node_names) == 0:
                return res
            test_name = node_names.pop()
            for father_name in global_father_dict[test_name] & node_names:
                res += sort_node(node_names, father_name)
            res.append(test_name)
            return res + sort_node(node_names, None)
        else:
            if test_name not in node_names:
                return res
            for father_name in global_father_dict[test_name] & node_names:
                res += sort_node(node_names, father_name)
            res.append(test_name)
            node_names.remove(test_name)
            return res

    res = sort_node(set(new_2_old_map.keys()))
    f = open('map.txt', 'w')
    for key in res:
        f.write(key + ',' + new_2_old_map[key][2] + ',' + new_2_old_map[key][
            3] + '\n')

    return input_graph_def


def use_bfs_find_input_channel(name):
    node_names = [name]
    for node_name in node_names:
        node = node_from_map(global_node_dict, node_name)
        if node.op[:6] == 'Concat':
            res = [use_bfs_find_input_channel(name)[1] for name in node.input[:-1]]
            return node.name, sum(res)
        elif node.op[:6] == 'Conv2D':
            return node.name, values_from_const(global_node_dict[node.input[1]]).shape[-1]
        elif node.op == 'SpaceToDepth':
            block_size = node.attr['block_size'].i
            return node.name, use_bfs_find_input_channel(node.input[0])[1] * block_size * block_size
        else:
            node_names.extend(node.input)
    return None


def check_graph_legality(input_graph_def):
    refresh_dict(input_graph_def)
    for node in global_node_dict.values():
        if node.op in ['Concat', 'ConcatV2']:
            for name in node.input[:-1]:
                res = use_bfs_find_input_channel(name)
                if res is not None and res[1] % 32 != 0:
                    raise Exception(
                        'this concat (' + node.name + ') has a input (' + name + ') which is from Conv2D(' + res[
                            0] + ') whose output_channel_num is ' + str(res[1]))


@pre_and_post
def add_conv2D_before_BN(input_graph_def):
    """
    add conv2D before BN whose ahead is not conv2D
    :param input_graph_def:
    :return:
    """
    nodes_to_extend = []
    for node in global_node_dict.values():
        if node.op != 'FusedBatchNorm':
            continue
        if node.op not in ("BatchNormWithGlobalNormalization", "FusedBatchNorm", "FusedBatchNormV2"):
            continue
        fore_node = node_from_map(global_node_dict, node.input[INPUT_ORDER[node.op].index("conv_op")])
        if fore_node.op in ["Conv2D", "DepthwiseConv2dNative"]:
            continue
        channel_num = len(values_from_const(global_node_dict[node.input[1]]))
        conv2D_weight_value = np.eye(channel_num).reshape(1, 1, channel_num, channel_num)
        conv2D_weight_node = create_node_Const(node.name + '_fore_Conv2D_weight', conv2D_weight_value)
        conv2D_node = create_node_Conv2D(node.name + '_fore_Conv2D', [fore_node.name, conv2D_weight_node.name],
                                         T='DT_FLOAT')
        nodes_to_extend.extend([conv2D_weight_node, conv2D_node])
        node.input[0] = conv2D_node.name
    input_graph_def.node.extend(nodes_to_extend)
    return input_graph_def


@pre_and_post
def merge_pad(input_graph_def):
    """Merge the pad before conv2D into conv2D by modifying the 'padding' attr.

    Args:
      input_graph_def: A GraphDef containing a model.

    Returns:
      Modified graph with the pad merged.
    """
    nodes_to_skip = []

    for n in global_node_dict.values():
        if n.op == 'Pad':
            if len(global_next_node_dict[n.name]) != 1:
                # If 2 or more branches after pad, don't merge it.
                continue
            conv2d_node = global_node_dict[global_next_node_dict[n.name][0]]
            if conv2d_node.op == 'Conv2D':
                # 1) Delete the Pad and paddings
                nodes_to_skip.extend([n.name, n.input[1]])
                # 2. Modify the 'padding' attr of Conv2D
                conv2d_node.input[list(conv2d_node.input).index(n.name)] = n.input[0]
                strides = conv2d_node.attr['strides'].list.i[1]
                if strides == 1:
                    conv2d_node.attr['padding'].CopyFrom(attr_value_pb2.AttrValue(s=b'SAME'))
                elif strides == 2:
                    conv2d_node.attr['padding'].CopyFrom(attr_value_pb2.AttrValue(s=b'LEFT'))
            if conv2d_node.op == 'MaxPool':
                conv2d_node.attr['padding'].CopyFrom(attr_value_pb2.AttrValue(s=b'SAME'))
                conv2d_node.input[list(conv2d_node.input).index(n.name)] = n.input[0]
    return create_new_graph(input_graph_def, nodes_to_skip)


def insert_map_info(new_name, new_op, old_name, old_op, method):
    if new_2_old_map.get(old_name) is None:
        new_2_old_map[new_name] = [new_op, old_op, old_name, method]
    else:
        old_info = new_2_old_map.get(old_name)
        insert_map_info(new_name, new_op, old_info[2], old_info[1], method)


@pre_and_post
def standardize_batchNorm(input_graph_def):
    BN_names = []
    enter_names = []
    last_names = []
    gamma_names = []
    beta_names = []
    moving_mean_names = []
    moving_variance_names = []
    epsilon_names = []
    extend_nodes = []
    for node in input_graph_def.node:
        if node.op != 'Add':
            continue
        if node_from_map(global_node_dict, node.input[0]).op != 'Mul':
            continue
        sub_beta_node = node_from_map(global_node_dict, node.input[1])
        if sub_beta_node.op != 'Sub':
            continue
        mul_mean_node = node_from_map(global_node_dict, sub_beta_node.input[1])
        if mul_mean_node.op != 'Mul':
            print('standardize_batchNorm', 'mul_mean_node=', mul_mean_node.op, mul_mean_node.name, mul_mean_node.input)
            continue
        mul_gama_node = node_from_map(global_node_dict, mul_mean_node.input[1])
        if mul_gama_node.op != 'Mul' and mul_gama_node.op != 'Rsqrt':
            print('standardize_batchNorm', 'mul_gama_node=', mul_gama_node.op, mul_gama_node.name, mul_gama_node.input)
            continue
        if mul_gama_node.op == 'Rsqrt':
            print('standardize_batchNorm', 'this organization miss a mul_gama_node, we should create one')
            rsqrt_node = node_from_map(global_node_dict, mul_mean_node.input[1])
            mul_gama_node = None
        else:
            rsqrt_node = node_from_map(global_node_dict, mul_gama_node.input[0])
        if rsqrt_node.op != 'Rsqrt':
            print('standardize_batchNorm', 'rsqrt_node=', rsqrt_node.op, rsqrt_node.name, rsqrt_node.input)
            continue
        add_var_node = node_from_map(global_node_dict, rsqrt_node.input[0])
        if add_var_node.op != 'Add':
            print('standardize_batchNorm', 'add_var_node=', add_var_node.op, add_var_node.name, add_var_node.input)
            continue
        BN_names.append('/'.join(node.name.split('/')[:-1]))
        enter_names.append(node.input[0])
        last_names.append(node.name)
        if mul_gama_node is None:
            moving_variance_value = values_from_const(global_node_dict[add_var_node.input[0]])
            new_gamma_node = create_node_Const(BN_names[-1] + '/gamma_weight',
                                               np.ones(moving_variance_value.shape).astype(np.float32))
            gamma_names.append(new_gamma_node.name)
            extend_nodes.append(new_gamma_node)
        else:
            gamma_names.append(mul_gama_node.input[1])
        beta_names.append(sub_beta_node.input[0])
        moving_mean_names.append(mul_mean_node.input[0])
        moving_variance_names.append(add_var_node.input[0])
        epsilon_names.append(add_var_node.input[1])
    for i in range(len(BN_names)):
        fusedBN_node = node_def_pb2.NodeDef()
        fusedBN_node.op = 'FusedBatchNorm'
        fusedBN_node.name = BN_names[i]
        fusedBN_node.input.append(global_node_dict[enter_names[i]].input[0])
        fusedBN_node.input.extend([gamma_names[i], beta_names[i], moving_mean_names[i], moving_variance_names[i]])
        fusedBN_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_FLOAT'))
        fusedBN_node.attr['data_format'].CopyFrom(attr_value_pb2.AttrValue(s=b'NHWC'))
        fusedBN_node.attr['epsilon'].CopyFrom(
            attr_value_pb2.AttrValue(f=values_from_const(global_node_dict[epsilon_names[i]]).item()))
        fusedBN_node.attr['is_training'].CopyFrom(attr_value_pb2.AttrValue(b=False))
        fusedBN_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_HALF'))
        skip_one_node(last_names[i], BN_names[i])
        extend_nodes.append(fusedBN_node)
        insert_map_info(BN_names[i], 'FusedBatchNorm', last_names[i], 'Add', 'standardize_batchNorm')
    return create_new_graph(input_graph_def, None, extend_nodes)


@pre_and_post
def merge_bias_BN(input_graph_def):
    nodes_to_skip = []
    nodes_to_extend = []
    for node in input_graph_def.node:
        if node.op != 'FusedBatchNorm':
            continue
        node_bias = node_from_map(global_node_dict, node.input[0])
        if node_bias.op != 'BiasAdd':
            continue
        node_bias_const = node_from_map(global_node_dict, node_bias.input[1])
        bias_value = values_from_const(node_bias_const)
        if len(global_next_node_dict[node_bias.name]) == 1:
            # Substitute  mean with mean - bias
            mean_op = node_from_map(global_node_dict, node.input[INPUT_ORDER[node.op].index("mean_op")])
            mean_value = values_from_const(mean_op)
            mean_value -= bias_value
            mean_op.attr["value"].CopyFrom(attr_value_pb2.AttrValue(
                tensor=tensor_util.make_tensor_proto(mean_value, mean_value.dtype.type, mean_value.shape)))
            # Rewire
            node.input[0] = node_bias.input[0]
            nodes_to_skip.append(node_bias.name)
        else:
            # Don't merge BiasAdd with BN, instead prepend a Conv2D before BN
            # 1) Conv2D node
            new_node = node_def_pb2.NodeDef()
            new_node.op = 'Conv2D'
            new_node.name = node.name + '_Conv2D'
            new_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_FLOAT'))
            new_node.attr['padding'].CopyFrom(attr_value_pb2.AttrValue(s=b'SAME'))
            new_node.attr['strides'].CopyFrom(
                attr_value_pb2.AttrValue(list=attr_value_pb2.AttrValue.ListValue(i=[1, 1, 1, 1])))
            new_node.input.append(node_bias.name)
            # 2) Weights input to this Conv2D node
            w_shape = bias_value.shape[0]
            new_weights_value = np.zeros([1, 1, w_shape, w_shape])
            for i in range(w_shape):
                new_weights_value[:, :, i, i] = 1
            new_weights_node = create_node_Const(node.name + '_Conv2D_weights', new_weights_value.astype(np.float32))
            new_node.input.append(new_weights_node.name)
            node.input[0] = new_node.name
            nodes_to_extend.extend([new_node, new_weights_node])

    return create_new_graph(input_graph_def, nodes_to_skip, nodes_to_extend)


@pre_and_post
def strip_unused_reserve_input_node_shape(input_graph_def, input_node_names, output_node_names, placeholder_type_enum):
    """Removes unused nodes from a GraphDef and reserve the shape of input node.

        Args:
          input_graph_def: A graph with nodes we want to prune.
          input_node_names: A list of the nodes we use as inputs.
          output_node_names: A list of the output nodes.
          placeholder_type_enum: The AttrValue enum for the placeholder data type, or
              a list that specifies one value per input node name.

        Returns:
          A `GraphDef` with all unnecessary ops removed.

        Raises:
          ValueError: If any element in `input_node_names` refers to a tensor instead
            of an operation.
          KeyError: If any element in `input_node_names` is not found in the graph.
        """
    if placeholder_type_enum is None:
        placeholder_type_enum = []
        for name in input_node_names:
            node = global_node_dict[name]
            placeholder_type_enum.append(node.attr['dtype' if 'dtype' in node.attr.keys() else 'T'].type)
    node_shape_dict = {}
    for node in input_graph_def.node:
        if node.name in input_node_names:
            node_shape_dict[node.name] = node.attr['shape'].shape.dim
            while len(node_shape_dict[node.name]) < 4:
                each = node_shape_dict[node.name].add()
                each.size = -1
    input_graph_def = strip_unused_lib.strip_unused(input_graph_def, input_node_names, output_node_names,
                                                    placeholder_type_enum)
    for node in input_graph_def.node:
        if node.name in input_node_names:
            node.attr['shape'].shape.dim.extend(node_shape_dict[node.name])

    return input_graph_def


@pre_and_post
def remove_training_nodes(input_graph, protected_nodes=None):
    """Prunes out nodes that aren't needed for inference.
    There are nodes like Identity and CheckNumerics that are only useful
    during training, and can be removed in graphs that will be used for
    nothing but inference. Here we identify and remove them, returning an
    equivalent graph. To be specific, CheckNumerics nodes are always removed, and
    Identity nodes that aren't involved in control edges are spliced out so that
    their input and outputs are directly connected.
    Args:
      input_graph: Model to analyze and prune.
      protected_nodes: An optional list of names of nodes to be kept
        unconditionally. This is for example useful to preserve Identity output
        nodes.
    Returns:
      A list of nodes with the unnecessary ones removed.
    """
    if not protected_nodes:
        protected_nodes = []

    types_to_remove = {"CheckNumerics": True}

    input_nodes = input_graph.node
    names_to_remove = {}
    for node in input_nodes:
        if node.op in types_to_remove and node.name not in protected_nodes:
            names_to_remove[node.name] = True

    nodes_after_removal = []
    for node in input_nodes:
        if node.name in names_to_remove:
            continue
        new_node = node_def_pb2.NodeDef()
        new_node.CopyFrom(node)
        input_before_removal = node.input
        del new_node.input[:]
        for full_input_name in input_before_removal:
            input_name = re.sub(r"^\^", "", full_input_name)
            if input_name in names_to_remove:
                continue
            new_node.input.append(full_input_name)
        nodes_after_removal.append(new_node)

    types_to_splice = {"Identity": True}
    control_input_names = set()
    node_names_with_control_input = set()
    for node in nodes_after_removal:
        for node_input in node.input:
            if "^" in node_input:
                control_input_names.add(node_input.replace("^", ""))
                node_names_with_control_input.add(node.name)

    names_to_splice = {}
    for node in nodes_after_removal:
        if node.op in types_to_splice and node.name not in protected_nodes:
            # We don't want to remove nodes that have control edge inputs, because
            # they might be involved in subtle dependency issues that removing them
            # will jeopardize.
            if node.name not in node_names_with_control_input:
                names_to_splice[node.name] = node.input[0]

    # We also don't want to remove nodes which are used as control edge inputs.
    names_to_splice = {name: value for name, value in names_to_splice.items() if name not in control_input_names}

    nodes_after_splicing = []
    for node in nodes_after_removal:
        if node.name in names_to_splice:
            continue
        new_node = node_def_pb2.NodeDef()
        new_node.CopyFrom(node)
        input_before_removal = node.input
        del new_node.input[:]
        for full_input_name in input_before_removal:
            input_name = re.sub(r"^\^", "", full_input_name)
            while input_name in names_to_splice:
                full_input_name = names_to_splice[input_name]
                input_name = re.sub(r"^\^", "", full_input_name)
            new_node.input.append(full_input_name)
        nodes_after_splicing.append(new_node)

    output_graph = graph_pb2.GraphDef()
    output_graph.node.extend(nodes_after_splicing)
    return output_graph


@pre_and_post
def append_identity_output(input_graph_def, output_node_names):
    """If the output_node_name is in the op_type list, we will append an identity op after it, and rename

        Args:
          input_graph_def: A graph with nodes we want to prune.
        Returns:
          A `GraphDef` with all unnecessary ops removed.

        Raises:
          ValueError: If any element in `input_node_names` refers to a tensor instead
            of an operation.
          KeyError: If any element in `input_node_names` is not found in the graph.
        """
    nodes_to_extend = []
    for node in input_graph_def.node:
        if node.name in output_node_names and node.op != 'Identity':
            new_node = node_def_pb2.NodeDef()
            new_node.op = 'Identity'
            new_node.name = node.name
            node.name = node.name + '_modified'
            new_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_HALF'))
            new_node.input.append(node.name)
            nodes_to_extend.append(new_node)
            insert_map_info(node.name, new_node.op, new_node.name, node.op, 'append_identity_output')
    input_graph_def.node.extend(nodes_to_extend)
    return input_graph_def


def create_new_graph(input_graph_def, skip_nodes=None, nodes_to_extend=None):
    """create new model

        Args:
          input_graph_def: A graph with nodes we want to prune.
          skip_nodes: the name of nodes which are needed to be removed and in the init graph
          graph_type: need to add nodes

        Returns:
          A `GraphDef` with all unnecessary ops removed.

        """
    result_graph_def = graph_pb2.GraphDef()
    for node in input_graph_def.node:
        if skip_nodes != None and node.name in skip_nodes:
            continue
        new_node = node_def_pb2.NodeDef()
        new_node.CopyFrom(node)
        result_graph_def.node.extend([new_node])
    if nodes_to_extend is not None and len(nodes_to_extend) > 0:
        result_graph_def.node.extend(nodes_to_extend)
    return result_graph_def


def create_node_Reshape(node_name):
    reshape_node = node_def_pb2.NodeDef()
    reshape_node.op = 'Reshape'
    reshape_node.name = node_name
    reshape_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_HALF'))
    reshape_node.attr['Tshape'].CopyFrom(attr_value_pb2.AttrValue(type='DT_INT32'))
    return reshape_node


data_type_dict = {'float16': 'DT_HALF', 'int32': 'DT_INT32', 'int64': 'DT_INT32', 'float32': 'DT_FLOAT'}


def create_node_Const(node_name, node_value):
    const_node = node_def_pb2.NodeDef()
    const_node.op = 'Const'
    const_node.name = node_name
    if type(node_value) != np.array:
        node_value = np.array(node_value)
    if node_value.dtype == np.int64:
        node_value = node_value.astype(np.int32)
    if node_value.dtype == np.float64:
        node_value = node_value.astype(np.float32)
    const_node.attr['dtype'].CopyFrom(attr_value_pb2.AttrValue(type=data_type_dict[str(node_value.dtype)]))
    const_node.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
        tensor=tensor_util.make_tensor_proto(node_value, node_value.dtype.type, node_value.shape)))
    return const_node


def create_node_Cast(node_name, SrcT='DT_FLOAT', DstT='DT_HALF'):
    cast_node = node_def_pb2.NodeDef()
    cast_node.op = 'Cast'
    cast_node.name = node_name
    cast_node.attr['SrcT'].CopyFrom(attr_value_pb2.AttrValue(type=SrcT))
    cast_node.attr['DstT'].CopyFrom(attr_value_pb2.AttrValue(type=DstT))
    return cast_node


def create_node_Conv2D(node_name, input_names, T='DT_HALF', padding=b'SAME', strides=[1, 1, 1, 1], data_format=b'NHWC'):
    new_node = node_def_pb2.NodeDef()
    new_node.op = 'Conv2D'
    new_node.name = node_name
    new_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type=T))
    new_node.attr['padding'].CopyFrom(attr_value_pb2.AttrValue(s=padding))
    new_node.attr['strides'].CopyFrom(attr_value_pb2.AttrValue(list=attr_value_pb2.AttrValue.ListValue(i=strides)))
    new_node.attr['data_format'].CopyFrom(attr_value_pb2.AttrValue(s=data_format))
    new_node.input.append(input_names[0])
    new_node.input.append(input_names[1])
    return new_node


@pre_and_post
def remove_reshape_before_matmul(input_graph_def):
    for node in global_node_dict.values():
        if node.op != 'MatMul':
            continue
        reshape_node = global_node_dict[node.input[0]]
        if reshape_node.op != 'Reshape':
            continue
        skip_one_node(reshape_node.name,reshape_node.input[0])
    return input_graph_def


@pre_and_post
def replace_matmul_to_conv2d(input_graph_def):
    """Convert MatMul op to Conv2D op"""
    # 1. Find the first MatMul op in the graph, expand the input to a 4D tensor
    nodes = input_graph_def.node
    op = 'MatMul'
    nodes_to_extend = []
    nodes_to_skip = []
    for node in nodes:
        if node.op == op:
            node_weights = global_node_dict[node.input[1]]
            weights_value = values_from_const(node_weights)
            # 1. Insert a reshape node before the first MatMul node
            if not any(global_node_dict[n].op == op for n in global_father_dict[node.name]):
                reshape_node = create_node_Reshape(node.name + "_Before_Reshape")
                reshape_const_node = create_node_Const(node.name + "_Before_Reshape_const",
                                                       [-1, 1, 1, weights_value.shape[0]])
                if global_node_dict[node.input[0]].op == 'Reshape':
                    reshape_node.input.append(global_node_dict[node.input[0]].input[0])
                else:
                    reshape_node.input.append(node.input[0])
                reshape_node.input.append(reshape_const_node.name)
                node.input[0] = reshape_node.name
                nodes_to_extend.extend([reshape_node, reshape_const_node])
            last_flag = False
            # 2. Append a reshape node after the last MatMul or BiasAdd nodes
            if not any(global_node_dict[n].op == op for n in global_son_dict[node.name]):
                last_flag = True
                reshape_node = create_node_Reshape(node.name + "_After_Reshape")
                reshape_const_node = create_node_Const(node.name + "_After_Reshape_const", [-1, weights_value.shape[1]])
                this_name = node.name
                if global_next_node_dict.get(node.name) is not None and global_node_dict[
                    global_next_node_dict[node.name][0]].op == 'BiasAdd':
                    last_flag = False
                    this_name = global_node_dict[global_next_node_dict[node.name][0]].name
                reshape_node.input.append(this_name)
                skip_one_node(this_name, reshape_node.name)
                reshape_node.input.append(reshape_const_node.name)
                nodes_to_extend.extend([reshape_node, reshape_const_node])

            # 3. Replace all MatMul op node to Conv2D node, and change the shape of weights
            nodes_to_skip.append(node.name)
            # 1) Modify the shape of weights
            weights_value = np.reshape(weights_value, [1, 1, weights_value.shape[0], weights_value.shape[1]])
            node_weights.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                tensor=tensor_util.make_tensor_proto(weights_value, weights_value.dtype.type, weights_value.shape)))
            # 2) Create a new conv2d node
            new_node = create_node_Conv2D(node.name + '_Conv2D', node.input)
            # 3). Rewire the output node's input
            if last_flag:
                reshape_node.input[0] = new_node.name
            else:
                skip_one_node(node.name, new_node.name)
            nodes_to_extend.append(new_node)
            insert_map_info(new_node.name, new_node.op, node.name, node.op, 'replace_matmul_to_conv2d')
    return create_new_graph(input_graph_def, nodes_to_skip, nodes_to_extend)


@pre_and_post
def fp32_to_fp16(optimized_graph_def):
    """Convert the FP32 GraphDef input_graph_def to FP16 GraphDef.
    1) Don't modify BN related ops, inlcuding 'Const' and 'read';
    2) If the op has 'dtype' attr and is float32, extract the value as np.array,
        convert to float16 and put it back.
    3) If the op has 'T' attr eqauls to float32, convert it.
    4) For 'FusedBatchNorm' op, convert it to
    Args:
      detection_graph: the FP32 Graph.

    Returns:
      new_model: the FP16 GraphDef.
    """

    def check_key(key_value):
        # -1 : no have this key
        # 0 : this key is not float or half
        # 1: this key is float
        # 2: this key is half
        if key_value.__contains__('no'):
            return -1
        if key_value.__contains__('FLOAT'):
            return 1
        if key_value.__contains__('HALF'):
            return 2
        return 0

    def can_32_to_16(node):

        keys = [key for key in node.attr.keys()]
        T_value = str(node.attr['T'] if 'T' in keys else 'no T').strip()
        dtype_value = str(node.attr['dtype'] if 'dtype' in keys else 'no dtype').strip()
        return check_key(T_value), check_key(dtype_value)

    def change_32_to_16(node, T_ans, dtype_ans):
        if T_ans >= 1:
            node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_HALF'))
        if dtype_ans >= 1:
            node.attr['dtype'].CopyFrom(attr_value_pb2.AttrValue(type='DT_HALF'))
            weights = values_from_const(node)
            weights = weights.astype(np.float16)

            new_value = weights.flatten().view(np.uint16)
            tensor_proto = tensor_pb2.TensorProto(dtype=19,
                                                  tensor_shape=tensor_shape.as_shape(weights.shape).as_proto())
            node.attr['value'].CopyFrom(attr_value_pb2.AttrValue(tensor=tensor_proto))
            node.attr['value'].tensor.half_val.extend(new_value)

    # 1. find the first epu node and the last epu node:
    device_node_names = set([node.name for node in optimized_graph_def.node if node.device == global_device])
    first_device_nodes = []
    last_device_nodes = []
    for node in optimized_graph_def.node:
        if node.device != global_device:
            continue
        if len(set(global_father_dict[node.name]) & set(device_node_names)) == 0:
            first_device_nodes.append(node.name)
        if len(set(global_son_dict[node.name]) & set(device_node_names)) == 0:
            last_device_nodes.append(node.name)

    # 2. find the node which has a father in first_device_nodes and has a son in last_device_nodes
    first_device_nodes = set(first_device_nodes)
    last_device_nodes = set(last_device_nodes)

    not_32_to_16_nodes = []
    inner_nodes = []
    outer_nodes = []
    for node in optimized_graph_def.node:
        T_ans, dtype_ans = can_32_to_16(node)
        if T_ans == 2 or dtype_ans == 2:
            inner_nodes.append(node.name)
            continue
        if T_ans <= 0 and dtype_ans <= 0:
            not_32_to_16_nodes.append(node.name)
            continue
        if node.device != global_device:
            if len(set(global_father_dict[node.name]) & first_device_nodes) == 0:
                outer_nodes.append(node.name)
                continue
            if len(set(global_son_dict[node.name]) & last_device_nodes) == 0:
                outer_nodes.append(node.name)
                continue
        inner_nodes.append(node.name)
        change_32_to_16(node, T_ans, dtype_ans)
    # 3. to add cast
    # 3-1. add 32 to 16 cast
    cast_32_to_16_node = []
    for node_name in inner_nodes:
        this_node = node_from_map(global_node_dict, node_name)
        for input_name in this_node.input:
            if input_name in outer_nodes:
                input_node = node_from_map(global_node_dict, input_name)
                cast_node_name = input_name + '_Cast_32_to_16'
                if cast_node_name not in cast_32_to_16_node:
                    cast_32_to_16_node.append(cast_node_name)
                    cast_node = create_node_Cast(cast_node_name, SrcT='DT_FLOAT', DstT='DT_HALF')
                    cast_node.input.append(input_node.name)
                    optimized_graph_def.node.extend([cast_node])
                this_node.input[list(this_node.input).index(input_name)] = cast_node_name
    # 3-1. add 16 to 32 cast
    cast_16_to_32_node = []
    for node_name in outer_nodes:
        this_node = node_from_map(global_node_dict, node_name)
        for input_name in this_node.input:
            if input_name in inner_nodes:
                input_node = node_from_map(global_node_dict, input_name)
                cast_node_name = input_name + '_Cast_16_to_32'
                if cast_node_name not in cast_16_to_32_node:
                    cast_16_to_32_node.append(cast_node_name)
                    cast_node = create_node_Cast(cast_node_name, SrcT='DT_HALF', DstT='DT_FLOAT')
                    cast_node.input.append(input_node.name)
                    optimized_graph_def.node.extend([cast_node])
                this_node.input[list(this_node.input).index(input_name)] = cast_node_name

    return optimized_graph_def


@pre_and_post
def modify_pad_maxpool(input_graph_def, graph_type, strict_padding=False):
    """Put the first Pad and all qualified MaxPool ops onto designated device.
    The paddings input to the Pad op will also be removed from the GraphDef. And if graph_type is 'yolo', the 'T'
    attr of Pad will be changed to 'unit8', and the dtype of the input placeholder will also be changed to 'unit8'.

        Args:
          input_graph_def: A graph with nodes we want to prune.
          device: device for placing the ops.
          graph_type: supports 'resnet' and 'yolo'.

        Returns:
          A `GraphDef` with all unnecessary ops removed.

        Raises:
          ValueError: If any element in `input_node_names` refers to a tensor instead
            of an operation.
          KeyError: If any element in `input_node_names` is not found in the graph.
        """
    conv2d_dict = find_first_last_conv2d(input_graph_def)
    skip_nodes = []
    first_conv2d_name_list = conv2d_dict['first']
    for node in input_graph_def.node:
        if node.op == 'Pad' and any([node.name in global_node_dict[n].input for n in first_conv2d_name_list]):
            node.op = 'PadEPU'
            node.device = global_device
            paddings_node = global_node_dict[node.input[1]]
            # Drop the paddings node
            node.input.pop()
            skip_nodes.append(paddings_node)
            node.attr.pop('Tpaddings')
            if graph_type == 'yolo':
                # Modify the 'T' attr
                node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_UINT8'))
                # Modify the 'dtype' attr of input placeholder
                input_node = global_node_dict[node.input[0]]
                input_node.attr['dtype'].CopyFrom(attr_value_pb2.AttrValue(type='DT_UINT8'))
        elif node.op == 'MaxPool':
            padding = node.attr['padding'].s
            if strict_padding and padding != b'VALID':
                tf_logging.warning(
                    "EPU MaxPool only supports the padding VALID, but found MaxPool node: %s padding=%s" % (
                        node.name, str(padding)))
                continue
            ksize = node.attr['ksize'].list.i
            if ksize[1] != ksize[2] or ksize[1] not in [2, 3]:
                tf_logging.warning(
                    "EPU MaxPool only supports the ksize 2*2 or 3*3, but found MaxPool node: %s ksize=%s" % (
                        node.name, str(ksize[1:3])))
                continue
            strides = node.attr['strides'].list.i
            if strides[1] != strides[2] or strides[1] not in [2]:
                tf_logging.warning("EPU MaxPool only supports the stride 2*2, but found MaxPool node: %s stride=%s" % (
                    node.name, str(strides[1:3])))
                continue

            node.op = 'MaxPoolEPU'
            node.device = global_device

    return create_new_graph(input_graph_def, skip_nodes)


def ensure_graph_is_valid(graph_def):
    """Makes sure that the graph is internally consistent.

    Checks basic properties of the graph def and raises an exception if there are
    input references to missing nodes, duplicated names, or other logic errors.

    Args:
      graph_def: Definition of a graph to be checked.

    Raises:
      ValueError: If the graph is incorrectly constructed.
    """
    node_map = {}
    for node in graph_def.node:
        if node.name not in node_map.keys():
            node_map[node.name] = node
        else:
            raise ValueError("Duplicate node names detected for ", node.name, node.op, node_map[node.name].op)
    for node in graph_def.node:
        for input_name in node.input:
            input_node_name = node_name_from_input(input_name)
            if input_node_name not in node_map.keys():
                raise ValueError("Input for ", node.name, " not found: ", input_name)


def node_name_from_input(node_name):
    """Strips off ports and other decorations to get the underlying node name."""
    if node_name.startswith("^"):
        node_name = node_name[1:]
    m = re.search(r"(.*):\d+$", node_name)
    if m:
        node_name = m.group(1)
    return node_name


def node_from_map(node_map, name):
    """Pulls a node def from a dictionary for a given name.

    Args:
      node_map: Dictionary containing an entry indexed by name for every node.
      name: Identifies the node we want to find.

    Returns:
      NodeDef of the node with the given name.

    Raises:
      ValueError: If the node isn't present in the dictionary.
    """
    stripped_name = node_name_from_input(name)
    if stripped_name not in node_map:
        raise ValueError("No node named '%s' found in map." % name)
    return node_map[stripped_name]


def values_from_const(node_def):
    """Extracts the values from a const NodeDef as a numpy ndarray.

    Args:
      node_def: Const NodeDef that has the values we want to access.

    Returns:
      Numpy ndarray containing the values.

    Raises:
      ValueError: If the node isn't a Const.
    """
    if node_def.op != "Const":
        raise ValueError("Node named '%s' should be a Const op for values_from_const." % node_def.name)
    input_tensor = node_def.attr["value"].tensor
    tensor_value = tensor_util.MakeNdarray(input_tensor)
    return tensor_value


# Whether to scale by gamma after normalization.
def scale_after_normalization(node):
    if node.op == "BatchNormWithGlobalNormalization":
        return node.attr["scale_after_normalization"].b
    return True


# @pre_and_post
def find_first_last_conv2d(input_graph_def):
    """This function searches for the name of the first conv2d ops and the last conv2d ops in input_graph_def,
    and return them as a dict.

    :param input_graph_def:
    :return:
    """

    result = {'first': [], 'last': []}
    for node in input_graph_def.node:
        if node.op == 'Conv2DEPU':
            if not any(global_node_dict[n].op == 'Conv2DEPU' for n in global_father_dict[node.name]):
                result['first'].append(node.name)
            if not any(global_node_dict[n].op == 'Conv2DEPU' for n in global_son_dict[node.name]):
                result['last'].append(node.name)
    return result


@pre_and_post
def pad_slice_conv2d2(input_graph_def, ck_multiplier=32):
    """Because the Conv2D operation on the EPU only accepts input and output channels that are multipliers of 32,
    we need to pad the input, or slice the output of conv2d operation, and pad the weights, bias if necessary。
    Notice that this function only pad the input to the first Covn2D and slice the output from the last Conv2D.
    This function also change the device to EPU for all conv2D op.

    Args:
        input_graph_def: A GraphDef containing a model.
        ck_multiplier: the input and output channel of the conv2D op must be a multiple of this number,
            defaults to 32.
        device: the device assigned to the Conv2D op, defaults to '/device:EPU:0'.
    Returns:
        Modified graph with conv2D compatible with the EPU

    Raises:
        ValueError: If the graph is badly formed with duplicate node names.

    """
    # input_node_map, next_node_name_map = get_node_and_next_map(input_graph_def)
    conv2d_dict = find_first_last_conv2d(input_graph_def)
    new_ops = []
    for node in input_graph_def.node:
        # 1. Find all the relevant nodes
        # 1) Only deal with Conv2D op
        if node.op != "Conv2DEPU":
            continue
        node.device = global_device
        # 2) Find the input op
        input_op = node_from_map(global_node_dict, node.input[0])

        # 3) Find the weights op and bias op
        weights_op = node_from_map(global_node_dict, node.input[1])
        if weights_op.op != "Const":
            continue
        weights = values_from_const(weights_op)
        C, K = weights.shape[2:]
        bias_op = node_from_map(global_node_dict, node.input[2])
        if bias_op.op != "Const":
            continue
        bias = values_from_const(bias_op)

        # 4) Find output node
        next_ops = [i for i in global_node_dict.values() if node.name in i.input]

        # 2. Modify / Append new nodes
        C_mod = C % ck_multiplier
        K_mod = K % ck_multiplier
        if C_mod != 0:
            n_pad_C = ck_multiplier - C_mod
            weights = np.pad(weights, ((0, 0), (0, 0), (0, n_pad_C), (0, 0)), 'constant', constant_values=0)
            # Modify the weights in place
            weights_op.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                tensor=tensor_util.make_tensor_proto(weights, weights.dtype.type, weights.shape)))

            # Only pad the first Conv2D
            if node.name in conv2d_dict['first']:
                # Create two nodes: Pad op and paddings op
                pad_input_node = node_def_pb2.NodeDef()
                pad_input_node.op = 'Pad'
                pad_input_node.name = node.name + '_Pad'
                pad_input_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_HALF'))
                pad_input_node.attr['Tpaddings'].CopyFrom(attr_value_pb2.AttrValue(type='DT_INT32'))
                pad_input_node.input.append(input_op.name)
                # the paddings which is a parameter to pad op is a Const op

                paddings_node = create_node_Const(pad_input_node.name + '/paddings',
                                                  ((0, 0), (0, 0), (0, 0), (0, n_pad_C)))
                # Append this paddings node to the Pad op
                pad_input_node.input.append(paddings_node.name)
                # Modify the input of the Conv2D op
                node.input[0] = pad_input_node.name
                # Append the new nodes
                new_ops.extend([pad_input_node, paddings_node])
                global_node_dict[pad_input_node.name] = pad_input_node
                global_node_dict[paddings_node.name] = paddings_node

        if K_mod != 0:
            n_pad_K = ck_multiplier - K_mod
            weights = np.pad(weights, ((0, 0), (0, 0), (0, 0), (0, n_pad_K)), 'constant', constant_values=0)
            # Modify the weights in place
            weights_op.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                tensor=tensor_util.make_tensor_proto(weights, weights.dtype.type, weights.shape)))
            # Modify the bias in place
            bias = np.pad(bias, ((0, n_pad_K)), 'constant', constant_values=0)
            bias_op.attr['value'].CopyFrom(
                attr_value_pb2.AttrValue(tensor=tensor_util.make_tensor_proto(bias, bias.dtype.type, bias.shape)))
            if node.name in conv2d_dict['last']:
                # Add 3 nodes to slice the output
                slice_node = node_def_pb2.NodeDef()
                slice_node.op = 'Slice'
                slice_node.name = node.name + '_Slice_1'
                slice_node.attr['Index'].CopyFrom(attr_value_pb2.AttrValue(type='DT_INT32'))
                slice_node.attr['T'].CopyFrom(attr_value_pb2.AttrValue(type='DT_HALF'))
                # Slice begin node
                slice_begin_node = create_node_Const(slice_node.name + '/begin', [0, 0, 0, 0])
                # Slice size node
                slice_size_node = create_node_Const(slice_node.name + '/size', [-1, -1, -1, K])
                # Append all 3 input nodes to the slice_node
                slice_node.input.extend([node.name, slice_begin_node.name, slice_size_node.name])
                for next_op in next_ops:
                    # Notice: add the slice op after BiasAdd because we will fuse Conv2D, bias, relu all into one op later
                    if next_op.op == 'BiasAdd':
                        bias_const = node_from_map(global_node_dict, next_op.input[1])
                        bias = values_from_const(bias_const)
                        # Pad the bias const
                        bias_value = np.pad(bias, ((0, n_pad_K)), 'constant', constant_values=0)
                        bias_const.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                            tensor=tensor_util.make_tensor_proto(bias_value, bias_value.dtype.type, bias_value.shape)))
                        # Append all 3 input nodes to the slice_node
                        slice_node.input.extend([next_op.name, slice_begin_node.name, slice_size_node.name])
                        for output_op in [i for i in global_node_dict.values() if next_op.name in i.input]:
                            # Rewire the output node's input to the slice node
                            idx = np.where([i == next_op.name for i in output_op.input])[0][0]
                            output_op.input[int(idx)] = slice_node.name
                    else:
                        # Rewire the output node's input
                        idx = np.where([i == node.name for i in next_op.input])[0][0]
                        next_op.input[int(idx)] = slice_node.name
                new_ops.extend([slice_node, slice_begin_node, slice_size_node])
                global_node_dict[slice_node.name] = slice_node
                global_node_dict[slice_begin_node.name] = slice_begin_node
                global_node_dict[slice_size_node.name] = slice_size_node

    input_graph_def.node.extend(new_ops)
    return input_graph_def


@pre_and_post
def fold_multiple_relus(input_graph_def):
    """ If there are multiple relu ops following one op, we fold them into one op after this father op."""
    nodes_to_skip = []
    for node in input_graph_def.node:
        if node.op != 'Relu' or node.name in nodes_to_skip:
            continue
        father_node = node.input[0]
        next_node_name_list = global_next_node_dict[father_node]
        if len(next_node_name_list) == 1:
            continue
        relu_name_list = [node_name for node_name in next_node_name_list if global_node_dict[node_name].op == 'Relu']
        if len(relu_name_list) == 1:
            continue
        for relu_node in relu_name_list[1:]:
            skip_one_node(relu_node, node.name)
        nodes_to_skip.extend(relu_name_list[1:])
    return create_new_graph(input_graph_def, nodes_to_skip)


@pre_and_post
def fold_conv2d_bias_relu(input_graph_def):
    """Removes Conv2D, BiasAdd and Relu/ Relu6 ops by folding them into Conv2DEPU op.

    Args:
        input_graph_def: A GraphDef containing a model.
    Returns:
        Modified graph with conv2D compatible with the EPU

    Raises:
        ValueError: If the graph is badly formed with duplicate node names.

    """
    skip_node = []
    for conv2d_node in input_graph_def.node:
        # 1) Find the Conv2D op which device is EPU
        if conv2d_node.op != "Conv2D":
            continue
        # Only supports the same strides value for h and w direction
        strides1 = conv2d_node.attr['strides'].list.i[1]
        strides2 = conv2d_node.attr['strides'].list.i[2]
        if strides1 != strides2:
            tf_logging.warning(
                "EPU Conv2D only supports the same stride in H&W, but found Conv2D node: %s stride=%s" % (
                    conv2d_node.name, str([strides1, strides2])))
            continue

        conv2d_node.op = 'Conv2DEPU'
        conv2d_node.device = global_device
        next_names = global_next_node_dict[conv2d_node.name]

        if len(global_next_node_dict[conv2d_node.name]) != 1:
            conv2d_node.attr['bias_en'].CopyFrom(attr_value_pb2.AttrValue(b=False))
            conv2d_node.input.append('const_zero')
            conv2d_node.attr['relu'].CopyFrom(attr_value_pb2.AttrValue(b=False))
            continue
        skip_node.append(conv2d_node.name)
        # 2) Check the follow of Conv2D is biasAdd or not

        biasAdd_node = global_node_dict[next_names[0]]
        if biasAdd_node.op == 'BiasAdd':
            bias_node = global_node_dict[biasAdd_node.input[1]]
            skip_node.append(biasAdd_node.name)
            conv2d_node.attr['bias_en'].CopyFrom(attr_value_pb2.AttrValue(b=True))
            conv2d_node.input.append(bias_node.name)
        else:
            conv2d_node.attr['bias_en'].CopyFrom(attr_value_pb2.AttrValue(b=False))
            conv2d_node.input.append('const_zero')
        # 2) Check the follow of next is Relu/LeaklyRelu or not
        next_names = global_next_node_dict[skip_node[-1]]
        if len(next_names) != 1:
            conv2d_node.attr['relu'].CopyFrom(attr_value_pb2.AttrValue(b=False))
        else:
            relu_node = global_node_dict[next_names[0]]
            if relu_node.op in ['Relu']:
                conv2d_node.attr['relu'].CopyFrom(attr_value_pb2.AttrValue(b=True))
                skip_node.append(relu_node.name)
            else:
                if relu_node.op in ['LeakyRelu', 'Relu6']:
                    tf_logging.warning(
                        "EPU Activation only supports Relu, but found %s node: %s" % (relu_node.op, relu_node.name))
                conv2d_node.attr['relu'].CopyFrom(attr_value_pb2.AttrValue(b=False))

        # 3) The input of the node which after combination is changed to Conv2DEPU
        insert_map_info(conv2d_node.name, 'Conv2DEPU', skip_node[-1], None, 'fold_conv2d_bias_relu')
        skip_one_node(skip_node[-1], conv2d_node.name)
        skip_node.remove(conv2d_node.name)
    input_graph_def.node.extend([create_node_Const('const_zero', np.array([0]).astype(np.float16))])
    return create_new_graph(input_graph_def, skip_node)


@pre_and_post
def fold_conv2depu_mul(input_graph_def):
    "Fold the mul into Conv2DEPU before it."
    nodes_to_skip = []
    for node in input_graph_def.node:
        if node.op == 'Mul' and node_from_map(global_node_dict, node.input[1]).op == 'Conv2DEPU':
            scalar_op = node_from_map(global_node_dict, node.input[0])
            scalar_value = values_from_const(scalar_op)
            conv2d_op = node_from_map(global_node_dict, node.input[1])
            if len(global_next_node_dict[conv2d_op.name]) != 1:
                continue
            weights_op = node_from_map(global_node_dict, conv2d_op.input[1])
            weights_value = values_from_const(weights_op)
            weights_value *= scalar_value
            weights_op.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                tensor=tensor_util.make_tensor_proto(weights_value, weights_value.dtype.type, weights_value.shape)))
            bias_op = node_from_map(global_node_dict, conv2d_op.input[2])
            bias_value = values_from_const(bias_op)
            bias_value *= scalar_value
            bias_op.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                tensor=tensor_util.make_tensor_proto(bias_value, bias_value.dtype.type, bias_value.shape)))
            # Rewire the output
            skip_one_node(node.name, conv2d_op.name)
            insert_map_info(conv2d_op.name, 'Conv2DEPU', node.name, 'Mul', 'fold_conv2depu_mul')
            nodes_to_skip.extend([node.name, scalar_op.name])
    return create_new_graph(input_graph_def, nodes_to_skip)


@pre_and_post
def fuse_second_input_ops_2(input_graph_def):
    """Append the second_input to the Conv2DEPU's input list.
        The second input defaults to a const op with a zero value with 'second_input_en' set to False.
        If the Conv2DEPU is indeed added to the shortcut output, 'second_input_en' will be set to True, and the shortcut
        output will be the second input.

        Args:
            input_graph_def: A GraphDef containing a model.
        Returns:
            Modified graph with the second_input appended to Conv2DEPU's input list.

        Raises:
            ValueError: If the graph is badly formed with duplicate node names.

    """

    def evaluate_node_rank(this_node, other_node, next_is_relu):
        if this_node.op != 'Conv2DEPU':
            return (-1, this_node.name + ' is ' + this_node.op + ', we need a Conv2DEPU.')
        if global_father_dict.get(other_node.name).__contains__(this_node.name):
            return (-1, this_node.name + ' before ' + other_node.name + '.')
        # if next_is_relu and this_node.attr['relu'].b:
        #     return (-1, this_node.name + ' has a relu, but the add has another relu.')
        if this_node.attr['relu'].b:
            return (-1, this_node.name + ' has a relu, but the add has another relu.')
        if len(this_node.input) == 4:
            return (-1, this_node.name + 'has a second_input')
        if len(global_next_node_dict.get(this_node.name)) != 1:
            return (-1, this_node.name + 'has many next nodes')
        return 1, 'OK'

    nodes_to_skip = []
    index = 0
    for add_node in input_graph_def.node:
        if add_node.op != 'Add':
            continue
        index += 1
        next_is_relu = False
        deal_node = add_node
        if len(global_next_node_dict[add_node.name]) == 1:
            deal_node = node_from_map(global_node_dict, global_next_node_dict[add_node.name][0])
            next_is_relu = deal_node.op == 'Relu'
        one_node = node_from_map(global_node_dict, add_node.input[0])
        two_node = node_from_map(global_node_dict, add_node.input[1])
        one_value, one_message = evaluate_node_rank(one_node, two_node, next_is_relu)
        two_value, two_message = evaluate_node_rank(two_node, one_node, next_is_relu)
        if one_value == -1 and two_value == -1:
            print("this add cannot transform to fuse_second_input because :", one_message, two_message)
            continue
        father_node, son_node = two_node, one_node
        if one_value == -1:
            father_node, son_node = one_node, two_node
        nodes_to_skip.append(add_node.name)
        # create second input
        son_node.attr['second_input_en'].CopyFrom(attr_value_pb2.AttrValue(b=True))
        global_next_node_dict[father_node.name].append(son_node.name)
        son_node.input.append(father_node.name)
        deal_name = add_node.name
        if next_is_relu:
            nodes_to_skip.append(deal_node.name)
            son_node.attr['relu'].CopyFrom(attr_value_pb2.AttrValue(b=True))
            deal_name = deal_node.name
        # skill add node
        skip_one_node(deal_name, son_node.name)
        insert_map_info(son_node.name, 'Conv2DEPU', deal_name, None, 'fuse_second_input_ops_2')
    result_graph_def = graph_pb2.GraphDef()
    for node in input_graph_def.node:
        if node.name in nodes_to_skip:
            continue
        new_node = node_def_pb2.NodeDef()
        new_node.CopyFrom(node)
        if new_node.op == 'Conv2DEPU' and len(new_node.input) == 3:
            new_node.input.append("const_zero")
        result_graph_def.node.extend([new_node])
    if global_node_dict.get('const_zero') is None:
        result_graph_def.node.extend([create_node_Const('const_zero', np.array([0]).astype(np.float16))])
    return result_graph_def


@pre_and_post
def move_const_to_epu(input_graph_def):
    """Moves all const op that is input to Conv2DEPU( e.g. biases, weights) to EPU.

        Args:
            input_graph_def: A GraphDef containing a model.
        Returns:
            Modified graph with all const input to Conv2DEPU on EPU.

        Raises:
            ValueError: If the graph is badly formed with duplicate node names.

        """
    for node in input_graph_def.node:
        if node.op != "Conv2DEPU":
            continue

        weights_op = node_from_map(global_node_dict, node.input[1])
        if weights_op.op != "Const":
            continue
        biases_op = node_from_map(global_node_dict, node.input[2])
        if biases_op.op != "Const":
            continue
        # Modify the device attr
        for op in [weights_op, biases_op]:
            op.device = global_device

    return input_graph_def


@pre_and_post
def pad_depthwise(input_graph_def, ck_multiplier=32):
    for node in input_graph_def.node:
        # 1. Find all the relevant nodes
        # 1) Only deal with DepthwiseConv2dNative op
        if node.op != "DepthwiseConv2dNative":
            continue
        # 2) Find the weights op and bias op
        weights_op = node_from_map(global_node_dict, node.input[1])
        if weights_op.op != "Const":
            tf_logging.warning("Didn't find expected conv Constant input to '%s',"
                               " found %s instead. Maybe because freeze_graph wasn't"
                               " run first?" % (node.name, weights_op))
            continue
        weights = values_from_const(weights_op)
        C = weights.shape[2]

        # 3) Find the bias add const after DepthwiseConv2dNative op
        bias_add_op = node_from_map(global_node_dict, global_next_node_dict[node.name][0])
        if bias_add_op.op == 'BiasAdd':
            bias_const_op = node_from_map(global_node_dict, bias_add_op.input[1])
            bias_const = values_from_const(bias_const_op)

        # 2. Modify / Append new nodes
        C_mod = C % ck_multiplier
        if C_mod != 0:
            n_pad_C = ck_multiplier - C_mod
            weights = np.pad(weights, ((0, 0), (0, 0), (0, n_pad_C), (0, 0)), 'constant', constant_values=0)
            # Modify the weights in place
            weights_op.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                tensor=tensor_util.make_tensor_proto(weights, weights.dtype.type, weights.shape)))
            if bias_add_op.op == 'BiasAdd':
                bias_const = np.pad(bias_const, (0, n_pad_C), 'constant', constant_values=0)
                bias_const_op.attr['value'].CopyFrom(attr_value_pb2.AttrValue(
                    tensor=tensor_util.make_tensor_proto(bias_const, bias_const.dtype.type, bias_const.shape)))

    return input_graph_def


@pre_and_post
def fold_batch_norms(input_graph_def):
    """Removes batch normalization ops by folding them into convolutions.

    Batch normalization during training has multiple dynamic parameters that are
    updated, but once the graph is finalized these become constants. That means
    there's an opportunity to reduce the computations down to a scale and
    addition, rather than the more expensive multiple ops, and even bake the
    scaling into the convolution weights. This function identifies the typical
    pattern of batch normalization subgraphs, and performs the transformation to
    fold the computations down into a simpler form. It currently only spots batch
    normalization that's performed by the BatchNormWithGlobalNormalization op, and
    will need to be extended in the future to handle the newer style.

    Args:
      input_graph_def: A GraphDef containing a model.

    Returns:
      Modified graph with BN ops removed, and modified weights.

    Raises:
      ValueError: If the graph is badly formed with duplicate node names.
    """
    input_node_map = {}
    for node in input_graph_def.node:
        if node.name not in input_node_map.keys():
            input_node_map[node.name] = node
        else:
            raise ValueError("Duplicate node names detected for ", node.name)

    nodes_to_skip = {}
    new_ops = []
    for node in input_graph_def.node:
        if node.op not in ("BatchNormWithGlobalNormalization", "FusedBatchNorm", "FusedBatchNormV2"):
            continue

        conv_op = node_from_map(input_node_map, node.input[INPUT_ORDER[node.op].index("conv_op")])
        if conv_op.op != "Conv2D" and conv_op.op != "DepthwiseConv2dNative":
            tf_logging.warning("Didn't find expected Conv2D input to '%s'" % node.name)
            continue

        weights_op = node_from_map(input_node_map, conv_op.input[1])
        if weights_op.op != "Const":
            tf_logging.warning("Didn't find expected conv Constant input to '%s',"
                               " found %s instead. Maybe because freeze_graph wasn't"
                               " run first?" % (conv_op.name, weights_op))
            continue
        weights = values_from_const(weights_op)
        if conv_op.op == "Conv2D":
            channel_count = weights.shape[3]
        elif conv_op.op == "DepthwiseConv2dNative":
            channel_count = weights.shape[2] * weights.shape[3]

        mean_op = node_from_map(input_node_map, node.input[INPUT_ORDER[node.op].index("mean_op")])
        if mean_op.op != "Const":
            tf_logging.warning("Didn't find expected mean Constant input to '%s',"
                               " found %s instead. Maybe because freeze_graph wasn't"
                               " run first?" % (node.name, mean_op))
            continue
        mean_value = values_from_const(mean_op)
        if mean_value.shape != (channel_count,):
            tf_logging.warning("Incorrect shape for mean, found %s, expected %s,"
                               " for node %s" % (str(mean_value.shape), str((channel_count,)), node.name))
            continue

        var_op = node_from_map(input_node_map, node.input[INPUT_ORDER[node.op].index("var_op")])
        if var_op.op != "Const":
            tf_logging.warning("Didn't find expected var Constant input to '%s',"
                               " found %s instead. Maybe because freeze_graph wasn't"
                               " run first?" % (node.name, var_op))
            continue
        var_value = values_from_const(var_op)
        if var_value.shape != (channel_count,):
            tf_logging.warning("Incorrect shape for var, found %s, expected %s,"
                               " for node %s" % (str(var_value.shape), str((channel_count,)), node.name))
            continue

        beta_op = node_from_map(input_node_map, node.input[INPUT_ORDER[node.op].index("beta_op")])
        if beta_op.op != "Const":
            tf_logging.warning("Didn't find expected beta Constant input to '%s',"
                               " found %s instead. Maybe because freeze_graph wasn't"
                               " run first?" % (node.name, beta_op))
            continue
        beta_value = values_from_const(beta_op)
        if beta_value.shape != (channel_count,):
            tf_logging.warning("Incorrect shape for beta, found %s, expected %s,"
                               " for node %s" % (str(beta_value.shape), str((channel_count,)), node.name))
            continue

        gamma_op = node_from_map(input_node_map, node.input[INPUT_ORDER[node.op].index("gamma_op")])
        if gamma_op.op != "Const":
            tf_logging.warning("Didn't find expected gamma Constant input to '%s',"
                               " found %s instead. Maybe because freeze_graph wasn't"
                               " run first?" % (node.name, gamma_op))
            continue
        gamma_value = values_from_const(gamma_op)
        if gamma_value.shape != (channel_count,):
            tf_logging.warning("Incorrect shape for gamma, found %s, expected %s,"
                               " for node %s" % (str(gamma_value.shape), str((channel_count,)), node.name))
            continue

        variance_epsilon_value = node.attr[EPSILON_ATTR[node.op]].f
        nodes_to_skip[node.name] = True
        nodes_to_skip[weights_op.name] = True
        nodes_to_skip[mean_op.name] = True
        nodes_to_skip[var_op.name] = True
        nodes_to_skip[beta_op.name] = True
        nodes_to_skip[gamma_op.name] = True
        nodes_to_skip[conv_op.name] = True

        if scale_after_normalization(node):
            scale_value = ((1.0 / np.vectorize(math.sqrt)(var_value + variance_epsilon_value)) * gamma_value)
        else:
            scale_value = (1.0 / np.vectorize(math.sqrt)(var_value + variance_epsilon_value))
        offset_value = (-mean_value * scale_value) + beta_value
        # offset_value = offset_value.astype(np.float16)
        scaled_weights = np.copy(weights)
        new_scale_value = scale_value.reshape(
            [1, 1, 1, len(scale_value)] if conv_op.op == 'Conv2D' else [1, 1, weights.shape[2], weights.shape[3]])
        scaled_weights = scaled_weights * new_scale_value
        scaled_weights_op = node_def_pb2.NodeDef()
        scaled_weights_op.op = "Const"
        scaled_weights_op.name = weights_op.name
        scaled_weights_op.attr["dtype"].CopyFrom(weights_op.attr["dtype"])
        scaled_weights_op.attr["value"].CopyFrom(attr_value_pb2.AttrValue(
            tensor=tensor_util.make_tensor_proto(scaled_weights, weights.dtype.type, weights.shape)))
        new_conv_op = node_def_pb2.NodeDef()
        new_conv_op.CopyFrom(conv_op)
        offset_op = node_def_pb2.NodeDef()
        offset_op.op = "Const"
        offset_op.name = node.name + "_biases"
        offset_op.attr["dtype"].CopyFrom(scaled_weights_op.attr["dtype"])
        offset_op.attr["value"].CopyFrom(attr_value_pb2.AttrValue(
            tensor=tensor_util.make_tensor_proto(offset_value, weights.dtype.type, offset_value.shape)))
        bias_add_op = node_def_pb2.NodeDef()
        bias_add_op.op = "BiasAdd"
        bias_add_op.name = node.name
        bias_add_op.attr["T"].CopyFrom(conv_op.attr["T"])
        bias_add_op.attr["data_format"].CopyFrom(conv_op.attr["data_format"])
        bias_add_op.input.extend([new_conv_op.name, offset_op.name])
        # output_node_ops = [n for n in input_node_map.values() if node.name in n.input]
        # for output_node_op in output_node_ops:
        #     idx = np.where([node.name == i for i in output_node_op.input])[0][0]
        #     output_node_op.input[int(idx)] = bias_add_op.name  # new_ops.extend([output_node_op])
        new_ops.extend([scaled_weights_op, new_conv_op, offset_op, bias_add_op])

    return create_new_graph(input_graph_def, nodes_to_skip, new_ops)


@pre_and_post
def reshape_conv2d_weights(input_graph_def):
    """Transpose and reshape the weights of the kernels in Conv2D op to make it compatible with EPU

    Args:
        input_graph_def: A GraphDef containing a model.

    Returns:
        Modified graph with resize and pad ops merged.
    Raises:
        ValueError: If the graph is badly formed with duplicate node names.
    """
    for node in input_graph_def.node:
        # 1. Find all the relevant nodes
        # 1) Only deal with Conv2D op
        if node.op != "Conv2DEPU":
            continue

        # 2) Find the weights op
        weights_op = node_from_map(global_node_dict, node.input[1])
        if weights_op.op != "Const":
            continue
        weights = values_from_const(weights_op)
        w_shape = weights.shape
        # 2. Transpose and Reshape
        new_w_tensor_val = weights.swapaxes(2, 3).reshape(w_shape)
        new_w_tensor = tensor_util.make_tensor_proto(new_w_tensor_val)
        # 3. Assign back the value
        weights_op.attr['value'].CopyFrom(attr_value_pb2.AttrValue(tensor=new_w_tensor))
    return input_graph_def


@pre_and_post
def make_op_async(input_graph_def):
    """Make the EPU Op in input_graph_def to async=true, if its all next Op also on EPU.
    Args:
      input_graph_def: the EPU optimized GraphDef.

    Returns:
      result_graph_def: the EPU Op aysnc optimized GraphDef.
    """
    node = input_graph_def.node
    result_graph_def = graph_pb2.GraphDef()
    for n in node:
        new_node = node_def_pb2.NodeDef()
        new_node.CopyFrom(n)
        # 1. Filter Non-EPU Op
        if new_node.op not in ['PadEPU', 'MaxPoolEPU', 'Conv2DEPU']:
            result_graph_def.node.extend([new_node])
            continue
        # 2. Set attr async=true if all next op also on EPU
        if new_node.name in global_next_node_dict.keys():
            on_epu = True
            for next_node_name in global_next_node_dict[new_node.name]:
                next_node = global_node_dict[next_node_name]
                if next_node.op not in ['PadEPU', 'MaxPoolEPU', 'Conv2DEPU']:
                    on_epu = False
                    break
            if on_epu:
                new_node.attr['async'].CopyFrom(attr_value_pb2.AttrValue(b=True))
        result_graph_def.node.extend([new_node])
    return result_graph_def
