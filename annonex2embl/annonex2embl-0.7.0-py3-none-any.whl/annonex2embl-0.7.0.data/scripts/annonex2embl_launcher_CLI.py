#!python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'annonex2embl'))
    import CLIOps

    CLIOps.start_annonex2embl()
