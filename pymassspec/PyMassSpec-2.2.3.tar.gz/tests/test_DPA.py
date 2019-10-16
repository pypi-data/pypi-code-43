import csv
import math
import operator

import numpy
import pytest

from tests.constants import *

from pyms.TopHat import tophat
from pyms.BillerBiemann import BillerBiemann, rel_threshold, num_ions_threshold
from pyms.IntensityMatrix import build_intensity_matrix_i
from pyms.GCMS.IO.JCAMP import JCAMP_reader
from pyms.Noise.SavitzkyGolay import savitzky_golay
from pyms.Peak.Function import peak_sum_area, peak_top_ion_areas
from pyms.Experiment import load_expr, Experiment
from pyms.DPA.Alignment import Alignment, exprl2alignment
from pyms.DPA.PairwiseAlignment import PairwiseAlignment, align_with_tree
from pyms.Peak.List.IO import store_peaks
from pyms.Peak.List.Function import composite_peak


eley_codes = ["ELEY_1_SUBTRACT", "ELEY_2_SUBTRACT", "ELEY_3_SUBTRACT", "ELEY_4_SUBTRACT", "ELEY_5_SUBTRACT"]
geco_codes = ["GECO_1_SUBTRACT", "GECO_2_SUBTRACT", "GECO_3_SUBTRACT", "GECO_4_SUBTRACT", "GECO_5_SUBTRACT"]

# within replicates alignment parameters
Dw = 2.5  # rt modulation [s]
Gw = 0.30  # gap penalty


@pytest.fixture(scope="module")
def expr_list(datadir, outputdir):
	# Create experiment files
	for jcamp_file in eley_codes:
		
		im = build_intensity_matrix_i(JCAMP_reader(datadir / f"{jcamp_file}.JDX"))
		
		# Intensity matrix size (scans, masses)
		n_scan, n_mz = im.size
		
		# noise filter and baseline correct
		for ii in range(n_mz):
			ic = im.get_ic_at_index(ii)
			ic_smooth = savitzky_golay(ic)
			ic_bc = tophat(ic_smooth, struct="1.5m")
			im.set_ic_at_index(ii, ic_bc)
		
		peak_list = BillerBiemann(im, points=9, scans=2)
		apl = rel_threshold(peak_list, 2)
		new_peak_list = num_ions_threshold(apl, 3, 3000)
		
		# ignore TMS ions and set mass range
		for peak in new_peak_list:
			peak.crop_mass(50, 400)
			peak.null_mass(73)
			peak.null_mass(147)
			
			# find area
			area = peak_sum_area(im, peak)
			peak.area = area
			area_dict = peak_top_ion_areas(im, peak)
			peak.ion_areas = area_dict
		
		expr = Experiment(jcamp_file, new_peak_list)
		
		# set time range for all experiments
		expr.sele_rt_range(["6.5m", "21m"])
		
		expr.dump(outputdir / f"{jcamp_file}.expr")
	
	# Load experiments
	expr_list = []
	for expr_code in eley_codes:
		expr = load_expr(outputdir / f"{expr_code}.expr")
		assert isinstance(expr, Experiment)
		expr_list.append(expr)
	
	return expr_list


def test_expr_inequality(expr_list):
	assert expr_list[0] != expr_list[1]


@pytest.fixture(scope="module")
def F1(expr_list):
	# do the alignment
	print('Aligning ELEY SUBTRACT')
	F1 = exprl2alignment(expr_list)
	assert isinstance(F1, list)
	
	return F1


@pytest.fixture(scope="module")
def T1(F1):
	T1 = PairwiseAlignment(F1, Dw, Gw)
	assert isinstance(T1, PairwiseAlignment)

	return T1


@pytest.fixture(scope="module")
def A1(T1):
	A1 = align_with_tree(T1, min_peaks=2)
	assert isinstance(A1, Alignment)
	
	assert isinstance(len(A1), int)
	assert len(A1) == 232
	A1.filter_min_peaks(5)
	assert len(A1) == 50
	
	return A1


