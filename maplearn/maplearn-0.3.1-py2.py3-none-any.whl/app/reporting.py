# -*- coding: utf-8 -*-
"""
**Report writer:** generates html from text

ReportWriters catches the system standard output (used with print for example)
and writes everything on a chosen html file. The text is formatted in html by
means of markdown library.
"""
from __future__ import unicode_literals

import os
import sys
import webbrowser
from shutil import copytree
from pkg_resources import resource_filename
import numpy as np
import markdown

from maplearn.datahandler.plotter import Plotter

from maplearn import logger

# list of usable browsers
BROWSERS = ('firefox', 'opera', 'chromium', 'konqueror', 'safari',
            'windows-default')

class ReportWriter(object):
    """
    Catches every strings printed in Markdown Language and outputs them in a
    text file and a HTML file.

    Args:
        filename (str): path to the file where report will be written

    Example:
        >>> reporter = ReportWriter('example')
        >>> print('#Example of report#')
        >>> print('This is an example')
        >>> reporter.close()

    Attributes:
        stdout: standard output catched by Report Writer
    """

    def __init__(self, filename):
        self.__ori_stdout = sys.stdout
        self.stdout = sys.stdout
        self.__file = filename
        self.__html_f = None
        self.open_(filename)

    def open_(self, filename, mode='w'):
        """
        Opens 2 files (one html file and on text file) to write standard output
        in both of them

        Args:
            * filename (str): path to the filename without extension. Text and
              HTML files will share this file name, but with different
              extensions (.txt and .html)
            * mode (str): mode used to open files ('w' or 'a' expected)
        """
        self.__html_f = open(filename + '.html', mode)
        self.__html_f.write("""
            <!DOCTYPE html><html lang="fr"><head>
            <meta charset="utf-8">
            <title>Mapping Learning</title>
            <link rel="stylesheet" href="style/style.css">
            </head><body>\n""")
        self.__file = filename

        # copy file necessary to report (style and icons)
        logger.debug('Copy files necessary to HTML report')
        for i in ['style', 'img']:
            try:
                copytree(resource_filename('maplearn.app', i),
                         os.path.join(os.path.dirname(self.__file), i))
            except OSError:
                logger.warning('%s already exists in report folder -> pass',
                               i)
    def write(self, text):
        """
        Writes given string in text file and html file

        Args:
            text (str): characters string to write
        """
        self.__html_f.write(markdown.markdown(text,
                            extensions=['markdown.extensions.attr_list',
                                        'markdown.extensions.tables']))

    def close(self):
        """
        Closes every opened files by ReportWrites and redirects printed strings
        to standard output. The HTML is finally displayed in web browser (if it
        is not text-based browser).
        """
        self.__html_f.write("\n</body>")
        self.__html_f.close()
        self.__html_f = None
        sys.stdout = self.__ori_stdout

        # look for webbrowser
        wb = None
        for i in BROWSERS:
            try:
                wb = webbrowser.get(i)
            except webbrowser.Error:
                logger.debug('Browser %s not found...', i)

        if wb is None:
            logger.warning('No browser found. Please see file://%s.html',
                           self.__file)
            return None

        # opens the report in webrowser
        try:
            wb.open("file://%s.html" % self.__file)
        except webbrowser.Error:
            logger.error('Web wrowser can\'t be opened. Look for %s file \
                         to read the report', self.__file+'.html')

    def flush(self):
        """
        Empty every coming flows
        """
        try:
            self.stdout.flush()
            self.__html_f.flush()
        except ValueError:
            self.open_(self.__file, 'a')


def str_table2(_headers=None, _cellsize=20, **kwargs):
    """
    Writes a table following Markdown format. You can specify if the table has
    a header or not, and the desired length of cells. The content of cells is
    given in **kwargs.

    Args:
        * _headers (list): list of character strings to write as header
        * _cellsize (int): number of characters in each cell
        * **kwargs: the content of cells

    Returns:
        str: formatted table
    """
    if _headers is not None and len(_headers) != len(kwargs):
        logger.warning("Headers contains more column than kwargs contains \
            using kwargs.keys() instead of _headers param")
        _headers = None
    if _headers is None:
        _headers = list(kwargs.keys())
    max_rows = max([len(v) for v in kwargs.values()])
    #Heads line
    res = "\n"+str_table_row(_headers, _cellsize)
    #Horizontal separator
    res += "\n"+str_table_row(
        [''.join(['-' * _cellsize]) for _ in range(len(kwargs))],
        _cellsize)
    for i in range(max_rows):
        line_arr = [("NA" if len(kwargs[k]) <= i else kwargs[k][i])
                    for k in _headers]
        res += "\n"+str_table_row(line_arr, _cellsize)
    return res

def str_table_row(lst, _cellsize):
    """
    Format a list of string characters as a row in a table (markdown format)

    Args:
        * lst (list): list of characters strings to format
        * _cellsize (int): size (number of characters) of cells in the row

    Returns:
        str: the formatted row
    """
    cellfmt = '%-{}s'.format(_cellsize)
    return '|'+('|'.join([cellfmt % i for i in lst]))+'|'
    #return '|'.join([cellfmt % i for i in lst])

def str_table(header, size=20, **kwargs):
    """
        retrocompatibility wrapper
    """
    return str_table2(_headers=header, _cellsize=size, **kwargs)

def str_extend(txt, size=20):
    """
    Extend a character string to the given size by adding space at the end

    Args:
        * txt (str): character string to extend
        * size (int): the wanted length for the character string

    Returns:
        str: the extended characters string
    """
    return str(('%%-%ds'%size)% txt)

def icon_msg(text, nature="info"):
    """
    Returns a given text as an information message (with an icon)

    Arg:
        * text (str): text to return
        * nature (str): nature of the message (info, warning or error)
    """
    return '\n![%s](img/%s.png){: .icon}*%s*\n' % (nature, nature, text)

def str_synthesis(*numbers):
    """
    Returns a list of numbers as a string corresponding to m (+/- 2*sd)

    Arg:
        *numbers: list of numbers to synthetize and return as a string

    Returns:
        str: synthesis of the list of numbers "m (+/- 2*sd)"
    """
    nb = np.array(numbers)
    return str("%.2f (+/-%.2f)" % (np.mean(nb), 2 * np.std(nb)))

def str_prop(counts, outdir, outfile):
    """
    Returns proportion of every number
    """
    str_msg = '\n\n<div style="clear:both;">\n</div>\n'
    __plt = Plotter(style="square", output=outdir)
    str_msg += __plt.donut(data=counts[1], labels=counts[0], file=outfile)
    str_msg += "**Repartition des %i classes (%i individus) :** \n" \
        % (counts[0].shape[0], np.sum(counts[1]))
    __perc = counts[1]*100/np.sum(counts[1])
    __synth = {'Classe':counts[0], 'Nombre':counts[1],
               'Pourcentage':  ["%.1f%%" % i for i in __perc]}
    str_msg += str_table(header=None, **__synth)
    str_msg += '\n\n<div style="clear:both;">\n</div>\n'
    __plt = None
    return str_msg