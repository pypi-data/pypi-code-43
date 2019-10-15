#!/usr/bin/python

__author__      = "Sander Granneman"
__copyright__   = "Copyright 2019"
__version__     = "0.0.2"
__credits__     = ["Sander Granneman"]
__maintainer__  = "Sander Granneman"
__email__       = "sgrannem@staffmail.ed.ac.uk"
__status__      = "Production"

##################################################################################
#
#   Exceptions.py
#
#
#   Copyright (c) Sander Granneman 2019
#   
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#
##################################################################################

class AnnotationError(Exception):
    """ Called when an annotation could not be found in the GTF annotation file """
    pass

class SourceError(Exception):
    """ Called when the user specifies a source (i.e. CDS,exon,5UTR, etc) that does not exist """
    pass

class LookupError(Exception):
    """ Called when a variable could not be found in an array or dictionary """
    pass
    
class NoSequenceError(Exception):
    """ Called when no sequence information is available. Usually because the genomic reference sequence has not been loaded """
    pass
    
class InputError(Exception):
    """ Called when an additional input is required to run the function/method or when the user uses an incorrect input """
    pass
    
class BaseQualityError(Exception):
    """ Called when a base quality could not be calculated """
    pass
    
class FileTypeError(Exception):
    """ Called the program could not recognise the file type of the input file or when the file type is not supported """
    pass
    
class FormatError(Exception):
    """ Called when a file or sequence format could not be recognised """
    pass
    
class ProcessingError(Exception):
    """ Called when a specific method needs to be run or a file needs to be processed first in order to continue """
    pass
    
class NoResultsError(Exception):
    """ Called when the method or function did not return any results """
    pass
    
class ClusteringError(Exception):
    """ Called during a Clustering error """
    pass