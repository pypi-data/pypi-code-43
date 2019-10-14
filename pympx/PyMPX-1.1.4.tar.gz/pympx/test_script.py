# Test config for FAAS site
from _Library import Simple_Empower_API as s

e = s.Empower(site_file = r"C:\Empower Sites\FAAS Divestment Model\FAAS Divestment Model.eks",
			data_sub_folder = "00. Client Files",
			username = "Administrator",
			version = "9.3",
			password_mode = "getpass",
			script_sub_sub_folder = "03. Load Processes\_Scripts",
			welcome_prompt = "03. Load Processes\_Prompts\welcome prompt.txt")

# Run some test commands			
e.run_batch(['Housekeep'])

# Export mapping files for each of the synchronised structures that will be used for load processd
# - Specify a name for the mapping file, what dimension it comes from, and what structure in that dimension to use
structures = {'primary_reporting_structure': {'dim': 0, 'struc': 'X01.Primar'}
              ,'secondary_reporting_structure': {'dim': 1, 'struc': 'X01.Second'}
              ,'fs_gl_level': {'dim': 8, 'struc': 'X01.2.Fina'}
              ,'fs_presented_level': {'dim': 8, 'struc': 'X01.3.Fina'}
			  ,'currencies': {'dim': 10, 'struc': 'X11.01'}
			  ,'period': {'dim': 11, 'struc': 'X12.01'}
			}
			
for i in structures:
    e.get_mapping_from_field(dimension = structures[i]['dim'],
                             structure = structures[i]['struc'],
                             field = 'xRef',
                             mapping_name = i,
                             subfolder = r'04. Processed Metadata\02. Mapping')

# Get the allocation basis separately
e.get_mapping_from_field(dimension = 8, structure = 'X9.03.2', field = 'xRefAB', mapping_name = 'allocation_basis', subfolder = r'04. Processed Metadata\02. Mapping', include_count = True)


# Update consolidation calculations
consolidation_calculation_commands = ['AddConsolidationCalcs Dimension = 1, Structure = 01.Primary_Structure, Sparse Addition = true, Real Calculations = true, Framework = Default Framework'
									,'AddConsolidationCalcs Dimension = 2, Structure = 01.Secondary_Structure, Sparse Addition = true, Real Calculations = true, Framework = Default Framework'
									,'AddConsolidationCalcs Dimension = 9, Structure = 01.2.Financial_Statements_GL, Sparse Addition = true, Real Calculations = true, Framework = Default Framework'
									,'AddConsolidationCalcs Dimension = 1, Structure = 01.Primary_Structure, Sparse Addition = true, Real Calculations = true, Framework = 04. Real Hierarchies'
									,'AddConsolidationCalcs Dimension = 2, Structure = 01.Secondary_Structure, Sparse Addition = true, Real Calculations = true, Framework = 04. Real Hierarchies'
									,'AddConsolidationCalcs Dimension = 9, Structure = 01.2.Financial_Statements_GL, Sparse Addition = true, Real Calculations = true, Framework = 04. Real Hierarchies'
									
									,'AddConsolidationCalcs Dimension = 1, Structure = 01.Primary_Structure, Sparse Addition = true, Real Calculations = false, Framework = 01. Virtual Consolidation - Primary Reporting Structure'
									,'AddConsolidationCalcs Dimension = 2, Structure = 01.Secondary_Structure, Sparse Addition = true, Real Calculations = false, Framework = 02. Virtual Consolidation - Secondary Reporting Structure'
									,'AddConsolidationCalcs Dimension = 9, Structure = 01.2.Financial_Statements_GL, Sparse Addition = true, Real Calculations = false, Framework = 03.1 Virtual Consolidation - Financial Statement - GL'
									,'AddConsolidationCalcs Dimension = 9, Structure = 01.3.Financial_Statements_Presented, Sparse Addition = true, Real Calculations = false, Framework = 03.2 Virtual Consolidation - Financial Statement - Presented'
									
									,'AddConsolidationCalcs Dimension = 1, Structure = 01.Primary_Structure, Sparse Addition = true, Real Calculations = false, Framework = 05. Virtual Consolidation - Primary and Financial Statement'
									,'AddConsolidationCalcs Dimension = 9, Structure = 01.2.Financial_Statements_GL, Sparse Addition = true, Real Calculations = false, Framework = 05. Virtual Consolidation - Primary and Financial Statement'
									]

#e.run_batch(consolidation_calculation_commands)
									
# Run Focus Calculate
commands = ['FocusCalculate Calc Viewpoint = 3, Calc Focus = 1=#5##1#5;2=#5##1#9;3=#1##1#-1;4=#1##1#-1;5=#1##1#-1;6=#1##1#-1;7=#1##1#-1;8=#1##1#-1;9=#6##1#1;10=#1##1#-1;11=#1##1#1;12=#3##1#2;13=#1##1#-1;, Packet = 150000, Expand = true'
		    ,'FocusCalculate Calc Viewpoint = 3, Calc Focus = 1=#5##1#5;2=#6##1#9;3=#1##1#-1;4=#1##1#-1;5=#1##1#-1;6=#1##1#-1;7=#1##1#-1;8=#1##1#-1;9=#6##1#1;10=#1##1#-1;11=#1##1#1;12=#3##1#2;13=#1##1#-1;, Packet = 150000, Expand = true'
		    ,'FocusCalculate Calc Viewpoint = 3, Calc Focus = 1=#6##1#5;2=#6##1#9;3=#1##1#-1;4=#1##1#-1;5=#1##1#-1;6=#1##1#-1;7=#1##1#-1;8=#1##1#-1;9=#6##1#1;10=#1##1#-1;11=#1##1#1;12=#3##1#2;13=#1##1#-1;, Packet = 150000, Expand = true'
		    ]

#e.run_batch(commands)

# Run the prep script for metadata
e.run_importer('process_financial_statement_structures.eimp')
e.run_importer('process_primary_reporting_structure.eimp')
e.run_importer('process_secondary_reporting_structure.eimp')


# Zip up part of the site
e.zip_site(target_folder = 'Archive', include_site_files = True, additional_folders = ['Commentary', 'Data Audit', 'Data Files'															
																,r'00. Client Files\01. Source Data\02. Prepared Files'
																,r'00. Client Files\02. Business Model Config\02. Prepared Files'
																,r'00. Client Files\04. Processed Metadata\01. Structures'
																])
															