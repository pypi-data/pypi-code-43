import numpy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as image
import matplotlib.animation as animation
import copy
import collections.abc

if 'jshtml' in matplotlib.rcsetup.validate_movie_html_fmt.valid:
  matplotlib.rc('animation', html='jshtml')
else:
  matplotlib.rc('animation', html='html5')

def histogram_plot(*args, **kwargs): #not used in the textbook
    plt.hist(*args, **kwargs)
    plt.show()

def image_preprocess(data):
  for i in range(0,len(data)):
    for j in range(0,len(data[i])):
      if isinstance(data[i][j], collections.abc.Sequence):
        if len(data[i][j]) < 3:
            raise ValueError("color pixel should be an array of length 3")
        for k in range(0,3):
          data[i][j][k] = float(data[i][j][k])
      else:
        if not (type(data[i][j]) is int or type(data[i][j]) is float):
          raise TypeError("monochrome image should be a 2d-array of numbers")
        v = float(data[i][j])
        data[i][j] = [v, v, v]

def image_show(data):
    if not (isinstance(data, collections.abc.Sequence) and
            isinstance(data[0], collections.abc.Sequence)):
        raise TypeError("image_show: argument should be an image (i.e., a 2d-array)")
    tmp = copy.deepcopy(data)
    image_preprocess(tmp)
    picture = plt.imshow(tmp)
    plt.show()
    return picture

def animation_show(data):
    if not (isinstance(data, collections.abc.Sequence) and
            isinstance(data[0], collections.abc.Sequence) and
            isinstance(data[0][0], collections.abc.Sequence)):
        raise TypeError("animation_show: argument should be an array of images (i.e., a 2d-array)")
    fig = plt.figure()
    a = []
    for i in range(0,len(data)):
        tmp = copy.deepcopy(data[i])
        image_preprocess(tmp)
        a.append([plt.imshow(tmp)])
    ani = animation.ArtistAnimation(fig, a, interval=500)
    plt.show()
    return ani

def linear_fit(data):
  if not isinstance(data, collections.abc.Sequence):
    TypeError("linear_fit: argument should be an array")
  xdata = [i[0] for i in data]
  ydata = [i[1] for i in data]
  fitp = numpy.poly1d(numpy.polyfit(xdata, ydata, 1))
  ma = max(xdata)
  mi = min(xdata)
  xp = numpy.linspace(mi, ma, (ma - mi))
  plt.plot(xdata, ydata, '.', xp, fitp(xp), '-')
  plt.show()

import matplotlib.cm as cm

def plotdata(data, line=False, **kwargs):
  if line:
    pltfun = plt.plot
  else:
    pltfun = plt.scatter
  if not isinstance(data, collections.abc.Sequence):
    TypeError("plotdata: argument should be an array")
  if isinstance(data[0], collections.abc.Sequence):
    if isinstance(data[0][0], collections.abc.Sequence):
      plot_clusters(data)
    else:
      xdata = [ i[0] for i in data ]
      ydata = [ i[1] for i in data ]
      pltfun(xdata, ydata, **kwargs)
  else:
    xdata = [ i for i in range(0,len(data)) ]
    pltfun(xdata, data, **kwargs)
  plt.show()

def plot_clusters(data, **kwargs):
  cnum = len(data)
  n = 0
  for x in data:
    n = n + len(x)
  xdata = [0] * n
  ydata = [0] * n
  colors = [0.0] * n
  k = 0
  for i in range(0,len(data)):
    for j in data[i]:
      xdata[k] = j[0]
      ydata[k] = j[1]
      colors[k] = cm.hsv(i/cnum)
      k = k + 1
  plt.scatter(xdata, ydata, c = colors, **kwargs)
  plt.show()


