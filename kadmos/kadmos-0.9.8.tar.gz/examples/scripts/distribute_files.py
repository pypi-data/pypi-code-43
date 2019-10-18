# Small file to copy the KADMOS CMDOWS and XDSM files to the different packages and folders
from __future__ import absolute_import, division, print_function

import os
import shutil

from os import listdir

from examples.scripts.sellar_problem import run_kadmos as run_kadmos_sellar

def copy_folder_content(src_folder, dst_folder, filename_filter=None):
    # Empty the destination folder
    files = [os.path.join(dst_folder, f) for f in listdir(dst_folder) if os.path.isfile(os.path.join(dst_folder, f))]
    for file in files:
        os.remove(file)
    # Copy files to the folder
    copy_files = [os.path.join(src_folder, f) for f in listdir(src_folder) if os.path.isfile(os.path.join(src_folder, f))]
    for copy_file in copy_files:
        copy = True
        if filename_filter:
            if not filename_filter in os.path.basename(copy_file):
                copy = False
        if copy:
            shutil.copy(copy_file, os.path.join(dst_folder, os.path.basename(copy_file)))

""" Sellar math """
mdao_definitions = ['unconverged-MDA-J',    # 0
                    'unconverged-MDA-GS',   # 1
                    'converged-DOE-GS',     # 2
                    'converged-DOE-J',      # 3
                    'converged-MDA-J',      # 4
                    'converged-MDA-GS',     # 5
                    'MDF-GS',               # 6
                    'MDF-J',                # 7
                    'IDF',                  # 8
                    'CO']                   # 9
kadmos_scripts_folder = os.path.join(os.path.dirname(__file__))
run_kadmos_sellar('all', 'math')
# Send CMDOWS files to OpenLEGO package tests
sellar_math_cmdows_folder = os.path.join(kadmos_scripts_folder, 'sellar_problem_math', 'CMDOWS')
sellar_math_xdsm_folder = os.path.join(kadmos_scripts_folder, 'sellar_problem_math', '(X)DSM')
dst_folder = '/Users/imcovangent/Documents/PhD/Software/OpenLEGO/openlego/test_suite/test_examples/sellar_math/cmdows_files'
for mdao_def in mdao_definitions:
    src_file = os.path.join(sellar_math_cmdows_folder, 'Mdao_{}.xml'.format(mdao_def))
    dst_file = os.path.join(dst_folder, 'Mdao_{}.xml'.format(mdao_def))
    if not os.path.isfile(src_file):
        raise AssertionError('Could not find file {}'.format(src_file))
    shutil.copy(src_file, dst_file)

# Send CMDOWS files to CMDOWS package examples
src_folder = sellar_math_cmdows_folder
dst_folder = '/Users/imcovangent/Documents/PhD/Software/CMDOWS/examples/sellar_problem/CMDOWS'
copy_folder_content(src_folder, dst_folder)

# Send XDSM files to CMDOWS package examples
src_folder = sellar_math_xdsm_folder
dst_folder = '/Users/imcovangent/Documents/PhD/Software/CMDOWS/examples/sellar_problem/(X)DSM'
copy_folder_content(src_folder, dst_folder, filename_filter='.pdf')

# Send CMDOWS files to VISTOMS package examples
files_to_copy = ['RCG.xml', 'FPG_converged-MDA-GS.xml', 'FPG_converged-DOE-GS.xml',
                 'FPG_MDF-GS.xml', 'Mdao_MDF-GS.xml', 'Mdao_MDF-J.xml',
                 'Mdao_IDF.xml', 'Mdao_CO.xml']
dst_folder = '/Users/imcovangent/Documents/PhD/Software/KADMOS/kadmos/vistoms/downloads'
for file_to_copy in files_to_copy:
    src_file = os.path.join(sellar_math_cmdows_folder, file_to_copy)
    dst_file = os.path.join(dst_folder, 'sellar_{}'.format(file_to_copy))
    shutil.copy(src_file, dst_file)

""" Sellar competences """
run_kadmos_sellar('all', 'math')
# Send CMDOWS files to OpenLEGO package tests
kadmos_scripts_folder = os.path.join(os.path.dirname(__file__))
sellar_comps_cmdows_folder = os.path.join(kadmos_scripts_folder, 'sellar_problem_math', 'CMDOWS')
dst_folder = '/Users/imcovangent/Documents/PhD/Software/OpenLEGO/openlego/test_suite/test_examples/sellar_competences/cmdows_files'
for mdao_def in mdao_definitions:
    src_file = os.path.join(sellar_comps_cmdows_folder, 'Mdao_{}.xml'.format(mdao_def))
    dst_file = os.path.join(dst_folder, 'Mdao_{}.xml'.format(mdao_def))
    if not os.path.isfile(src_file):
        raise AssertionError('Could not find file {}'.format(src_file))
    shutil.copy(src_file, dst_file)