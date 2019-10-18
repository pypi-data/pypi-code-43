import os
import logging
import warnings

from kadmos.graph.mixin_vistoms import vistoms_start
from kadmos.graph import FundamentalProblemGraph, load

########################################################################################################################
#                                                 Introduction                                                         #
########################################################################################################################
# This script matches the case study that is described in the KADMOS journal paper (recently submitted). Running the
# script will provide all outputs in the "case_study_results" folder and at the end of the script a VISTOMS instance is
# openend in which the different graphs are visualized and can be inspected in detail.

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
repo_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../knowledgebases', 'case_study')
pdf_dir = 'case_study_results/(X)DSM'
cmdows_dir = 'case_study_results/CMDOWS'
vistoms_dir = 'case_study_results/VISTOMS'

# Standard functions
create_dsm = lambda g, f_name, fun_order, mpg : g.create_dsm(file_name=f_name, function_order=fun_order,
                                                             include_system_vars=True, summarize_vars=True,
                                                             destination_folder=pdf_dir, abbreviate_keywords=True,
                                                             keep_tex_file=True, compile_pdf=compile_pdfs, mpg=mpg)
save_cmdows = lambda g, f_name, mpg : g.save(f_name, mpg=mpg, file_type='cmdows', destination_folder=cmdows_dir)

########################################################################################################################
#                                          SECTION 7.1. Tool repository                                                #
########################################################################################################################
# Create the RCG by reading the tool repository
R = load('database_overview.xml', file_type='cmdows', source_folder=repo_dir)
R.graph['name'] = 'Figure 15 - Repository'
fun_ord = R.get_possible_function_order('single-swap')

# Export visualization of the RCG as XDSM data flow (Figure 15)
create_dsm(R, 'Fig15-RCG', fun_ord, None)

########################################################################################################################
#                                       SECTION 7.2. Initial design point                                              #
########################################################################################################################
#  Step 1: Initiate FPG
F_MDA = FundamentalProblemGraph(R, name='Figure 16a - FPG - MDA')
mdao_definition = 'converged-MDA-GS'

# Step 2: Mark quantities of interest
an_el = '/cpacs/vehicles[@uID="AGILE_DC1_vehicleID"]/aircraft/model[@uID="agile_v13_modelID"]/analyses/'
qoi_nodes = [an_el + 'massBreakdown/mOEM/mEM/mStructure/mWingsStructure/mWingStructure/massDescription/mass',
             an_el + 'massBreakdown/fuel/massDescription/mass',
             an_el + 'massBreakdown/designMasses/mTOM/mass', an_el + 'massBreakdown/designMasses/mZFM/mass']
F_MDA.mark_as_qois(qoi_nodes)

# Step 3: Remove the functions from the FPG that are not needed and remove collisions
F_MDA.remove_unused_nodes()
F_MDA.remove_function_nodes(['INITIATOR', 'HANGAR[AGILE_AC]'] + [fn for fn in F_MDA.function_nodes if 'SCAM' in fn])
F_MDA.disconnect_problematic_variables_from('HANGAR[AGILE_AC_wing]')

# Step 4: Check the graph / make graph valid on all conditions (done by inspection)
F_MDA.make_all_variables_valid()

# Step 5: Merge functions
F_MDA = F_MDA.merge_sequential_functions('Q3D[VDE]', 'SMFA', remove_internal_couplings=True)
F_MDA = F_MDA.merge_sequential_functions('Q3D[FLC]', 'EMWET', remove_internal_couplings=True)

# Step 6: Define FPG function order
function_order = ['HANGAR[AGILE_AC_wing]', 'GACA[mainWingRefArea]', 'Q3D[VDE]-SMFA', 'Q3D[FLC]-EMWET', 'MaCal']
F_MDA.add_problem_formulation(mdao_definition, function_order)
F_MDA.add_function_problem_roles()

# Create DSM from FPG F_MDA (Figure 16a)
create_dsm(F_MDA, 'Fig16a-FPG_MDA', None, None)

