# -*- coding: utf-8 -*-
# system libraries
import os.path
import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(parent, "soscikit"))
print(os.path.join(parent, "soscikit"))
from run import main

main()

if __name__ == "__main__":
    main()