# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['peakipy', 'peakipy.commandline']

package_data = \
{'': ['*'],
 'peakipy.commandline': ['edit_fits_app/*', 'edit_fits_app/templates/*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'bokeh>=1.0.4,<2.0.0',
 'colorama>=0.4.1,<0.5.0',
 'docopt>=0.6.2,<0.7.0',
 'lmfit>=0.9.12,<0.10.0',
 'matplotlib>=3.0,<4.0',
 'nmrglue>=0.6.0,<0.7.0',
 'numba>=0.44.1,<0.45.0',
 'numdifftools>=0.9.39,<0.10.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.24.0,<0.25.0',
 'schema>=0.7.0,<0.8.0',
 'scikit-image>=0.14.2,<0.15.0',
 'scipy>=1.2,<2.0',
 'tabulate>=0.8.3,<0.9.0']

entry_points = \
{'console_scripts': ['peakipy = peakipy.__main__:main']}

setup_kwargs = {
    'name': 'peakipy',
    'version': '0.1.26',
    'description': 'Deconvolute overlapping NMR peaks',
    'long_description': '# Peakipy - NMR peak integration/deconvolution using python\n\n[![Build Status](https://travis-ci.com/j-brady/peakipy.svg?token=wh1qimLa9ucxKasjXFoj&branch=master)](https://travis-ci.com/j-brady/peakipy)\n\n[peakipy documentation](https://j-brady.github.io/peakipy)\n\n## Description\n\nSimple deconvolution of NMR peaks for extraction of intensities. Provided an NMRPipe format spectrum (2D or Pseudo 3D)\n and a peak list (NMRPipe, Sparky or Analysis2), overlapped peaks are automatically/interactively clustered and groups\n of overlapped peaks are fitted together using Gaussian, Lorentzian or Pseudo-Voigt (Gaussian + Lorentzian) lineshape.\n\n## Installation\n\nThe easiest way to install peakipy is with poetry...\n\n```bash\ncd peakipy; poetry install\n```\n\nIf you don\'t have poetry you can install it with the following command\n\n```bash\ncurl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python\n```\nOtherwise refer to the [poetry documentation](https://poetry.eustace.io/docs/) for more details\n\nYou can also install peakipy with `setup.py`. You will need python3.6 or greater installed.\n\n```bash\ncd peakipy; python setup.py install\n```\n\nAt this point the package should be installed and the main scripts (`peakipy read`, `peakipy edit`, `peakipy fit` and `peakipy check`)\nshould have been added to your path.\n\n## Inputs\n\n1. Peak list (NMRPipe, Analysis v2.4, Sparky) \n2. NMRPipe frequency domain dataset (2D or Pseudo 3D)\n\nThere are four main commands:\n\n1. `peakipy read` converts your peak list and selects clusters of peaks.\n2. `peakipy edit` is used to check and adjust fit parameters interactively (i.e clusters and mask radii) if initial clustering is not satisfactory.\n3. `peakipy fit` fits clusters of peaks.\n4. `peakipy check` is used to check individual fits or groups of fits and make plots.\n\nYou can use the `-h` or `--help` flags for instructions on how to run the programs (e.g. peakipy read -h)\n\n\n## Outputs\n\n1. Pandas DataFrame containing fitted intensities/linewidths/centers etc.\n\n```bash\n,fit_prefix,assignment,amp,amp_err,center_x,center_y,sigma_x,sigma_y,fraction,clustid,plane,x_radius,y_radius,x_radius_ppm,y_radius_ppm,lineshape,fwhm_x,fwhm_y,center_x_ppm,center_y_ppm,sigma_x_ppm,sigma_y_ppm,fwhm_x_ppm,fwhm_y_ppm,fwhm_x_hz,fwhm_y_hz\n0,_None_,None,291803398.52980924,5502183.185104156,158.44747896487527,9.264911100915297,1.1610674220702277,1.160506074898704,0.0,1,0,4.773,3.734,0.035,0.35,G,2.3221348441404555,2.321012149797408,9.336283145411077,129.6698850201278,0.008514304888101518,0.10878688239041588,0.017028609776203036,0.21757376478083176,13.628064792721176,17.645884354478063\n1,_None_,None,197443035.67109975,3671708.463467884,158.44747896487527,9.264911100915297,1.1610674220702277,1.160506074898704,0.0,1,1,4.773,3.734,0.035,0.35,G,2.3221348441404555,2.321012149797408,9.336283145411077,129.6698850201278,0.008514304888101518,0.10878688239041588,0.017028609776203036,0.21757376478083176,13.628064792721176,17.645884354478063\netc...\n```\n\n2. If `--plot=<path>` option selected the first plane of each fit will be plotted in <path> with the files named according to the cluster ID (clustid) of the fit. Adding `--show` option calls `plt.show()` on each fit so you can see what it looks like. However, using `peakipy check` should be preferable since plotting the fits during fitting\nslows down the process a lot.\n\n3. To plot fits for all planes or interactively check them you can run `peakipy check`\n\n```bash\npeakipy check fits.csv test.ft2 --dims=0,1,2 --clusters=1,10,20 --show --outname=plot.pdf\n```\nWill plot clusters 1,10 and 20 showing each plane in an interactive matplotlib window and save the plots to a multipage pdf called plot.pdf. Calling `peakipy check`\nwith the `--first` flag results in only the first plane of each fit being plotted.\n\nRun `peakipy check -h` for more options.\n\nYou can explore the output data conveniently with `pandas`.\n\n```python\nIn [1]: import pandas as pd\n\nIn [2]: import matplotlib.pyplot as plt\n\nIn [3]: data = pd.read_csv("fits.csv")\n\nIn [4]: groups = data.groupby("assignment")\n\nIn [5]: for ind, group in groups:\n   ...:     plt.errorbar(group.vclist,group.amp,yerr=group.amp_err,fmt="o",label=group.assignment.iloc[0])\n   ...:     plt.legend()\n   ...:     plt.show()\n```\n\n## Pseudo-Voigt model\n\n![Pseudo-Voigt](images/equations/pv.tex.png)\n\nWhere Gaussian lineshape is\n\n![G](images/equations/G.tex.png)\n\nAnd Lorentzian is\n\n![L](images/equations/L.tex.png)\n\nThe fit minimises the residuals of the functions in each dimension\n\n![PV_xy](images/equations/pv_xy.tex.png)\n\nFraction parameter is fraction of Lorentzian lineshape.\n\nThe linewidth for the G lineshape is\n\n![G_lw](images/equations/G_lw.tex.png)\n\nThe linewidth for PV and L lineshapes is\n\n![PV FWHM](images/equations/pv_lw.png)\n\n## Test data\n\nDownload from git repo. To test the program for yourself `cd` into the `test` directory . I wrote some tests for the code itself which should be run from the top directory like so `python test/test_core.py`.\n\n## Comparison with NMRPipe\n\nA sanity check... Peak intensities were fit using the nlinLS program from NMRPipe and compared with the output from peakipy for the same dataset.\n\n![NMRPipe vs peakipy](test/test_protein_L/correlation.png)\n\n## Homage to FuDA\n\nIf you would rather use FuDA then try running `peakipy read` with the `--fuda` flag to create a FuDA parameter file\n(params.fuda) and peak list (peaks.fuda).\nThis should hopefully save you some time on configuration.\n\n## Acknowledgements\n\nThanks to Jonathan Helmus for writing the wonderful `nmrglue` package.\nThe `lmfit` team for their awesome work.\n`bokeh` and `matplotlib` for beautiful plotting.\n`scikit-image`!\n\nMy colleagues, Rui Huang, Alex Conicella, Enrico Rennella, Rob Harkness and Tae Hun Kim for their extremely helpful input.\n',
    'author': 'Jacob Brady',
    'author_email': 'jacob.brady0449@gmail.com',
    'url': 'https://j-brady.github.io/peakipy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
