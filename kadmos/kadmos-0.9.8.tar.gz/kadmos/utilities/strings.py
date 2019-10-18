from __future__ import absolute_import, division, print_function

def find_between(s, first, last):
    """Function to find a target string that is located between two particular strings.

    :param s: string to search
    :type s: basestring
    :param first: the string in front of the target string
    :type first: basestring
    :param last: the string behind the target string
    :type last: basestring
    :return: the target string
    :rtype: basestring
    """
    try:
        start = s.index(first)+len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def find_until(s, until):
    """Function to find a target string that is located before a particular string.

    :param s: string to search
    :type s: basestring
    :param until: the string signifying the end of the target string
    :type until: basestring
    :return: target string
    :rtype: basestring
    """
    try:
        until = s.index(until)
        return s[0:until]
    except ValueError:
        return ""


def get_correctly_extended_latex_label(label, label_extension):
    """Function to obtain a correctly extended latex label.

    :param label: label to be extended
    :type label: str
    :param label_extension: extensions of the label
    :type label_extension: str
    :return: extended latex label
    :rtype: str
    """

    if '^{' in label and '^{' in label_extension:
        return label[:-1] + ',' + label_extension[2:]
    else:
        return label + label_extension
