import os
import logging
import warnings

from kadmos.graph import FundamentalProblemGraph, load

########################################################################################################################
#                                                 Introduction                                                         #
########################################################################################################################
# This script matches the Sellar example case that is described in the KADMOS journal paper (recently submitted).
# Running the script will provide all outputs in the "sellar_problem_results" folder.

# Installation requirements:
# - To run this script the Python package KADMOS needs to be installed. This can done with "pip install kadmos==0.9.7"
# - The automatic creation of PDFs requires the installation of LaTeX / MikTex on the system. To avoid issue with this,
#   compile_pdfs is automatically set to False if the pdflatex command cannot be found.

# Logging settings
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# Check version of KADMOS
from kadmos import __version__ as kadmos_version
if not kadmos_version == '0.9.7':
    warnings.warn('\nThis script has been written and tested on KADMOS version 0.9.7.\nYou are '
                  'currently running on KADMOS version {}.'.format(kadmos_version))

# Check PDF compilation
import distutils.spawn
pdflatex_path = distutils.spawn.find_executable('pdflatex')
if pdflatex_path:
    compile_pdfs = True
else:
    warnings.warn('Could not find command pdflatex, hence no PDFs will be compiled in the '
                  'create_dsm method.')
    compile_pdfs = False

# Directory settings
repo_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../knowledgebases', 'sellar')
pdf_dir = 'sellar_problem_results/(X)DSM'
cmdows_dir = 'sellar_problem_results/CMDOWS'

# Standard functions
create_dsm = lambda g, f_name, fun_order, mpg : g.create_dsm(file_name=f_name, function_order=fun_order,
                                                             include_system_vars=True, destination_folder=pdf_dir,
                                                             keep_tex_file=True, compile_pdf=compile_pdfs, mpg=mpg)

########################################################################################################################
#                                          SECTION 6.1. Tool repository                                                #
########################################################################################################################
# Create the RCG by reading the tool repository
rcg = load('database_overview.xml', file_type='cmdows', source_folder=repo_dir)
rcg.graph['name'] = 'Repository - Figure 9'
rcg.graph['description'] = 'Repository graph of tools where a subset can be used to solve the Sellar problem'

# Create a DSM visualization of the RCG (Figure 9)
create_dsm(rcg, 'Fig9-RCG', rcg.get_possible_function_order('single-swap'), None)

########################################################################################################################
#                                     SECTION 6.2. Fundamental problem graph                                           #
########################################################################################################################
# A initial fundamental problem graph is created based on the RCG
fpg = rcg.deepcopy_as(FundamentalProblemGraph)

# Step 1: Anticipate MDAO architecture -> MDO
mdao_definition = 'MDF-GS'  # change to 'CO' for Collaborative Optimization case

# Step 2: Mark problem roles of variables based on the type of MDAO architecture
fpg.mark_as_objective('/dataSchema/analyses/f')
fpg.mark_as_constraints(['/dataSchema/analyses/g1', '/dataSchema/analyses/g2'], '>=', 0.0)
fpg.remove_edge('B', '/dataSchema/variables/z1')
fpg.remove_edge('B', '/dataSchema/variables/z2')
fpg.mark_as_design_variables(['/dataSchema/variables/z1', '/dataSchema/variables/z2',
                                      '/dataSchema/variables/x0'], lower_bounds=[-10, 0.0, 0.0], upper_bounds=10,
                                      nominal_values=0.0)
fpg.mark_as_qoi('/dataSchema/analyses/y2')
# Create Figure 10a
create_dsm(fpg, 'Fig10a-FPG', fpg.get_possible_function_order('single-swap'), None)

# Step 3: Solve problematic nodes
fpg.remove_function_nodes('E')
fpg.graph['problem_formulation'] = {'function_order': ['A', 'B', 'C', 'H', 'D[1]', 'D[2]', 'F', 'G[1,2]']}
fpg.split_variables('/dataSchema/settings/b')

# Step 4: Check graph validity (done by inspection)
assert not fpg.find_all_nodes(subcategory='all problematic variables')
assert not fpg.find_all_nodes(subcategory='all problematic functions')
# Create Figure 10b
create_dsm(fpg, 'Fig10b-FPG', fpg.get_possible_function_order('single-swap'), None)

# Step 5
fpg = fpg.merge_sequential_functions('A', 'B', 'C', new_label='ABC', remove_internal_couplings=True)
if mdao_definition != 'CO':
    fpg = fpg.merge_parallel_functions('G[1]', 'G[2]', new_label='G[1,2]')
# Create Figure 10c
create_dsm(fpg, 'Fig10c-FPG', fpg.get_possible_function_order('single-swap'), None)

# Step 6
fpg.add_function_problem_roles()
# Create Figure 10d
create_dsm(fpg, 'Fig10d-FPG', fpg.get_possible_function_order('single-swap'), None)

# Step 7
function_order = fpg.get_possible_function_order('single-swap')
fpg.add_problem_formulation(mdao_definition, function_order)

# Step 8
if mdao_definition == 'CO':
    fpg.graph['problem_formulation']['coupled_functions_groups'] = [['D[1]'], ['D[2]']]

# Add some metadata
fpg.graph['name'] = 'FPG - ' + mdao_definition
fpg.graph['description'] = 'Fundamental problem graph for solving the Sellar problem using the strategy: ' \
                           + mdao_definition + '.'

########################################################################################################################
#                                SECTION 6.3.-6.5 MDAO data / process graphs and XDSMs                                 #
########################################################################################################################
# Get MDAO graphs
mdg = fpg.get_mdg(name='mdg Sellar problem')
mpg = mdg.get_mpg(name='mpg Sellar problem')
mdg.graph['name'] = 'XDSM - ' + mdao_definition
mdg.graph['description'] = 'Solution strategy to solve the Sellar problem using the strategy: ' + str(mdao_definition)

# Create an XDSM visualization (Figures 11c and 12)
create_dsm(mdg, 'Fig11c-XDSM-MDF' if mdao_definition == 'MDF-GS' else 'Fig12-XDSM-CO',
           None, mpg)

# Save CMDOWS file
mdg.save(file_name='Mdao_'+mdao_definition, file_type='cmdows',
         destination_folder=cmdows_dir,
         mpg=mpg,
         pretty_print=True)

logging.info('Done!')