def test_alignment_errors(F1, A1, outputdir):
	for type in [test_string, test_int, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			PairwiseAlignment(F1, type, Gw)
		with pytest.raises(TypeError):
			PairwiseAlignment(F1, Dw, type)
	
	for type in [test_float, test_string, test_int, test_list_ints, test_list_strs, test_dict, test_tuple]:
		with pytest.raises(TypeError):
			exprl2alignment(type)
		with pytest.raises(TypeError):
			PairwiseAlignment(type, Dw, Gw)
		with pytest.raises(TypeError):
			Alignment(type)
	
	for type in [test_float, test_string, test_dict, test_list_strs, test_list_ints]:
		with pytest.raises(TypeError):
			A1.filter_min_peaks(type)
	
	for type in [test_float, test_int, test_dict, test_list_strs, test_list_ints]:
		with pytest.raises(TypeError):
			A1.write_csv(type, outputdir / 'alignment_area.csv')
		with pytest.raises(TypeError):
			A1.write_csv(outputdir / 'alignment_rt.csv', type)
		with pytest.raises(TypeError):
			A1.write_common_ion_csv(type, A1.common_ion())
		with pytest.raises(TypeError):
			A1.write_ion_areas_csv(type)
	
	for type in [test_float, test_int, test_dict, test_list_strs, test_string]:
		with pytest.raises(TypeError):
			A1.write_common_ion_csv(outputdir / 'alignent_ion_area.csv', type)


def test_write_csv(A1, outputdir):
	A1.write_csv(outputdir/'alignment_rt.csv', outputdir/'alignment_area.csv')
	
	# Read alignment_rt.csv and alignment_area.csv and check values
	assert (outputdir / "alignment_rt.csv").exists()
	assert (outputdir / "alignment_area.csv").exists()
	
	rt_csv = list(csv.reader((outputdir / "alignment_rt.csv").open()))
	area_csv = list(csv.reader((outputdir / "alignment_area.csv").open()))
	
	assert rt_csv[0][0:2] == area_csv[0][0:2] == ["UID", "RTavg"]
	assert rt_csv[0][2:] == area_csv[0][2:] == A1.expr_code
	
	for peak_idx in range(len(A1.peakpos[0])):  # loop through peak lists (rows)
		
		new_peak_list = []
		
		for align_idx in range(len(A1.peakpos)):
			peak = A1.peakpos[align_idx][peak_idx]
			
			if peak is not None:
				
				if peak.rt is None or numpy.isnan(peak.rt):
					assert rt_csv[peak_idx + 1][align_idx + 2] == "NA"
				else:
					assert rt_csv[peak_idx + 1][align_idx + 2] == f"{peak.rt / 60:.3f}"
				
				if peak.area is None or numpy.isnan(peak.area):
					assert area_csv[peak_idx + 1][align_idx + 2] == "NA"
				else:
					assert area_csv[peak_idx + 1][align_idx + 2] == f"{peak.area:.0f}"
				
				new_peak_list.append(peak)
		
		compo_peak = composite_peak(new_peak_list)
		
		assert rt_csv[peak_idx + 1][0] == area_csv[peak_idx + 1][0] == compo_peak.UID
		
		assert rt_csv[peak_idx + 1][1] == area_csv[peak_idx + 1][1] == f"{float(compo_peak.rt / 60):.3f}"
	
	A1.write_csv(outputdir / 'alignment_rt_seconds.csv', outputdir / 'alignment_area_seconds.csv', minutes=False)
	
	# Read alignment_rt_seconds.csv and alignment_area_seconds.csv and check values
	assert (outputdir / "alignment_rt_seconds.csv").exists()
	assert (outputdir / "alignment_area_seconds.csv").exists()
	
	rt_csv = list(csv.reader((outputdir / "alignment_rt_seconds.csv").open()))
	area_csv = list(csv.reader((outputdir / "alignment_area_seconds.csv").open()))
	
	assert rt_csv[0][0:2] == area_csv[0][0:2] == ["UID", "RTavg"]
	assert rt_csv[0][2:] == area_csv[0][2:] == A1.expr_code
	
	for peak_idx in range(len(A1.peakpos[0])):  # loop through peak lists (rows)
		
		new_peak_list = []
		
		for align_idx in range(len(A1.peakpos)):
			peak = A1.peakpos[align_idx][peak_idx]
			
			if peak is not None:
				
				if peak.rt is None or numpy.isnan(peak.rt):
					assert rt_csv[peak_idx + 1][align_idx + 2] == "NA"
				else:
					assert rt_csv[peak_idx + 1][align_idx + 2] == f"{peak.rt:.3f}"
				
				if peak.area is None or numpy.isnan(peak.area):
					assert area_csv[peak_idx + 1][align_idx + 2] == "NA"
				else:
					assert area_csv[peak_idx + 1][align_idx + 2] == f"{peak.area:.0f}"
				
				new_peak_list.append(peak)
		
		compo_peak = composite_peak(new_peak_list)
		
		assert rt_csv[peak_idx + 1][0] == area_csv[peak_idx + 1][0] == compo_peak.UID
		
		assert rt_csv[peak_idx + 1][1] == area_csv[peak_idx + 1][1] == f"{float(compo_peak.rt):.3f}"


def test_write_ion_areas_csv(A1, outputdir):
	A1.write_ion_areas_csv(outputdir/'alignment_ion_areas.csv')
	A1.write_ion_areas_csv(outputdir/'alignment_ion_areas_seconds.csv', minutes=False)
	
	# Read alignment_ion_areas.csv and check values
	assert (outputdir / "alignment_ion_areas.csv").exists()
	
	ion_csv = list(csv.reader((outputdir / "alignment_ion_areas.csv").open(), delimiter='|'))
	seconds_ion_csv = list(csv.reader((outputdir / "alignment_ion_areas_seconds.csv").open(), delimiter='|'))
	
	assert ion_csv[0][0:2] == seconds_ion_csv[0][0:2] == ["UID", "RTavg"]
	assert ion_csv[0][2:] == seconds_ion_csv[0][2:] == A1.expr_code
	
	for peak_idx in range(len(A1.peakpos[0])):  # loop through peak lists (rows)
		
		new_peak_list = []
		
		for align_idx in range(len(A1.peakpos)):
			peak = A1.peakpos[align_idx][peak_idx]
			
			if peak is not None:
				
				ia = peak.ion_areas
				ia.update((mass, math.floor(intensity)) for mass, intensity in ia.items())
				sorted_ia = sorted(ia.items(), key=operator.itemgetter(1), reverse=True)
				
				assert ion_csv[peak_idx + 1][align_idx + 2] == str(sorted_ia)
				assert seconds_ion_csv[peak_idx + 1][align_idx + 2] == str(sorted_ia)
				
				new_peak_list.append(peak)
				
		compo_peak = composite_peak(new_peak_list)
		
		assert ion_csv[peak_idx + 1][0] == seconds_ion_csv[peak_idx + 1][0] == compo_peak.UID
		
		assert ion_csv[peak_idx + 1][1] == f"{float(compo_peak.rt / 60):.3f}"
		assert seconds_ion_csv[peak_idx + 1][1] == f"{float(compo_peak.rt):.3f}"


def test_write_common_ion_csv(A1, outputdir):
	common_ion = A1.common_ion()
	assert isinstance(common_ion, list)
	assert isinstance(common_ion[0], int)
	assert common_ion[0] == 77
	
	A1.write_common_ion_csv(outputdir/'alignment_common_ion.csv', A1.common_ion())
	# TODO: read the csv and check values
	A1.write_common_ion_csv(outputdir/'alignment_common_ion_seconds.csv', A1.common_ion(), minutes=False)
	# TODO: read the csv and check values
	
	
def test_align_2_alignments(A1, datadir, outputdir):
	expr_list = []
	
	for jcamp_file in geco_codes:
		im = build_intensity_matrix_i(JCAMP_reader(datadir/f"{jcamp_file}.JDX"))
		
		# Intensity matrix size (scans, masses)
		n_scan, n_mz = im.size
		
		# noise filter and baseline correct
		for ii in range(n_mz):
			ic = im.get_ic_at_index(ii)
			ic_smooth = savitzky_golay(ic)
			ic_bc = tophat(ic_smooth, struct="1.5m")
			im.set_ic_at_index(ii, ic_bc)
		
		peak_list = BillerBiemann(im, points=9, scans=2)
		apl = rel_threshold(peak_list, 2)
		new_peak_list = num_ions_threshold(apl, 3, 3000)
		
		# ignore TMS ions and set mass range
		for peak in new_peak_list:
			peak.crop_mass(50, 400)
			peak.null_mass(73)
			peak.null_mass(147)
			
			# find area
			area = peak_sum_area(im, peak)
			peak.area = area
			area_dict = peak_top_ion_areas(im, peak)
			peak.ion_areas = area_dict
		
		expr = Experiment(jcamp_file, new_peak_list)
		
		# set time range for all experiments
		expr.sele_rt_range(["6.5m", "21m"])
		
		expr_list.append(expr)
	
	F2 = exprl2alignment(expr_list)
	T2 = PairwiseAlignment(F2, Dw, Gw)
	A2 = align_with_tree(T2, min_peaks=2)
	
	#top_ion_list = A2.common_ion()
	#A2.write_common_ion_csv(outputdir/'area1.csv', top_ion_list)
	
	# between replicates alignment parameters
	Db = 10.0 # rt modulation
	Gb = 0.30 # gap penalty
	
	print('Aligning input {1,2}')
	T9 = PairwiseAlignment([A1,A2], Db, Gb)
	A9 = align_with_tree(T9)
	
	A9.write_csv(outputdir/'rt.csv', outputdir/'area.csv')
	
	aligned_peaks = A9.aligned_peaks()
	store_peaks(aligned_peaks, outputdir/'peaks.bin')
	
	top_ion_list = A9.common_ion()
	A9.write_common_ion_csv(outputdir/'area.csv', top_ion_list)


#def test_alignment_compare():
	#todo
	
#def test_dp()
	#todo

