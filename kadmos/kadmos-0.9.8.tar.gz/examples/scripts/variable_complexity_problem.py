import os

import networkx as nx

from kadmos.graph import RepositoryConnectivityGraph, FundamentalProblemGraph

# List of MDAO definitions that can be wrapped around the problem
mdao_definitions = ['converged-MDA-GS',         # 0
                    'converged-MDA-J',          # 1
                    'MDF-GS',                   # 2
                    'MDF-J',                    # 3
                    'IDF']                      # 4

n_partitions = 2      # Number of partitions
partition_range = []  # Option to analyze a specific range of partitions. If set to 'pareto', the pareto
                      # front is calculated. After the analysis a number of partitions can be chosen.

result_dir = 'variable_complexity_problem'
pdf_dir = os.path.join(result_dir, '(X)DSM')
cmdows_dir = os.path.join(result_dir, 'CMDOWS')
kdms_dir = os.path.join(result_dir, 'KDMS')
vistoms_dir = os.path.join(result_dir, 'VISTOMS')

rcg = RepositoryConnectivityGraph(name='Variable complexity problem RCG')

# TODO: Store matrix definitions and load them
math_problem = rcg.create_mathematical_problem(10, 0.1, n_local_constraints=[0]*10)

rcg.save('VCP_RCG.kdms', destination_folder=kdms_dir)

rcg.create_dsm('VCP_RCG.pdf', destination_folder=pdf_dir, open_pdf=False)

if nx.is_directed_acyclic_graph(rcg):
    raise AssertionError('Invalid graph created.')

# An initial fundamental problem graph is created based on the rcg
fpg_initial = FundamentalProblemGraph(rcg)

for mdao_definition in mdao_definitions:

    print('Scripting FPG_' + str(mdao_definition) + '...')

    # Reset FPG
    fpg = fpg_initial.deepcopy()
    fpg.graph['name'] = rcg.graph['name'] + ' - ' + mdao_definition + ' - FPG'
    fpg.graph['description'] = 'Fundamental problem graph for solving the variable complexity problem using the ' \
                               'strategy: ' + mdao_definition + '.'

    # Get function order (needed to determine the problem roles)
    function_order = fpg.get_possible_function_order(use_runtime_info=True)

    # Define settings of the problem formulation
    fpg.add_problem_formulation(mdao_definition, function_order)

    if mdao_definition in ['MDF-GS', 'MDF-J', 'IDF']:
        # Assign design variables
        design_variables = [node for node in fpg.find_all_nodes(category='variable') if 'design_variable' in node]
        fpg.mark_as_design_variables(design_variables, lower_bounds=[-5]*len(design_variables),
                                     upper_bounds=[5]*len(design_variables),
                                     nominal_values=[-0.5]*len(design_variables))
        # Assign objective
        fpg.mark_as_objective('/data_schema/objective/f')
        # Assign constraints
        fpg.mark_as_constraints([node for node in fpg.find_all_nodes(category='variable') if 'constraint' in node],
                                '<=', 0.0)

    if mdao_definition in ['converged-MDA-GS', 'converged-MDA-J']:
        qois = [node for node in fpg.find_all_nodes(category='variable') if ('coupling_variable' in node or
                                                                             'constraint' in node or
                                                                             'objective' in node)]
        fpg.mark_as_qois(qois)

    # Search for problem roles
    fpg.add_function_problem_roles()

    # Partition graph
    if partition_range:
        fpg.select_number_of_partitions(partition_range, local_convergers=True,
                                        rcb_partitioning=0.5, plot_solutions=True,
                                        use_runtime_info=True)
    elif n_partitions > 0:
        fpg.partition_graph(n_partitions, use_runtime_info=True, local_convergers=True,
                            rcb_partitioning=0.5)

    # Update function order with partitioning
    function_order = fpg.get_possible_function_order(use_runtime_info=True)
    fpg.graph['problem_formulation']['function_order'] = function_order

    # Create a DSM visualization of the FPG
    colors_coupled_functions = 'partitions' if 'coupled_functions_groups' in fpg.graph['problem_formulation'] else \
        'function_roles'
    fpg.create_dsm(file_name='FPG_' + mdao_definition, function_order=function_order, include_system_vars=True,
                   destination_folder=pdf_dir, colors_based_on=colors_coupled_functions, summarize_vars=False,
                   open_pdf=False)

    # Save the FPG as kdms
    fpg.save('FPG_' + mdao_definition, destination_folder=kdms_dir)
    # Save the FPG as cmdows (and do an integrity check)
    fpg.save('FPG_' + mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
             description='FPG CMDOWS file of the variable complexity problem',
             creator='Anne-Liza Bruggeman',
             version='0.1',
             pretty_print=True,
             integrity=True)

    print('Scripting Mdao_' + str(mdao_definition) + '...')

    # Get Mdao graphs
    mdg, mpg = fpg.impose_mdao_architecture()
    mdg.graph['name'] = rcg.graph['name'] + ' - ' + mdao_definition + ' - Mdao'
    mdg.graph['description'] = 'Solution strategy to solve the variable complexity problem using the strategy: ' \
                               '{}.'.format(mdao_definition)

    # Create a DSM visualization of the MDAO
    mdg.create_dsm(file_name='Mdao_' + mdao_definition, include_system_vars=True, destination_folder=pdf_dir,
                   mpg=mpg, summarize_vars=False, colors_based_on=colors_coupled_functions, open_pdf=False,
                   keep_tex_file=False)

    # Save the Mdao as kdms
    mdg.save('Mdao_' + mdao_definition, destination_folder=kdms_dir, mpg=mpg)
    # Save the Mdao as cmdows (and do an integrity check)
    mdg.save('Mdao_' + mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
             mpg=mpg,
             description='Mdao CMDOWS file of the variable complexity problem',
             creator='Anne-Liza Bruggeman',
             version='0.1',
             pretty_print=True,
             integrity=True)

    # # Create OpenLEGO model
    # print 'Scripting OpenLEGO model'
    # problem = LEGOProblem(os.path.join(cmdows_dir, 'Mdao_' + mdao_definition + '.xml'), data_folder=result_dir)
    #
    # # Calculate partial derivatives over the entire model
    # problem.model.approx_totals(method='fd')
    #
    # # Initialize model
    # problem.initialize()
    #
    # # Create n2 chart
    # view_model(problem.model, show_browser=False)
    #
    # # Run model
    # print 'Run OpenMDAO'
    # problem.run_driver()
    #
    # # Get results
    # result = problem.collect_results()
    #
