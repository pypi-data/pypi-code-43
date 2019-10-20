"""
Bandit plugin that checks for AWS keys. This code is adapted from:
https://github.com/dxa4481/truffleHog/blob/ac57eae8c5a46383975bb584dc9d7560f36c4a8d/truffleHog/truffleHog.py#L167
"""

from collections import Counter
import math
import re
import string

import bandit
from bandit.core import test_properties as test


AWS_ACCESS_KEY_ID_SYMBOLS = string.ascii_uppercase + string.digits
AWS_ACCESS_KEY_ID_REGEX = re.compile('[' +
                                     AWS_ACCESS_KEY_ID_SYMBOLS +
                                     ']{20}')
AWS_ACCESS_KEY_ID_MAX_ENTROPY = 3

AWS_SECRET_ACCESS_KEY_SYMBOLS = string.ascii_letters + string.digits + '/+='
AWS_SECRET_ACCESS_KEY_REGEX = re.compile('[' +
                                         AWS_SECRET_ACCESS_KEY_SYMBOLS +
                                         ']{40}')
AWS_SECRET_ACCESS_KEY_MAX_ENTROPY = 4.5


def shannon_entropy(data, symbols):
    """
    Source: http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html
    """
    if not data:
        return 0
    entropy = 0
    counts = Counter(data)
    for x in symbols:
        p_x = float(counts[x]) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy


@test.checks('Str')
@test.test_id('C100')
def hardcoded_aws_key(context):
    node = context.node
    if AWS_ACCESS_KEY_ID_REGEX.fullmatch(node.s):
        entropy = shannon_entropy(node.s, AWS_ACCESS_KEY_ID_SYMBOLS)
        if entropy > AWS_ACCESS_KEY_ID_MAX_ENTROPY:
            return bandit.Issue(
                severity=bandit.LOW,
                confidence=bandit.MEDIUM,
                text=("Possible hardcoded AWS access key ID: %r" % node.s))
    elif AWS_SECRET_ACCESS_KEY_REGEX.fullmatch(node.s):
        entropy = shannon_entropy(node.s, AWS_SECRET_ACCESS_KEY_SYMBOLS)
        if entropy > AWS_SECRET_ACCESS_KEY_MAX_ENTROPY:
            return bandit.Issue(
                severity=bandit.MEDIUM,
                confidence=bandit.MEDIUM,
                text=("Possible hardcoded AWS secret access key: %r" % node.s))
