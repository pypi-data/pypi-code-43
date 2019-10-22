"""
This package offers a set of classes and functions to handle dna sequences
and files commonly used in bioinformatics, such as FASTA and FASTQ files.

For documentation please visit https://dinopy.readthedocs.org or use the 
python help-function.
You can also build the help files yourself after checking out the code
from https://bitbucket.org/HenningTimm/dinopy .
"""

__version__ = '2.0.2'

__all__ = ['fasta_reader', 'fasta_writer', 'fastq_reader', 'fastq_writer', 'auxiliary', 'shaping', 'shape',
           'processors', 'definitions', 'exceptions', 'output_opener', 'nameline_parser', 'sam_reader', 'sam_writer',
           'sambam']
from .output_opener import OutputOpener
from .fastq_reader import FastqReader
from .fasta_reader import FastaReader
from .fastq_writer import FastqWriter
from .fasta_writer import FastaWriter
from .sam_reader import SamReader
from .sam_writer import SamWriter
from .nameline_parser import NamelineParser
from . import auxiliary
from . import shaping
from . import processors
from .processors import qgrams, complement, reverse_complement
from . import fai_io
from .definitions import *
from .exceptions import *
from . import sambam