# Now use the KADMOS algorithms to automatically determine the MDAO data and process graphs
MD_MDA, MP_MDA = F_MDA.impose_mdao_architecture()
MD_MDA.graph['name'] = 'Figure 16b - XDSM - MDA'

# Export XDSM visualization (Figure 16b)
create_dsm(MD_MDA, 'Fig16b-XDSM_MDA', None, MP_MDA)

# Export as CMDOWS file to be parsed in RCE (Figure 16c), Optimus or OpenMDAO
save_cmdows(MD_MDA, 'CMDOWS_MDA', MP_MDA)

########################################################################################################################
#                                     SECTION 7.3. Design space exploration                                            #
########################################################################################################################
# Step 1: Initiate FPG
F_DOE = FundamentalProblemGraph(R, name='Figure 17a - FPG - DOE')
mdao_definition = 'converged-DOE-J'

# Step 2: Use same QOIs and add the design variables
F_DOE.mark_as_qois(qoi_nodes, remove_unused_outputs=True)
sc_el = '/cpacs/toolspecific/sCAM/'
des_vars = [[sc_el + 'wing_length_morph/required_length', 14.0, 16.3, 20.0],
            [sc_el+'wing_root_chord_morph/required_root_chord',5.0,6.4,8.0],
            [sc_el+'wing_sweep_morph/required_sweep1',20.0,33.2,40.0],
            [sc_el+'wing_sweep_morph/required_sweep2',20.0,33.2,40.0],
            [sc_el+'wing_spar_morph/required_spar_position1', 0.05, 0.15, 0.40],
            [sc_el+'wing_spar_morph/required_spar_position2', 0.6, 0.7, 0.8],
            ['/cpacs/toolspecific/q3D/VDE/frictionCoefficient', 0.75, 0.8, 1.00],
            [sc_el+'wing_taper_morph/required_taper1',0.30,0.43,0.60],
            [sc_el+'wing_taper_morph/required_taper2',0.10,0.16,0.30],
            [sc_el + 'wing_dihedral_morph/required_wing_dihedral', 3.0, 6.0, 6.0]]
F_DOE.mark_as_design_variables([ds_vr[0] for ds_vr in des_vars], lower_bounds=[ds_vr[1] for ds_vr in des_vars],
                               nominal_values=[ds_vr[2] for ds_vr in des_vars],
                               upper_bounds=[ds_vr[3] for ds_vr in des_vars])

# Step 3: Remove the unnecessary functions and collisions from the FPG
F_DOE.remove_unused_nodes()
F_DOE.remove_function_nodes(['INITIATOR', 'HANGAR[AGILE_AC]'])

# Step 4: Check the graph / make graph valid on all conditions (done by inspection)

# Step 5: Merge functions
F_DOE = F_DOE.merge_function_modes('SCAM[wing_length_morph]', 'SCAM[wing_taper_morph]', 'SCAM[wing_root_chord_morph]',
                                   'SCAM[wing_sweep_morph]', 'SCAM[wing_dihedral_morph]', 'SCAM[wing_spar_morph]',
                                   new_label='SCAM')
F_DOE = F_DOE.merge_sequential_functions('Q3D[VDE]', 'SMFA', remove_internal_couplings=True)
F_DOE = F_DOE.merge_sequential_functions('Q3D[FLC]', 'EMWET', remove_internal_couplings=True)

# Find and fix problematic nodes w.r.t. HANGAR tool after the merger of SCAM
F_DOE.disconnect_problematic_variables_from('HANGAR[AGILE_AC_wing]', ignore_list=F_DOE.get_sources('SCAM'))

# Step 6: Define FPG function order
function_order = ['HANGAR[AGILE_AC_wing]', 'SCAM', 'GACA[mainWingRefArea]', 'Q3D[VDE]-SMFA', 'Q3D[FLC]-EMWET', 'MaCal']
F_DOE.add_problem_formulation(mdao_definition, function_order,
                              doe_settings={'method':'Latin hypercube design', 'seed':6, 'runs':5})
