# -*- coding: utf-8 -*-
import sys
import tflex
import argparse


def get_parser():
    parser = argparse.ArgumentParser(
        description='Convert source model(.pb,.h5,SavedModel) to target model(.tflex graph) supported on EPU.')
    parser.add_argument(
        '--keras_model', '-k',
        type=str,
        default='',
        help="Source model with .h5 file to be converted.")
    parser.add_argument(
        '--frozen_model', '-f',
        type=str,
        default='',
        help="Source model with .pb file to be converted.")
    parser.add_argument(
        '--saved_model', '-s',
        type=str,
        default='',
        help="Source SavedModel with .pb file and variables to be converted.")
    parser.add_argument(
        '--save_path', '-p',
        type=str,
        default='./',
        help="Pathname to save the optimized graph(e.g., ./model.tflex).")
    parser.add_argument(
        '--input_arrays', '-i',
        type=str,
        default=None,
        help="String of input node names. If your model has more inputs, please use tflexconverter -i input_1,input_2.")
    parser.add_argument(
        '--output_arrays', '-o',
        type=str,
        default=None,
        help="String of output node names. If your model has more outputs, please use tflexconverter -o output_1,output_2.")
    parser.add_argument(
        '--device', '-d',
        type=str,
        default='/device:EPU:0',
        help="EPU devices assigned to the Conv2D, MaxPool and Pad ops, default is /device:EPU:0.")
    parser.add_argument(
        '--level', '-l',
        type=int,
        default=4,
        help="Selection of 5 optimal combination levels. For example, `level=1`: fundamental optimization;`level=2`: fundamental and batchnormalization optimization; `level=3`: fundamental, batchnormalization and EPU core optimization; `level=4`: fundamental, batchnormalization, EPU core and EPU Advanced optimization; `level=5`: fundamental, batchnormalization, EPU core, EPU Advanced and additional optimization. Default `level=4` means that the first four optimizations will be executed.")
    parser.add_argument(
        '--strict_padding', '-r',
        dest='strict_padding',
        action='store_true',
        help="EPU MaxPool only support padding is SAME or VALID(without remnant in W/H). If True is set, it will execute on the CPU.")
    parser.add_argument(
        '--start_node_names', '-t',
        type=str,
        default=None,
        help="The starting nodes are set as the initial input nodes for optimization to flexibly control the starting position in the scope of optimization.")
    parser.add_argument(
        '--end_node_names', '-e',
        type=str,
        default=None,
        help="The ending nodes are set as the last output nodes for optimization to flexibly control the ending position in the scope of optimization.")
    return parser


def extract_node_names(flags):
    input_arrays = []
    output_arrays = []
    start_node_names = []
    end_node_names = []
    if flags.input_arrays and flags.output_arrays:
        for name in flags.input_arrays.split(','):
            input_arrays.append(name)
        for name in flags.output_arrays.split(','):
            output_arrays.append(name)
    if not (flags.start_node_names or flags.end_node_names):
        start_node_names = end_node_names = None
    else:
        if flags.start_node_names:
            for name in flags.start_node_names.split(','):
                start_node_names.append(name)
        else:
            start_node_names = None
        if flags.end_node_names:
            for name in flags.end_node_names.split(','):
                end_node_names.append(name)
        else:
            end_node_names = None

    return input_arrays, output_arrays, start_node_names, end_node_names


def main():
    parser = get_parser()
    flags = parser.parse_args()
    input_arrays, output_arrays, start_node_names, end_node_names = extract_node_names(flags)
    if flags.frozen_model:
        converter = tflex.Converter.from_frozen_graph(flags.frozen_model, input_arrays, output_arrays)
        converter.convert(flags.save_path, flags.device, flags.level, flags.strict_padding, start_node_names,
                          end_node_names)

    elif flags.keras_model:
        converter = tflex.Converter.from_keras_model(flags.keras_model, input_arrays=input_arrays,
                                                     output_arrays=output_arrays)
        converter.convert(flags.save_path, flags.device, flags.level, flags.strict_padding, start_node_names,
                          end_node_names)
    elif flags.saved_model:
        converter = tflex.Converter.from_saved_model(flags.saved_model, input_arrays=input_arrays,
                                                     output_arrays=output_arrays)
        converter.convert(flags.save_path, flags.device, flags.level, flags.strict_padding, start_node_names,
                          end_node_names)
    else:
        parser.print_help(sys.stderr)


if __name__ == '__main__':
    main()
