#!/bin/bash

# MAGNET RESULTS - Producing FFT for every run

nuri transform \
     --start 2017-03-09-15-58 \
     --end   2017-03-10 \
     --path /Users/vincent/ASTRO/data/magnet_2017-03-09/sample1_background_noise/ \
     --station magnet --sample --unit secs --nogps \
     --discard 1 --fmin 1 --down 12 --seaborn

# TIMING TEST - Comparing GNOME and NURI results for square pulse run

nuri timing --seaborn --down 1 --sample \
     --start 2017-3-1-12 \
     --end   2017-3-1-16

nuri timing --seaborn --down 1 --sample \
     --start 2017-3-1-14-1-1 \
     --end   2017-3-1-14-1-2

# TIMING TEST - Comparing GNOME and NURI results for PPS run

nuri timing --seaborn --down 1 --sample --tmode 3 \
     --start 2017-3-16 \
     --end   2017-3-19

nuri timing --seaborn --down 1 --sample \
     --start 2017-3-16 \
     --end   2017-3-19

nuri timing --seaborn --down 1 --sample \
     --start 2017-3-17-23-4-50 \
     --end   2017-3-17-23-5-10

nuri timing --seaborn --down 1 --sample \
     --start 2017-3-17-23-29-5-900000 \
     --end   2017-3-17-23-29-6-300000

nuri timing --seaborn --down 1 --sample \
     --start 2017-3-17-22-54-39-900000 \
     --end   2017-3-17-22-54-40-300000

# Produce wavelet spectrogram on full day from station 4

nuri wavelet \
     --station station4 --start 2016-03-20 --end 2016-03-21 \
     --path /Volumes/NURI-GNOME/NURIDrive/NURI-station-04/
