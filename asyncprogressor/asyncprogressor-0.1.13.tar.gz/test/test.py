#!/usr/bin/env python3

from asyncprogressor import progressor_key
import time
@progressor_key
def long_function(s):
        time.sleep(s)

if __name__ == "__main__":
        long_function(10)
        
