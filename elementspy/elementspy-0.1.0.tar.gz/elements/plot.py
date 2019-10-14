import collections
import logging
import pathlib

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


CURVE = dict()
AREA = dict(alpha=0.15, linewidths=0)
SCATTER = dict(alpha=0.15, linewidths=0, s=20)
DIST = dict(interpolation='none')
LINE = dict(ls='--', color='#444444')
BAR = dict()
COLORS = (
    '#377eb8', '#4daf4a', '#984ea3', '#e41a1c', '#ff7f00', '#a65628',
    '#f781bf', '#888888', '#a6cee3', '#b2df8a', '#cab2d6', '#fb9a99',
    '#fdbf6f')
LEGEND = dict(
    fontsize='medium', numpoints=1, labelspacing=0, columnspacing=1.2,
    handlelength=1.5, handletextpad=0.5)


class Figure:

  def __init__(
      self, columns=None, rows=None, title=None, figure=None, size=4):
    columns = columns or 1
    rows = rows or 1
    size = size if isinstance(size, (tuple, list)) else (size, size)
    if figure:
      self._fig, self._axes = figure, figure.get_axes()
    else:
      self._fig, self._axes = plt.subplots(
          ncols=columns, nrows=rows, squeeze=False,
          figsize=(size[0] * columns, size[1] * rows))
    if title:
      # Requires coordinating subplots rect with the legend if it exists.
      raise NotImplementedError
    self._rect = (0, 0, 1, 1)

  @property
  def figure(self):
    return self._fig

  @property
  def axes(self):
    return self._axes

  def legend(self, target=None, sources=None, **kwargs):
    target = target or self._fig
    sources = sources or self._axes
    sources = sources.flatten() if isinstance(sources, np.ndarray) else sources
    config = LEGEND.copy()
    config['loc'] = 'lower center'
    if kwargs.get('loc', None) == 'best':
      kwargs.pop('loc')  # Best location for a figure legend is the default.
    config.update(kwargs)
    # Positioning the legend by coordinates changes the meaning of the loc
    # keyword, which now refers to the anchor that is placed at the coordinates
    # rather than the corner used by the legend.
    if 'bbox_to_anchor' not in config:
      yloc, xloc = config['loc'].split()
      config['bbox_to_anchor'] = (
          dict(left=0, center=0.5, right=1)[xloc],
          dict(lower=0, center=0.5, upper=1)[yloc])
    # Collect legend entries.
    entries = collections.OrderedDict()
    for ax in sources:
      for handle, label in zip(*ax.get_legend_handles_labels()):
        entries[label] = handle
    legend = target.legend(entries.values(), entries.keys(), **config)
    # Style visual appearance.
    legend.set_zorder(2000)
    legend.get_frame().set_edgecolor('white')
    for line in legend.get_lines():
      line.set_alpha(1)
    # Adjust the rectangle of the subplot grid to make space for the legend.
    if target is self._fig:
      box = legend.get_window_extent(
          self._fig.canvas.get_renderer()).transformed(
              self._fig.transFigure.inverted())
      yloc, xloc = config['loc'].split()
      y0 = dict(lower=box.y1, center=0, upper=0)[yloc]
      y1 = dict(lower=1, center=1, upper=box.y0)[yloc]
      x0 = dict(left=box.x1, center=0, right=0)[xloc]
      x1 = dict(left=1, center=1, right=box.x0)[xloc]
      self._rect = (x0, y0, x1, y1)
      self._fig.tight_layout(rect=self._rect, h_pad=0.5, w_pad=0.5)
    return legend

  def save(self, filename, **kwargs):
    filename = pathlib.Path(filename).expanduser()
    filename.parent.mkdir(parents=True, exist_ok=True)
    config = {}
    config.update(kwargs)
    self._fig.savefig(filename, **config)


