# -*- coding: utf-8 -*-
import cv2
import sys
import argparse
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from tflex import utils
from fpdf import FPDF


def get_parser():
    parser = argparse.ArgumentParser(
        description='Verify the correctness of the source frozen model(.pb) conversion.')
    parser.add_argument(
        '--frozen_model', '-f',
        type=str,
        default='',
        help="Source frozen model with .pb file.")
    parser.add_argument(
        '--optimized_model', '-o',
        type=str,
        default='',
        help="Target optimized model with .tflex file.")
    parser.add_argument(
        '--map_file', '-m',
        type=str,
        default='',
        help="The map.txt file generated automatically during model conversion process.")
    parser.add_argument(
        '--image_file', '-i',
        type=str,
        default='',
        help="An image (e.g., ILSVRC2012_val_00013716.JPEG) is required for inference.")

    return parser


def main():
    parser = get_parser()
    flags = parser.parse_args()
    if flags.frozen_model and flags.optimized_model and flags.map_file and flags.image_file:
        new_names = ['new node']
        old_names = ['old node']
        func_names = ['function']
        for line in open(flags.map_file, 'r').readlines():
            infos = line.strip().split(',')
            new_names.append(infos[0])
            old_names.append(infos[1])
            func_names.append(infos[2])
        print('start')
        new_graph, input_names, _ = utils.import_graph(flags.optimized_model)
        d_input = new_graph.get_tensor_by_name(input_names[0] + ':0')
        d_outputs = [new_graph.get_tensor_by_name(name + ':0') for name in new_names[1:]]

        input_shape = [each._value if each._value is not None else 3 for each in d_input.get_shape()]
        print('input_shape =', type(input_shape), input_shape)
        input_image = np.ones(input_shape)
        if flags.image_file is not None:
            print('image_file =', flags.image_file)
            input_image = cv2.resize(cv2.imread(flags.image_file), (input_shape[1], input_shape[2]))
            input_image = np.array([input_image for _ in range(3)])

        print('input_image =', input_image.mean())
        # input_image = np.expand_dims(input_image, axis=0)

        new_res = tf.Session(graph=new_graph).run(d_outputs, feed_dict={d_input: input_image})
        new_res = [v.mean() for v in new_res]
        old_graph, __, ___ = utils.import_graph(flags.frozen_model)
        d_input = old_graph.get_tensor_by_name(input_names[0] + ':0')
        d_outputs = [old_graph.get_tensor_by_name(name + ':0') for name in old_names[1:]]

        old_feed_dict = {d_input: input_image}
        for op in old_graph.get_operations():
            if op.name[0] != 'i':
                continue
            if str(op).__contains__('"Placeholder"') and op.name not in input_names:
                print(op.name)
                this_input = old_graph.get_tensor_by_name(op.name + ':0')
                this_shape = [each._value if each._value is not None else 3 for each in this_input.get_shape()]
                old_feed_dict[this_input] = np.ones(this_shape)

        print('start calcu old')
        old_res = tf.Session(graph=old_graph).run(d_outputs, feed_dict=old_feed_dict)
        print('finish calcu')
        old_res = [v.mean() for v in old_res]

        plt.figure()
        num = len(func_names) - 1
        nums = list(range(num + 1))[1:]
        plt.xlabel('node index')
        plt.ylabel('mean value')
        plt.title('The mean value from new node and old node')

        plt.plot(nums, new_res, color='red', label='new node')
        plt.plot(nums, old_res, color='blue', label='old node')
        plt.legend()
        plt.savefig("v1.jpg")
        img = cv2.imread("v1.jpg")
        h0, w0, _ = img.shape

        conclusion = 'Conversion validation passes'
        error = 0.1
        print('*' * 120)
        for v in new_res, old_res, new_names[1:], old_names[1:], func_names[1:]:
            print(len(v), v)
        print('*' * 120)
        for n_r, o_r, n_n, o_n, func in zip(new_res, old_res, new_names[1:], old_names[1:], func_names[1:]):
            print(n_r, o_r, n_n, o_n, func)
            if n_r < (1 - error) * o_r or n_r > (1 + error) * o_r:
                print(type(n_n), type(o_n), func)
                conclusion = 'The conversion is wrong, the first error node is (' + n_n + ' --> ' + o_n + '), it is produced by the function ( ' + func + ' )'
                break
        print('conclusion =', conclusion)
        pdf = FPDF('p', 'mm', (605, 792))
        pdf.add_page()
        pdf.set_font('Times', 'B', 25.0)
        epw = pdf.w - 2 * pdf.l_margin
        col_widths = [5, 5, 3]
        col_width = epw / (1 + sum(col_widths))
        pdf.cell(epw, 0.0, 'Demographic data', align='C')
        pdf.set_font('Times', '', 20.0)
        pdf.ln(5)
        pdf.write(10, '1.Conclusion:')

        pdf.set_font('Times', '', 20.0)
        pdf.ln(10)
        pdf.write(10, conclusion)

        pdf.set_font('Times', '', 20.0)
        pdf.ln(20)
        pdf.write(10, '2.Mapping Relational Table:')

        pdf.set_font('Times', '', 10.0)
        pdf.ln(10)
        th = pdf.font_size
        for i in range(num):
            pdf.cell(col_width, 2 * th, str(i) if i > 0 else 'index', border=1)
            for each, datum in zip(col_widths, [new_names, old_names, func_names]):
                # Enter data in colums
                pdf.cell(each * col_width, 2 * th, str(datum[i]), border=1)

            pdf.ln(2 * th)
        # pdf.add_font('TTF')
        pdf.set_font('Times', '', 20.0)
        pdf.ln(20 - 2 * th)
        pdf.write(10, '3.The value from new_node and old_node:')

        pdf.ln(9)
        pdf.image("v1.jpg", w=pdf.w / 1.0, h=h0 / w0 * pdf.w / 1.0)

        pdf.output('v1.pdf', 'F')
    else:
        parser.print_help(sys.stderr)


if __name__ == '__main__':
    main()
