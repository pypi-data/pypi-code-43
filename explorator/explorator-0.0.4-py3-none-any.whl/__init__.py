from . import general_info
from . import total_review
from . import functions

def libinfo():
    print('''
    Library explorator.
    Version: 0.0.2
    Structure:
    1. General info
        get_total
    2. Functions
        - Convert series to str
        - Convert series to date
        - Convert series to numeric (specify int or float)
    ''')
