"""
Traveling Salesman problem for 2d (x,y) case
author: Valentyn Stadnytskyi
data: 2017 - Nov 17 2018

The traveling salesman algorithm takes an input array of coordinates and vary array (True/False)

"""
__vesrion__ = '1.0.0'
from time import  time, sleep
import sys
if sys.version_info[0] == 2:
    from time import clock as perf_counter
else:
    from time import perf_counter
import platform


def create_test_sequence(N, dim = 2):
    """

    """
    from numpy import random, array
    arr = (random.rand(N, dim)-0.5)*10
    arr[0] = array([0]*dim)
    arr[-1] = array([0]*dim)
    vary = arr[:,0]*0+1
    vary[0] = 0
    vary[-1] = 0
    return arr, vary

def euclidean_distance(i,j):
    """
    return euclidean_distance between two points
    """
    from numpy import array, nan
    dim_i = len(i)
    dim_j = len(j)
    if dim_i == dim_j:
        dim = dim_i
        distance = ((array(i) - array(j))**2).sum()**0.5
    else:
        distance = nan
    return distance

def total_distance(arr):
    """
    returns total distance as a sum of distances.
    """
    length = arr.shape[0]
    sum_distance = 0.0
    for i in range(length-1):
        a = arr[i]
        b = arr[i+1]
        sum_distance += euclidean_distance(a,b)
    return sum_distance

def distance(i,j):
    """
    simple wrapper around euclidean_distance
    """
    return euclidean_distance(i,j)

def minimize(arr, vary,  method = 'brute_force', N = 300):
    if method == 'brute_force':
        for i in range(int(N)):
            arr = minimize_brute_force_once(arr)
        return arr
    elif method == 'temperature':
        return arr

def minimize_brute_force_once(arr):
    """
    complete random minimization algorithm; slow and inefficient
    """
    from numpy.random import shuffle
    from numpy import concatenate, copy
    mid_array = arr[1:-1]
    new_mid_array = copy(mid_array)

    new_arr = copy(arr)
    new_arr[0] = arr[0]
    new_arr[-1] = arr[-1]

    shuffle(new_mid_array)
    new_arr[1:-1] = new_mid_array

    distance = total_distance(arr)
    new_distance = total_distance(new_arr)
    if new_distance < distance:
        return new_arr
    else:
        return arr

def minimize_temperature(self):
    """
    """
    import random, numpy, math, copy
    tour = list(self.sequence)
    cities = self.data
    N = len(self.sequence)
    for temperature in numpy.logspace(0,5,num=100000)[::-1]:
        [i,j] = sorted(random.sample(list(range(N)), 2));
        newTour =  tour[:i] + tour[j:j + 1] +  tour[i + 1:j] + tour[i:i + 1] + tour[j+1:];
        if math.exp((sum([ math.sqrt(sum([(cities[tour[(k+1) % N]][d] - cities[tour[k % N]][d])**2 for d in [0,1] ])) for k in [j,j-1,i,i-1]]) - sum([math.sqrt(sum([(cities[newTour[(k+1) % N]][d] - cities[newTour[k % N]][d])**2 for d in [0,1] ])) for k in [j,j-1,i,i-1]])) / temperature) > random.random():
            self.sequence = copy.copy(newTour);

def init(data):
    from numpy import array
    self.data = data
    self.length = int(data.size/2)
    self.sequence = range(1, self.length)

def run(data):
    self.init(data)
    self.minimize(N=500)
    return self.sorted_data

@property
def sorted_data(self):
    from numpy import array
    data = []
    data.append(self.data[0])
    for item in self.sequence:
        data.append(self.data[item])
    data.append(self.data[0])
    return array(data)






##### OLD functions
def matrix(arr):
    from numpy import zeros, roll, nan, nanmax, arange
    length = int(arr.size/2)
    N_vector = arange(0, length,1)
    x_vector = arr[:, 0]
    y_vector = arr[:, 1]
    Mx = zeros((length, length))
    My = zeros((length, length))
    Mn = zeros((length, length))
    for i in range(length):
        Mx[i] = roll(x_vector, i)
        My[i] = roll(y_vector, i)
        Mn[i] = roll(N_vector, i)
    return Mx, My, Mn

def minimize_matrix(Mx, My, Mn):
    from numpy import matmul, nan, where, nanmax
    Dx = matmul(Mx, Mx.T)
    Dy = matmul(My, My.T)
    length = Mx.shape[0]
    D = Dx+Dy
    for i in range(length):
        D[i,i] = nan
    res = where(D == nanmax(D))
    return res

def test(self):
    global Mn
    N = 5
    self.init(N)
    print(self.minimize())
    Mx, My, Mn = self.matrix()
    print(Mn)
    self.plot_x()
    return Mn,Mx,My

def plot(arr, vary = None, labels = None):
    """
    visualizes the array of coordintes. Parameters vary and labels can be used to customize the graph. Do not work for now. TODO.
    """
    from matplotlib import pyplot as plt
    from numpy import where
    plt.ion()
    if vary is None:
        vary = arr[:,0]*0+1
        vary[0] = vary[-1] = 0
    x = arr[:,0]
    y = arr[:,1]
    x_data = x[where(vary != 0)]
    y_data = y[where(vary != 0)]
    x_center = x[where(vary == 0)]
    y_center = y[where(vary == 0)]
    if labels is None:
        n = list(range(len(x-2)))
    fig, ax = plt.subplots()
    ax.plot(x, y, '-o')
    for i, txt in enumerate(n):
        ax.annotate(txt, (x[i], y[i]))
    plt.show()

if __name__ == '__main__':
    from pdb import pm
    arr, vary = create_test_sequence(10)
    total_dist = total_distance(arr)