F_DOE.make_all_variables_valid()
F_DOE.add_function_problem_roles()

# Create DSM from FPG F_DOE (Figure 17a)
create_dsm(F_DOE, 'Fig17a-FPG_DOE', None, None)

# Now use the KADMOS algorithms to automatically determine the MDG and MPG
MD_DOE, MP_DOE = F_DOE.impose_mdao_architecture()
MD_DOE.graph['name'] = 'Figure 17b - XDSM - DOE'

# Export XDSM visualization (Figure 17b)
create_dsm(MD_DOE, 'Fig17b-XDSM_DOE', None, MP_DOE)

# Export as CMDOWS file to be parsed in RCE, Optimus or OpenMDAO
save_cmdows(MD_DOE, 'CMDOWS_DOE', MP_DOE)

########################################################################################################################
#                                       SECTION 7.4. Optimization (IDF)                                                #
########################################################################################################################
#  Step 1: Initiate FPG
F_MDO = FundamentalProblemGraph(R, name='Figure 17a - FPG - MDO IDF')
mdao_definition = 'IDF'

# Step 2: Use same QOIs and design variables (except the dihedral and taper ratios) and add constraints and objective
F_MDO.mark_as_qois(qoi_nodes)
F_MDO.mark_as_design_variables([ds_vr[0] for ds_vr in des_vars[:-3]],
                               lower_bounds=[ds_vr[1] for ds_vr in des_vars[:-3]],
                               nominal_values=[ds_vr[2] for ds_vr in des_vars[:-3]],
                               upper_bounds=[ds_vr[3] for ds_vr in des_vars[:-3]])
F_MDO.mark_as_objective('/cpacs/mdodata/objectives/mtow/normalized_mtow')
F_MDO.mark_as_constraints(['/cpacs/mdodata/constraints/wingLoading/latestValue',
                         '/cpacs/mdodata/constraints/fuelTankVolume/latestValue'],
                         '<=', reference_values=0.0, remove_unused_outputs=True)

# Step 3: Remove the functions from the FPG that are not needed and remove collisions
F_MDO.remove_unused_nodes()
F_MDO.remove_function_nodes('INITIATOR', 'HANGAR[AGILE_AC]', 'SCAM[wing_taper_morph]', 'SCAM[wing_dihedral_morph]')

# Step 4: Check the graph / make graph valid on all conditions (done by inspection)

# Step 5: Merge functions
F_MDO = F_MDO.merge_parallel_functions('CNSTRNT_fuelTankVolume', 'CNSTRNT_wingLoading', new_label='CNSTRNT[WL,FTV]')
F_MDO = F_MDO.merge_sequential_functions('Q3D[VDE]', 'SMFA', remove_internal_couplings=True)
F_MDO = F_MDO.merge_sequential_functions('Q3D[FLC]', 'EMWET', remove_internal_couplings=True)
# We make an FPG specifically for IDF for reasons of visualization
F_IDF = F_MDO.deepcopy()
F_IDF = F_IDF.merge_function_modes('SCAM[wing_length_morph]', 'SCAM[wing_root_chord_morph]',
                                   'SCAM[wing_sweep_morph]', 'SCAM[wing_spar_morph]', new_label='SCAM')
F_IDF = F_IDF.merge_function_modes('GACA[mainWingFuelTankVol]', 'GACA[mainWingRefArea]', new_label='GACA')
F_IDF.disconnect_problematic_variables_from('HANGAR[AGILE_AC_wing]', ignore_list=F_IDF.get_sources('SCAM'))

# Step 6: Define FPG function order
function_order = ['HANGAR[AGILE_AC_wing]', 'SCAM', 'GACA', 'Q3D[VDE]-SMFA', 'Q3D[FLC]-EMWET', 'MaCal',
                  'OBJ', 'CNSTRNT[WL,FTV]']
F_IDF.add_problem_formulation(mdao_definition, function_order)
F_IDF.make_all_variables_valid()
F_IDF.add_function_problem_roles()

