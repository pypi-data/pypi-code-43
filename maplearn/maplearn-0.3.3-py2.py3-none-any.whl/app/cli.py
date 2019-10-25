# -*- coding: utf-8 -*-
"""
Command Line Interface (cli)

This module serves only as an interface between:

* what user inputs
* parameters stored in 'config' object
"""
from __future__ import print_function

import argparse

import maplearn
from maplearn.app.config import Config

cfg = Config(None)

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=maplearn.__doc__,
                                 epilog="Mapping Learning is a free software \
                                 (lGPL). Version %s" % maplearn.__version__)
parser.add_argument('-c', "--config-file",
                    help='path to the configuration file to be used')

# IO
io = parser.add_argument_group('io')
io.add_argument('-s', "--io-samples", 
                type=str, default=None,
                help="samples used to fit machine learning on")
io.add_argument('-lab', "--io-label", default=None,
                help="attribute containing names of labels")
io.add_argument('-lab_id', "--io-label_id", default=None,
                help="attribute containing codes (integers) of labels")
io.add_argument('-f', "--io-features", default=None,
                help="list of features to use")
io.add_argument('-d', "--io-data", default=None,
                help="dataset to apply machine learning on")
io.add_argument('-out', "--io-output", default=None,
                help="output directory where results and report will be stored")

# Preprocessing
preprocess = parser.add_argument_group('preprocess')
preprocess.add_argument('-scale', "--preprocess-scale", default=None,
                        action='store_true',
                     help="scale features before processing machine learning")
preprocess.add_argument('-red', "--preprocess-reduce", default=None,
                     help="dataset will be reduced before processing, using \
                         specified algorithm")

preprocess.add_argument('-n', "--preprocess-ncomp", type=int, default=None,
                     help="number of dimensions expected after reduction. \
                     only considered when reduction is asked (-red)")
preprocess.add_argument('-sep', "--preprocess-separability",
                        action='store_true', default=None,
                     help="analyse separability of samples")
preprocess.add_argument('-b', "--preprocess-balance", action='store_true',
                        default=None,
                        help="balance samples to get similar number of \
                              individuals between classes")

# Processing
process = parser.add_argument_group('process')
process.add_argument('-t', "--process-type",
                     choices=['classification', 'clustering', 'regression'],
                     default=None,
                     help="kind of process to apply to dataset")
process.add_argument('-k', "--process-kfold", type=int, default=None,
                     help="Number of folds to test fitting/prediction\
                           (default:%i)" % cfg.process['kfold'])
process.add_argument('-algo', "--process-algorithm", default=None,
                     help="algorithm(s) to apply (separated by ',')")
process.add_argument('-optim', "--process-optimize", default=None, 
                     action='store_true',
                     help="look for parameters of algorithms to get a better\
                           accuracy (default:False)")
process.add_argument('-pred', "--process-predict", action='store_true',
                     default=None,
                     help="Results should be predicted on the whole dataset")
process.add_argument('-dist', "--process-distance", default=None,
                     help="Type of distance used (default:%s)" \
                          % cfg.process['distance'])

# parsing arguments
args = parser.parse_args()

if 'config_file' in args.__dict__ and not args.__dict__['config_file'] is None:
    cfg = Config(args.__dict__['config_file'])
    cfg.read()
    print('Config file: %s' % args.__dict__['config_file'])
    args.__dict__.pop('config_file')

for k,v in args.__dict__.items():
    if v is not None and v != '':
        print(k, v)
        if hasattr(k, 'name'):
            v = str(k.name) # use filepaths as string instead of IOTextWrapper
            print("CLI(%s) : conversion to %s" % (k, v))
        cfg.__getattribute__(k.split('_')[0])[k[k.find('_') + 1:]] = v


