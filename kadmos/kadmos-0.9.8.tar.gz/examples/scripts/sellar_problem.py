# Imports
from __future__ import absolute_import, division, print_function

import distutils.spawn
import logging
import os


from kadmos.graph import RepositoryConnectivityGraph, FundamentalProblemGraph, load
from kadmos.utilities.general import get_mdao_setup, pdflatex_command_found

# Settings for logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# List of MDAO definitions that can be wrapped around the problem
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


def get_loop_items(analyze_mdao_definitions):
    if isinstance(analyze_mdao_definitions, int):
        mdao_defs_loop = [mdao_definitions[analyze_mdao_definitions]]
    elif isinstance(analyze_mdao_definitions, list):
        mdao_defs_loop = [mdao_definitions[i] for i in analyze_mdao_definitions]
    elif isinstance(analyze_mdao_definitions, str):
        if analyze_mdao_definitions == 'all':
            mdao_defs_loop = mdao_definitions
        else:
            raise ValueError(
                'String value {} is not allowed for analyze_mdao_definitions.'.format(analyze_mdao_definitions))
    else:
        raise IOError(
            'Invalid input {} provided of type {}.'.format(analyze_mdao_definitions, type(analyze_mdao_definitions)))
    return mdao_defs_loop


def get_sellar_rcg(repository_type):

    if repository_type == 'math':
        # A new repository connectivity graph is defined to describe the general problem
        rcg = RepositoryConnectivityGraph(name='Sellar problem graph')

        # A description is added to the graph
        rcg.graph['description'] = 'Repository graph of tools where a subset can be used to solve the Sellar problem'

        # All function nodes are defined
        rcg.add_fnodes('A', 'B', 'C', 'D[1]', 'D[2]', 'E', 'F', 'G[1]', 'G[2]', 'H')

        # All variable nodes are defined
        rcg.add_vnodes('/dataSchema/settings/a',
                       '/dataSchema/settings/b',
                       '/dataSchema/settings/c',
                       '/dataSchema/analyses/f',
                       '/dataSchema/analyses/g1',
                       '/dataSchema/analyses/g2',
                       '/dataSchema/variables/x0',
                       '/dataSchema/variables/x1',
                       '/dataSchema/analyses/y1',
                       '/dataSchema/analyses/y2',
                       '/dataSchema/variables/z1',
                       '/dataSchema/variables/z2')

        # The edges between the nodes are defined
        rcg.connect_variable('/dataSchema/settings/a', input_of=['A'], output_of=[])
        rcg.connect_variable('/dataSchema/settings/b', input_of=['B', 'C', 'E'], output_of=['A', 'B'])
        rcg.connect_variable('/dataSchema/settings/c', input_of=['D[1]', 'D[2]'], output_of=['C'])
        rcg.connect_variable('/dataSchema/analyses/f', output_of=['F'])
        rcg.connect_variable('/dataSchema/analyses/g1', output_of=['G[1]'])
        rcg.connect_variable('/dataSchema/analyses/g2', output_of=['G[2]'])
        rcg.connect_variable('/dataSchema/variables/x0', input_of=['H'])
        rcg.connect_variable('/dataSchema/variables/x1', input_of=['D[1]', 'F'], output_of=['H'])
        rcg.connect_variable('/dataSchema/analyses/y1',
                             input_of=['D[2]', 'F', 'G[1]'], output_of=['D[1]', 'E'])
        rcg.connect_variable('/dataSchema/analyses/y2',
                             input_of=['D[1]', 'F', 'G[2]'], output_of=['D[2]', 'E'])
        rcg.connect_variable('/dataSchema/variables/z1', input_of=['D[1]', 'D[2]', 'E'], output_of=['B'])
        rcg.connect_variable('/dataSchema/variables/z2',
                             input_of=['D[1]', 'D[2]', 'E', 'F'], output_of=['B'])

        rcg.assert_node_categories()

        # Add some (optional) equations
        rcg.add_equation_labels(rcg.function_nodes)
        rcg.add_equation('A', 'a', 'Python')
        rcg.add_equation('H', 'x0', 'Python')
        rcg.add_equation('D[1]', 'c*(z1**2. + x1 + z2 - .2*y2)', 'Python')
        rcg.add_equation('D[2]', 'c*(abs(y1)**.5 + z1 + z2)', 'Python')
        rcg.add_equation('G[1]', 'y1/3.16-1', 'Python')
        rcg.add_equation('G[2]', '1-y2/24.0', 'Python')
        rcg.add_equation('F', 'x1**2+z2+y1+exp(-y2)', 'Python')

        # Add some (optional) organization information
        rcg.add_contact('Imco van Gent', 'i.vangent@tudelft.nl', 'ivangent', company='TU Delft',
                        roles=['architect',
                               'integrator'])
        rcg.add_contact('Lukas Muller', 'l.muller@student.tudelft.nl', 'lmuller', company='TU Delft',
                        roles='architect')
    elif repository_type=='competences':
        repo_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../knowledgebases',
                                'sellar')
        rcg = load('database_overview.xml', file_type='cmdows', source_folder=repo_dir)
        rcg.name = 'Tool repository Sellar'
    else:
        raise AssertionError('Invalid input "repository_type".')
    return rcg


