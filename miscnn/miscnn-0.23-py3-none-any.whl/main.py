#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------#
#                   Library imports                   #
#-----------------------------------------------------#
# External libraries
import sys
import argparse
import os
# Internal libraries/scripts
import miscnn.neural_network as MIScnn_NN
import miscnn.evaluation as MIScnn_CV

#-----------------------------------------------------#
#                  Parse command line                 #
#-----------------------------------------------------#
# Implement a modified ArgumentParser from the argparse package
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message + "\n")
        self.print_help()
        sys.exit(2)
# Initialize the modifed argument parser
parser = MyParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                add_help=False, description=
    """
Description...

Author: Dominink Müller
Email: dominik.mueller@informatik.uni-augsburg.de
Chair: IT-Infrastructure for Translational Medical Research- University Augsburg (Germany)
""")
# Add arguments for mutally exclusive required group
required_group = parser.add_argument_group(title='Required arguments')
required_group.add_argument('-i', '--input', type=str, action='store',
                required=True, dest='args_input', help='Path to data directory')
# Add arguments for optional group
optional_group = parser.add_argument_group(title='Optional arguments')
optional_group.add_argument('-v', '--verbose', action='store_true',
                default=False, dest='args_verbose',
                help="Print all informations and warnings")
optional_group.add_argument('-h', '--help', action="help",
                help="Show this help message and exit")
# Parse arguments
args = parser.parse_args()

#-----------------------------------------------------#
#                   Configurations                    #
#-----------------------------------------------------#
from miscnn.configurations import get_options
config = get_options()
config["data_path"] = args.args_input

config["input_shape"] = (None, 128, 128, 1)     # Neural Network input shape
config["patch_size"] = (48, 128, 128)           # Patch shape/size
config["batch_size"] = 22                       # Number of patches in on step
config["overlap"] = (12, 32, 32)                # Overlap in (x,y,z)-axis
config["pred_overlap"] = False                  # Usage of overlapping patches in prediction

cases = list(range(268,269))

#-----------------------------------------------------#
#                    Runner code                      #
#-----------------------------------------------------#
# Output the configurations
print(config)

# Create the Convolutional Neural Network
#cnn_model = MIScnn_NN.NeuralNetwork(config)

# Train the Convolutional Neural Network model
#cnn_model.train(config["cases"])
# Dump the model
#cnn_model.dump("model")

# Load a model
#cnn_model.load("model")

# Predict a segmentation with the Convolutional Neural Network model
#cnn_model.predict(list(range(3,4)))

# Evaluate the Convolutional Neural Network
#MIScnn_CV.cross_validation(config)
#MIScnn_CV.leave_one_out(config)
#MIScnn_CV.split_validation(cases, config)


from miscnn.preprocessing import preprocessing_MRIs
from miscnn.data_io import batch_load
from miscnn.data_io import case_loader
from miscnn.utils.matrix_operations import concat_3Dmatrices
from utils.matrix_operations import slice_3Dmatrix
import math
from miscnn.preprocessing import create_batches

# Define overlap usage for patches
if not config["pred_overlap"]:
    cache_overlap = config["overlap"]
    config["overlap"] = (0,0,0)
# Iterate over each case
for id in cases:
    # Preprocess Magnetc Resonance Images
    mri = case_loader(id, config["data_path"], load_seg=False)
    patches_vol = slice_3Dmatrix(mri.vol_data,
                                 config["patch_size"],
                                 config["overlap"])
    steps = math.ceil(len(patches_vol) / config["batch_size"])
    batches_vol = create_batches(patches_vol,
                                 config["batch_size"],
                                 steps)
    print(str(id) + "\t" + str(mri.vol_data.shape) + "\t" + str(len(batches_vol)) + "\t" + str(batches_vol[0].shape))


    preprocessing_MRIs([id], config, training=False, validation=False)
    # pred_seg = concat_3Dmatrices(patches=batch_vol,
    #                             image_size=mri.vol_data.shape,
    #                             window=config["patch_size"],
    #                             overlap=(config["overlap"]))
# Reset overlap in config if required
if not config["pred_overlap"]:
    config["overlap"] = cache_overlap