class Plot:

  def __init__(self, ax, title=None, xlabel=None, ylabel=None):
    self._ax = ax
    title and self._ax.set_title(title)
    xlabel and self._ax.set_xlabel(xlabel)
    ylabel and self._ax.set_ylabel(ylabel)
    self._index = 0
    self._xlim = (np.inf, -np.inf)
    self._random = np.random.RandomState(seed=0)
    self._logger = logging.getLogger('plot')

  @property
  def ax(self):
    return self._ax

  def curve(
      self, name, xs, ys,
      bins=None,
      curve=np.mean,
      area=lambda x: (np.mean(x) - np.std(x), np.mean(x) + np.std(x)),
      scatter=False,
      smooth=None,
      color=None,
      **kwargs):
    xs, ys = np.array(xs), np.array(ys)
    assert len(xs.shape) == 1 and len(ys.shape) == 1
    self._update_xlim(xs)
    xs, ys = self._sort_series(xs, ys)
    binned_xs, binned_ys = self._bin_series(xs, ys, bins)
    curve_ys = np.array([curve(y) for y in ys])
    binned_curve_ys = np.array([curve(y) for y in binned_ys])
    if curve:
      config = CURVE.copy()
      config['color'] = color or self._current_color()
      config['zorder'] = 1000 - 10 * self._index
      config['label'] = name
      config.update(kwargs)
      if smooth:
        data = self._smooth(xs, curve_ys, smooth)
      else:
        data = binned_xs, binned_curve_ys
      self._ax.plot(*data, **config)
    if scatter:
      config = SCATTER.copy()
      config['color'] = color or self._current_color()
      config['zorder'] = 1000 - 10 * self._index - 1
      config['label'] = name if not curve else None
      self._ax.scatter(xs, ys, **config)
    if area:
      config = AREA.copy()
      config['color'] = color or self._current_color()
      config['zorder'] = 1000 - 10 * self._index - 2
      config['label'] = name if (not curve and not scatter) else None
      below, above = np.array([area(y) for y in binned_ys]).T
      self._ax.fill_between(binned_xs, below, above, **config)
    self._index += 1

  def dist(self, name, xs, ys, resolution=20, xlim=None, ylim=None):
    xs, ys = np.array(xs), np.array(ys)
    assert len(xs.shape) == 1 and len(ys.shape) == 1
    self._update_xlim(xs)
    xs, ys = self._sort_series(xs, ys)
    xlim = xs.min(), xs.max()
    ylim = ys.min(), ys.max()
    xbins = np.linspace(*xlim, resolution)
    ybins = np.linspace(*ylim, resolution)
    xi, yi = np.meshgrid(xbins, ybins)
    xbins = np.linspace(*xlim, resolution + 1, endpoint=True)
    ybins = np.linspace(*ylim, resolution + 1, endpoint=True)
    zi = np.histogram2d(xs, ys, [xbins, ybins])[0].T.reshape(xi.shape)
    color = self._current_color()
    make_cmap = mpl.colors.LinearSegmentedColormap.from_list
    config = DIST.copy()
    config['cmap'] = make_cmap('name', [color + '00', color + 'ff'])
    config['zorder'] = 1000 - 10 * self._index
    config['aspect'] = 'auto'
    config['extent'] = (*xlim, *ylim)
    self._ax.matshow(zi.reshape((resolution, resolution)), **config)
    # Add empty area to create legend entry.
    self._ax.fill_between([], [], [], color=color, label=name)
    self._index += 1

  def line(self, name, ys, **kwargs):
    ys = np.array(ys)
    config = LINE.copy()
    config['color'] = self._current_color()
    config['zorder'] = 1000 - 10 * self._index
    config['label'] = name
    config.update(kwargs)
    self._ax.axhline(ys, **config)
    self._index += 1

  def bars(
      self, groups, names, ys, annotate=False, rotate=0, spacing=0.1):
    ys = np.array(ys)
    centers = np.arange(len(groups))
    scale = 1 - spacing
    width = scale * (1 / len(names))
    text_config = dict(
        xytext=(0, 1), textcoords='offset points', ha='center',
        va='bottom', rotation=rotate, fontsize=7)
    for name, heights in zip(names, ys.T):
      config = BAR.copy()
      config['color'] = self._current_color()
      config['label'] = name
      offset = scale * ((names.index(name) + 0.5) / len(names) - 0.5)
      rects = self._ax.bar(
          centers + offset, np.nan_to_num(heights), width, **config)
      for rect, height in zip(rects, heights.flatten()):
        text = None
        if annotate is True:
          text = f'{height}'
        if np.isnan(height):
          text = 'n/a'
        if callable(annotate):
          text = annotate
        if not text:
          continue
        position = (rect.get_x() + rect.get_width() / 2, rect.get_height())
        self._ax.annotate(text, xy=position, **text_config)
      self._index += 1
    self._ax.set_xlim(centers[0] - 0.5, centers[-1] + 0.5)
    self._ax.set_xticks(centers)
    self._ax.set_xticklabels(
        groups, rotation=rotate, ha='center', multialignment='right',
        fontdict={'fontsize': 9})
    self._ax.tick_params(axis='x', which='both', length=1.0, width=20.5)
    self._ax.spines['top'].set_visible(False)
    self._ax.spines['right'].set_visible(False)
    self._ax.spines['bottom'].set_visible(False)

  def legend(self, target=None, sources=None, **kwargs):
    config = LEGEND.copy()
    config.update(kwargs)
    target = target or self._ax
    sources = sources or [self._ax]
    entries = collections.OrderedDict()
    for ax in sources:
      for handle, label in zip(*ax.get_legend_handles_labels()):
        entries[label] = handle
    legend = target.legend(entries.values(), entries.keys(), **config)
    legend.set_zorder(2000)
    legend.get_frame().set_edgecolor('white')
    for line in legend.get_lines():
      line.set_alpha(1)
    return legend

  def _sort_series(self, xs, ys):
    order = np.argsort(xs)
    xs = np.array(xs)[order]
    ys = np.array(ys)[order]
    return xs, ys

  def _bin_series(self, xs, ys, bins):
    # Assume input arguments are already sorted.
    if bins is None:
      binned_xs = np.array(sorted(set(xs)))
    elif isinstance(bins, (int, float)):
      binned_xs = np.arange(*self._xlim, bins)
    elif len(bins) == len(xs):
      binned_xs = []
      current = None
      for x, bin_ in zip(xs, bins):
        if not current or current != bin_:
          current = bin_
          binned_xs.append(x)
      binned_xs.append(xs[-1])
      binned_xs = np.array(binned_xs)
    else:
      message = 'Bins should be None, number, or a list of data size.'
      raise ValueError(message)
    binned_ys = []
    for start, stop in zip([-np.inf] + list(binned_xs), binned_xs):
      left = (xs <= start).sum()
      right = (xs <= stop).sum()
      if left < right:
        binned_ys.append(ys[left:right])
      else:
        binned_ys.append([np.nan])
    assert len(binned_xs) == len(binned_ys), (len(binned_xs), len(binned_ys))
    return binned_xs, binned_ys

  def _update_xlim(self, xs):
    self._xlim = min(self._xlim[0], xs.min()), max(self._xlim[1], xs.max())
    self._ax.set_xlim(self._xlim)

  def _current_color(self):
    return COLORS[min(self._index, len(COLORS) - 1)]

  def _smooth(self, xs, ys, amount):
    # Add noise to avoid duplicate X values.
    epsilon = 1e-6 * (xs.min() - xs.max())
    xs += self._random.uniform(-epsilon, epsilon, xs.shape)
    xs, ys = self._sort_series(xs, ys)
    import scipy.interpolate
    assert 0 <= amount <= 1, amount
    strength2 = (len(xs) ** (1 - amount) - 1) / (len(xs) - 1)
    amount = 2 + int(strength2 * (len(xs) - 4))
    indices = np.linspace(1, len(xs) - 2, amount).astype(int)
    knots = xs[indices]
    # The degree k makes a big difference. Degree 1 results in piece-wise
    # linear interpolation but works well for all smoothing factors. Degree 2
    # gives a piece-wise quadratic interpolation that looks nicer but overfits
    # for small smoothing amounts.
    spline = scipy.interpolate.LSQUnivariateSpline(xs, ys, knots, k=2)
    smooth_xs = np.linspace(xs[1], xs[-2], 10 * len(xs))
    smooth_ys = spline(smooth_xs)
    smooth_ys = np.clip(smooth_ys, ys.min(), ys.max())
    return smooth_xs, smooth_ys