# Create DSM from FPG F_IDF (Figure 17a)
create_dsm(F_IDF, 'Fig17a-FPG_IDF', None, None)

# Now use the KADMOS algorithms to automatically determine the MDG and MPG
MD_IDF, MP_IDF = F_IDF.impose_mdao_architecture()
MD_IDF.graph['name'] = 'Figure 18 - XDSM - IDF'

# Export XDSM visualization (Figure 18c)
create_dsm(MD_IDF, 'Fig18-XDSM_IDF', None, MP_IDF)

# Export as CMDOWS file to be parsed in RCE, Optimus or OpenMDAO
save_cmdows(MD_IDF, 'CMDOWS_IDF', MP_IDF)

########################################################################################################################
#                                   SECTION 7.4. Optimization (BLISS-2000)                                             #
########################################################################################################################
#  D.1: Initiate FPG
F_B2k = F_MDO.deepcopy()
F_B2k.graph['name'] = 'Figure 17a - FPG - MDO BLISS-2000'
mdao_definition = 'BLISS-2000'

# Step 5: Merge functions
F_B2k = F_B2k.merge_function_modes('SCAM[wing_length_morph]', 'SCAM[wing_root_chord_morph]',
                                   'SCAM[wing_sweep_morph]', new_label='SCAM')
F_B2k.disconnect_problematic_variables_from('HANGAR[AGILE_AC_wing]', ignore_list=F_B2k.get_sources('SCAM'))

# Step 6: Define FPG function order
function_order = ['HANGAR[AGILE_AC_wing]', 'SCAM', 'GACA[mainWingRefArea]', 'SCAM[wing_spar_morph]',
                  'GACA[mainWingFuelTankVol]', 'Q3D[VDE]-SMFA', 'Q3D[FLC]-EMWET', 'MaCal', 'OBJ', 'CNSTRNT[WL,FTV]']
F_B2k.add_problem_formulation(mdao_definition, function_order,
                              doe_settings={'method': 'Latin hypercube design', 'seed': 5, 'levels': 4})
F_B2k.graph['problem_formulation']['coupled_functions_groups'] = [['Q3D[VDE]-SMFA'], ['Q3D[FLC]-EMWET', 'MaCal']]
F_B2k.make_all_variables_valid()

# Adjust sources of SCAM[wing_spar_morph] to be taken from HANGAR
sources = list(set(F_B2k.get_sources('SCAM[wing_spar_morph]')).intersection(F_B2k.get_targets('SCAM')))
for source in sources:
    F_B2k.remove_edge(source, 'SCAM[wing_spar_morph]')
    F_B2k.add_edge(F_B2k.nodes[source]['related_to_schema_node'], 'SCAM[wing_spar_morph]')

F_B2k.add_function_problem_roles()

# Create DSM from FPG F_D3 (Figure 17a)
create_dsm(F_B2k, 'Fig17a-FPG_B2k', None, None)

# Now use the KADMOS algorithms to automatically determine the MDG and MPG
MD_B2k, MP_B2k = F_B2k.impose_mdao_architecture()
MD_B2k.graph['name'] = 'Figure 19 - XDSM - BLISS-2000'

# Export XDSM visualization (Figure 19)
create_dsm(MD_B2k, 'Fig19-XDSM_B2k', None, MP_B2k)
# Export as CMDOWS file to be parsed in RCE, Optimus or OpenMDAO
save_cmdows(MD_B2k, 'CMDOWS_B2k', MP_B2k)

########################################################################################################################
#                                 Bonus: dynamic visualization with VISTOMS                                            #
########################################################################################################################
# Below a VISTOMS package is initiated which contains all of the graphs created in this script
# VISTOMS can be used to inspect (and also manipulate) the graphs in a browser.
all_graphs = [R, F_MDA, (MD_MDA, MP_MDA), F_DOE, (MD_DOE, MP_DOE), F_IDF, (MD_IDF, MP_IDF), F_B2k, (MD_B2k, MP_B2k)]
vistoms_start(all_graphs, file_dir=vistoms_dir)
