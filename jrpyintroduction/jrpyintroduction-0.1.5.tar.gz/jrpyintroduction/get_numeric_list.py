from numpy.random import uniform
from numpy.random import seed
from numpy import round

def get_numeric_list():
    seed(0) # set the seed so always the same values
    x = list(round(uniform(-40,90,55748), decimals  = 2))
    return x