def run_kadmos(analyze_mdao_definitions, repository_type, folder_str='sellar_problem'):

    global mdao_definitions

    # Check and analyze inputs
    mdao_defs_loop = get_loop_items(analyze_mdao_definitions)

    # Settings for saving
    pdf_dir = os.path.join('{}_{}'.format(folder_str, repository_type), '(X)DSM')
    cmdows_dir = os.path.join('{}_{}'.format(folder_str, repository_type), 'CMDOWS')
    kdms_dir = os.path.join('{}_{}'.format(folder_str, repository_type), 'KDMS')

    compile_pdf = pdflatex_command_found()
    if not compile_pdf:
        logging.warning('Could not find command pdflatex, hence no PDFs will be compiled in the '
                        'create_dsm method.')

    logging.info('Scripting RCG...')
    rcg = get_sellar_rcg(repository_type)

    # Add some (optional) ranges
    function_order = rcg.function_nodes

    # Create a DSM visualization of the RCG
    rcg.create_dsm(file_name='RCG', function_order=function_order, include_system_vars=True,
                   destination_folder=pdf_dir, keep_tex_file=not compile_pdf, compile_pdf=compile_pdf)
    rcg.save('RCG', file_type='cmdows', destination_folder=cmdows_dir, pretty_print=True)
    rcg.save('RCG', file_type='kdms', destination_folder=kdms_dir)

    logging.info('Scripting initial FPG...')

    # A initial fundamental problem graph is created based on the rcg
    fpg_initial = rcg.deepcopy_as(FundamentalProblemGraph)
    # The dummy function nodes are removed
    fpg_initial.remove_function_nodes('E')
    fpg_initial.remove_edge('B', '/dataSchema/variables/z1')
    fpg_initial.remove_edge('B', '/dataSchema/variables/z2')
    fpg_initial.split_variables('/dataSchema/settings/b', function_order=['A', 'B', 'C'])
    fpg_initial = fpg_initial.merge_sequential_functions('A', 'B', 'C', new_label='ABC',
                                                         remove_internal_couplings=True)
    fpg_initial.add_equation_labels(['ABC'])
    fpg_initial.add_equation('ABC', 'a', 'Python')

    # TODO: Build and handle FPG such that it can be created outside the loop of architectures
    for mdao_definition in mdao_defs_loop:

        logging.info('Scripting ' + str(mdao_definition) + '...')

        # Determine the three main settings: architecture, convergence type and unconverged coupling setting
        mdao_architecture, convergence_type, allow_unconverged_couplings = get_mdao_setup(mdao_definition)

        # Reset FPG
        fpg = fpg_initial.deepcopy()
        fpg.graph['name'] = 'FPG - ' + mdao_definition
        fpg.graph['description'] = 'Fundamental problem graph for solving the Sellar problem using the strategy: ' \
                                   + mdao_definition + '.'

        # Define settings of the problem formulation
        fpg.graph['problem_formulation'] = problem_formulation = dict()
        problem_formulation['function_order'] = ['ABC', 'H', 'D[1]', 'D[2]', 'F', 'G[1]', 'G[2]']
        problem_formulation['mdao_architecture'] = mdao_architecture
        problem_formulation['convergence_type'] = convergence_type
        problem_formulation['allow_unconverged_couplings'] = allow_unconverged_couplings
        if mdao_definition in ['CO']:
            problem_formulation['coupled_functions_groups'] = [['D[1]'], ['D[2]']]
        if mdao_architecture in ['unconverged-DOE', 'converged-DOE']:
            problem_formulation['doe_settings'] = doe_settings = dict()
            doe_settings['method'] = 'Custom design table'
            if doe_settings['method'] in ['Latin hypercube design', 'Monte Carlo design', 'Uniform design']:
                doe_settings['seed'] = 6
                doe_settings['runs'] = 5
            elif doe_settings['method'] in ['Full factorial design']:
                doe_settings['levels'] = 3
            elif doe_settings['method'] in ['Box-Behnken design']:
                doe_settings['center_runs'] = 2

        # Depending on the architecture, different additional node attributes have to be specified. This is automated here
        # to allow direct execution of all different options.
        if mdao_architecture in ['IDF', 'MDF', 'unconverged-OPT', 'CO']:
            fpg.mark_as_objective('/dataSchema/analyses/f')
            fpg.mark_as_constraints(['/dataSchema/analyses/g1', '/dataSchema/analyses/g2'], '>=', 0.0)
            fpg.mark_as_design_variables(['/dataSchema/variables/z1', '/dataSchema/variables/z2',
                                          '/dataSchema/variables/x0'], lower_bounds=[-10, 0.0, 0.0], upper_bounds=10,
                                         nominal_values=2.0)
        elif mdao_architecture in ['unconverged-MDA', 'converged-MDA']:
            fpg.mark_as_qois(['/dataSchema/analyses/f',
                              '/dataSchema/analyses/g1',
                              '/dataSchema/analyses/g2',
                              '/dataSchema/analyses/y1',
                              '/dataSchema/analyses/y2'])
        elif mdao_architecture in ['unconverged-DOE', 'converged-DOE']:
            fpg.mark_as_qois(['/dataSchema/analyses/f',
                              '/dataSchema/analyses/g1',
                              '/dataSchema/analyses/g2'])
            if doe_settings['method'] == 'Custom design table':
                fpg.mark_as_design_variable('/dataSchema/variables/z1', samples=[0.0, 0.1, 0.5, 0.75])
                fpg.mark_as_design_variable('/dataSchema/variables/z2', samples=[1.0, 1.1, 1.5, 1.75])
                fpg.mark_as_design_variable('/dataSchema/variables/x0', samples=[2.0, 2.1, 2.5, 2.75])
            else:
                fpg.mark_as_design_variable('/dataSchema/variables/z1', lower_bound=-10., upper_bound=10, nominal_value=2.0)
                fpg.mark_as_design_variable('/dataSchema/variables/z2', lower_bound=0., upper_bound=10., nominal_value=2.0)
                fpg.mark_as_design_variable('/dataSchema/variables/x0', lower_bound=0., upper_bound=10., nominal_value=2.0)
        if mdao_architecture in ['IDF', 'CO']:
            fpg.nodes['/dataSchema/analyses/y1']['valid_ranges'] = {'limit_range': {'minimum': -10., 'maximum': 10.}}
            fpg.nodes['/dataSchema/analyses/y2']['valid_ranges'] = {'limit_range': {'minimum': -10., 'maximum': 10.}}

        # Search for problem roles
        fpg.add_function_problem_roles()

        # Create a DSM visualization of the FPG
        fpg.create_dsm(file_name='FPG_'+mdao_definition, include_system_vars=True,
                       destination_folder=pdf_dir, keep_tex_file=not compile_pdf, compile_pdf=compile_pdf)
        fpg.save(file_name='FPG_'+mdao_definition, file_type='cmdows',
                 destination_folder=cmdows_dir, pretty_print=True)
        fpg.save(file_name='FPG_' + mdao_definition, file_type='kdms', destination_folder=kdms_dir)

        # Get Mdao graphs
        mdg = fpg.get_mdg(name='mdg Sellar problem')
        mpg = mdg.get_mpg(name='mpg Sellar problem')
        mdg.graph['name'] = 'XDSM - ' + mdao_definition
        mdg.graph['description'] = 'Solution strategy to solve the Sellar problem using the strategy: ' + \
                                   str(mdao_architecture) + ('_' + str(convergence_type) if convergence_type else '') + '.'

        # Create a DSM visualization of the Mdao
        mdg.create_dsm(file_name='Mdao_'+mdao_definition, include_system_vars=True, destination_folder=pdf_dir, mpg=mpg,
                       keep_tex_file=not compile_pdf, compile_pdf=compile_pdf)

        # Save the Mdao as cmdows (and do an integrity check)
        mdg.save('Mdao_' + mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
                 mpg=mpg,
                 description='Mdao CMDOWS file of the well-known Sellar problem',
                 creator='Imco van Gent',
                 version='0.1',
                 pretty_print=True,
                 convention=True)
        mdg.save('Mdao_' + mdao_definition, file_type='kdms', mpg=mpg, destination_folder=kdms_dir)
    logging.info('Done!')


if __name__ == '__main__':
    """ 0: unconverged-MDA-J
        1: unconverged-MDA-GS
        2: converged-DOE-GS
        3: converged-DOE-J
        4: converged-MDA-J
        5: converged-MDA-GS
        6: MDF-GS
        7: MDF-J
        8: IDF
        9: CO
    """
    # Set options
    analyze_mdao_definitions = 'all'

    # Run KADMOS
    run_kadmos(analyze_mdao_definitions, 'math')
    run_kadmos(analyze_mdao_definitions, 'competences')
