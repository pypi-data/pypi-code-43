"""
Class to Display Ion Chromatograms and TIC
"""

################################################################################
#                                                                              #
#    PyMassSpec software for processing of mass-spectrometry data              #
#    Copyright (C) 2005-2012 Vladimir Likic                                    #
#    Copyright (C) 2019 Dominic Davis-Foster                                   #
#                                                                              #
#    This program is free software; you can redistribute it and/or modify      #
#    it under the terms of the GNU General Public License version 2 as         #
#    published by the Free Software Foundation.                                #
#                                                                              #
#    This program is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU General Public License for more details.                              #
#                                                                              #
#    You should have received a copy of the GNU General Public License         #
#    along with this program; if not, write to the Free Software               #
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.                 #
#                                                                              #
################################################################################


import warnings

import matplotlib
from matplotlib import figure, axes
import matplotlib.pyplot as plt

from pyms.Spectrum import MassSpectrum
from pyms.IonChromatogram import IonChromatogram
from pyms.Peak.List.Function import is_peak_list


default_filetypes = ["png", "pdf", "svg"]


class Display(object):
	"""
	Class to display Ion Chromatograms and Total Ion Chromatograms from class:`IonChromatogram.IonChromatogram`
	Uses matplotlib module pyplot to do plotting.
	
	If `fig` is not given then `fig` and `ax` default to:
	>>> fig = plt.figure()
	>>> ax = fig.add_subplot(111)
	
	if only `fig` is given then ax defaults to:
	>>> ax = fig.add_subplot(111)
	
	:param fig: figure object to use
	:type fig: matplotlib.figure.Figure, optional
	:param ax: axes object to use
	:type ax: matplotlib.axes.Axes, optional
	
	:author: Sean O'Callaghan
	:author: Vladimir Likic
	:author: Dominic Davis-Foster
	"""
	
	def __init__(self, fig=None, ax=None):
		"""
		Initialises an instance of Display class
		"""
		
		if fig is None:
			fig = plt.figure()
			ax = fig.add_subplot(111)
		
		elif isinstance(fig, matplotlib.figure.Figure) and ax is None:
			ax = fig.add_subplot(111)
			
		if not isinstance(fig, matplotlib.figure.Figure):
			raise TypeError("'fig' must be a matplotlib.figure.Figure object")
			
		if not isinstance(ax, matplotlib.axes.Axes):
			raise TypeError("'ax' must be a matplotlib.axes.Axes object")
			
		self.fig = fig
		self.ax = ax
		
		# Container to store plots
		self.__tic_ic_plots = []
		
		# color dictionary for plotting of ics; blue reserved
		# for TIC
		self.__col_ic = {0:'r', 1:'g', 2:'k', 3:'y', 4:'m', 5:'c'}
		self.__colour_count = 0  # counter to keep track of colors
		
		# Peak list container
		self.__peak_list = []
	
	def do_plotting(self, plot_label=None):
		"""
		Plots TIC and IC(s) if they have been created by plot_tic() or plot_ics().
		Adds detected peaks if they have been added by plot_peaks()

		:param plot_label: Optional to supply a label or other
				definition of data origin
		:type plot_label: str
		"""
		
		# if no plots have been created advise user
		if len(self.__tic_ic_plots) == 0:
			warnings.warn("""No plots have been created.
Please call a plotting function before calling 'do_plotting()'""", UserWarning)
			return
		
		if plot_label is not None:
			t = self.ax.set_title(plot_label)
		
		l = self.ax.legend()
		
		self.fig.canvas.draw
		
		# If no peak list plot, no mouse click event
		if len(self.__peak_list) != 0:
			cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
		#plt.show()
	
	@staticmethod
	def get_5_largest(intensity_list):
		"""
		Computes the indices of the largest 5 ion intensities for writing to console

		:param intensity_list: List of Ion intensities
		:type intensity_list: list

		:return: Indices of largest 5 ion intensities
		:rtype: list
		"""
		
		largest = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		
		# Find out largest value
		for i in range(len(intensity_list)):
			if intensity_list[i] > intensity_list[largest[0]]:
				largest[0] = i
		
		# Now find next four largest values
		for j in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
			for i in range(len(intensity_list)):
				# if intensity_list[i] > intensity_list[largest[j]] and intensity_list[i] < intensity_list[largest[j-1]]:
				if intensity_list[largest[j]] < intensity_list[i] < intensity_list[largest[j - 1]]:
					largest[j] = i
		
		return largest
	
	def onclick(self, event):
		"""
		Finds the 5 highest intensity m/z channels for the selected peak.
		The peak is selected by clicking on it.
		If a button other than the left one is clicked, a new plot of the mass spectrum is displayed

		:param event: a mouse click by the user
		"""
		
		intensity_list = []
		mass_list = []
		
		for peak in self.__peak_list:
			# if event.xdata > 0.9999*peak.rt and event.xdata < 1.0001*peak.rt:
			if 0.9999 * peak.rt < event.xdata < 1.0001 * peak.rt:
				intensity_list = peak.get_mass_spectrum().mass_spec
				mass_list = peak.get_mass_spectrum().mass_list
		
		largest = self.get_5_largest(intensity_list)
		
		if len(intensity_list) != 0:
			print("mass\t intensity")
			for i in range(10):
				print(mass_list[largest[i]], "\t", intensity_list[largest[i]])
		else:  # if the selected point is not close enough to peak
			print("No Peak at this point")
		
		# Check if a button other than left was pressed, if so plot mass spectrum
		# Also check that a peak was selected, not just whitespace
		if event.button != 1 and len(intensity_list) != 0:
			self.plot_mass_spec(event.xdata, mass_list, intensity_list)
		
	def plot_ic(self, ic, **kwargs):
		"""
		Plots an Ion Chromatogram

		:param ic: Ion Chromatograms m/z channels for plotting
		:type ic: class:`pyms.IonChromatogram.IonChromatogram`

		:param: **kwargs : `matplotlib.lines.Line2D` properties, optional
			*kwargs* are used to specify properties like a line label (for
			auto legends), linewidth, antialiasing, marker face color.

			Example::

			>>> plot_ic(im.get_ic_at_index(5), label='IC @ Index 5', linewidth=2)

			See https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.lines.Line2D.html
			for the list of possible kwargs
		"""
		
		if not isinstance(ic, IonChromatogram):
			raise TypeError("'ic' must be an IonChromatogram")
		
		plot = self.ax.plot(ic.time_list,
							 ic.intensity_array,
							 self.__col_ic[self.__colour_count], **kwargs)
		
		self.__tic_ic_plots.append(plot)
	
		if self.__colour_count == 5:
			self.__colour_count = 0
		else:
			self.__colour_count += 1
		
		self.__tic_ic_plots.append(plot)
		
		# Set axis ranges
		self.ax.set_xlim(min(ic.time_list), max(ic.time_list))
		self.ax.set_ylim(bottom=0)
		
		return plot
	
	def plot_mass_spec(self, mass_spec, **kwargs):
		"""
		Plots a Mass Spectrum
		
		:param mass_spec: The mass spectrum at a given time/index
		:type mass_spec: class:`Spectrum.MassSpectrum`
		
		:param: **kwargs : `matplotlib.lines.Line2D` properties, optional
			*kwargs* are used to specify properties like a line label (for
			auto legends), linewidth, antialiasing, marker face color.

			Example::

			>>> plot_mass_spec(im.get_ms_at_index(5), linewidth=2)
			>>>	ax.set_title(f"Mass spec for peak at time {im.get_time_at_index(5):5.2f}")

			See https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.lines.Line2D.html
			for the list of possible kwargs
		"""
		
		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("'mass_spec' must be a MassSpectrum")
		
		mass_list = mass_spec.mass_list
		intensity_list = mass_spec.mass_spec
		
		# to set x axis range find minimum and maximum m/z channels
		max_mz = mass_list[0]
		min_mz = mass_list[0]
		
		for i in range(len(mass_list)):
			if mass_list[i] > max_mz:
				max_mz = mass_list[i]
		
		for i in range(len(mass_list)):
			if mass_list[i] < min_mz:
				min_mz = mass_list[i]
		
		plot = self.ax.bar(mass_list, intensity_list, **kwargs)
		
		# Set axis ranges
		self.ax.set_xlim(min_mz, max_mz)
		self.ax.set_ylim(bottom=0)
		
		return plot
	
	def plot_peaks(self, peak_list, label="Peaks"):
		"""
		Plots the locations of peaks as found by PyMassSpec.

		:param peak_list: List of peaks
		:type peak_list: list of class:`pyms.Peak.Class.Peak` objects

		:param label: label for plot legend, default "Peaks"
		:type label: str, optional
		"""
		
		if not is_peak_list(peak_list):
			raise TypeError("'peak_list' must be a list of Peak objects")
		
		time_list = []
		height_list = []
		
		# Copy to self.__peak_list for onclick event handling
		self.__peak_list = peak_list
		
		for peak in peak_list:
			time_list.append(peak.rt)
			height_list.append(sum(peak.get_mass_spectrum().mass_spec))
		
		self.__tic_ic_plots.append(plt.plot(time_list, height_list, 'o', label=label))
	
	def plot_tic(self, tic, **kwargs):
		"""
		Plots a Total Ion Chromatogram

		:param tic: Total Ion Chromatogram
		:type tic: class:`pyms.IonChromatogram.IonChromatogram`

		:param: **kwargs : `matplotlib.lines.Line2D` properties, optional
			*kwargs* are used to specify properties like a line label (for
			auto legends), linewidth, antialiasing, marker face color.

			Example::

			>>> plot_tic(im.get_ic_at_index(5), label='IC @ Index 5', linewidth=2)

			See https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.lines.Line2D.html
			for the list of possible kwargs
		"""
		
		if not isinstance(tic, IonChromatogram) or not tic.is_tic():
			raise TypeError("'tic' must be an Ion Chromatogram object representing a total ion chromatogram")
		
		plot = self.ax.plot(tic.time_list, tic.intensity_array, **kwargs)
		
		self.__tic_ic_plots.append(plot)
		
		# Set axis ranges
		self.ax.set_xlim(min(tic.time_list), max(tic.time_list))
		self.ax.set_ylim(bottom=0)
		
		return plot
	
	def save_chart(self, filepath, filetypes=None):
		
		if filetypes is None:
			filetypes = default_filetypes
		
		matplotlib.use("Agg")
		
		for filetype in filetypes:
			# plt.savefig(filepath + ".{}".format(filetype))
			self.fig.savefig(filepath + ".{}".format(filetype))
		plt.close()
	
	def show_chart(self):
		
		matplotlib.use("TkAgg")
		
		self.fig.show()
		plt.close()



