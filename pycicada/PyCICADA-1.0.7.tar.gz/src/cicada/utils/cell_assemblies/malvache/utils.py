def load_cell_assemblies_data(data_file_name):
    """
    Load data concerning cell assemblies detection using Malvache et al. method.
    Args:
        data_file_name: File_name (with path) of the data file containing the result of the analysis (txt file)

    Returns: a list with 5 structures
    1. cell_assemblies: list of list, each list correspond to one cell assembly
    2. sce_times_in_single_cell_assemblies: dict, key is the CA index, each value is a list correspond to tuples
    (first and last index of the SCE in frames)
    3. sce_times_in_multiple_cell_assemblies: list of tuples representing the the first and last index of SCE part of
    multiple cell assemblies
    4. sce_times_in_cell_assemblies: list of list, each list correspond to tuples
    (first and last index of the SCE in frames)
    5. sce_times_in_cell_assemblies_by_cell: dict, for each cell, list of list, each correspond to tuples
    (first and last index of the SCE in frames) in which the cell is supposed
    to be active for the single cell assembly to which it belongs

    """
    # list of list, each list correspond to one cell assemblie
    cell_assemblies = []
    # key is the CA index, eachkey is a list correspond to tuples
    # (first and last index of the SCE in frames)
    sce_times_in_single_cell_assemblies = dict()
    sce_times_in_multiple_cell_assemblies = []
    # list of list, each list correspond to tuples (first and last index of the SCE in frames)
    sce_times_in_cell_assemblies = []
    # for each cell, list of list, each correspond to tuples (first and last index of the SCE in frames)
    # in which the cell is supposed to be active for the single cell assemblie to which it belongs
    sce_times_in_cell_assemblies_by_cell = dict()

    with open(data_file_name, "r", encoding='UTF-8') as file:
        param_section = False
        cell_ass_section = False
        for nb_line, line in enumerate(file):
            if line.startswith("#PARAM#"):
                param_section = True
                continue
            if line.startswith("#CELL_ASSEMBLIES#"):
                cell_ass_section = True
                param_section = False
                continue
            if cell_ass_section:
                if line.startswith("SCA_cluster"):
                    cells = []
                    line_list = line.split(':')
                    cells = line_list[2].split(" ")
                    cell_assemblies.append([int(cell) for cell in cells])
                elif line.startswith("single_sce_in_ca"):
                    line_list = line.split(':')
                    ca_index = int(line_list[1])
                    sce_times_in_single_cell_assemblies[ca_index] = []
                    couples_of_times = line_list[2].split("#")
                    for couple_of_time in couples_of_times:
                        times = couple_of_time.split(" ")
                        sce_times_in_single_cell_assemblies[ca_index].append([int(t) for t in times])
                        sce_times_in_cell_assemblies.append([int(t) for t in times])
                elif line.startswith("multiple_sce_in_ca"):
                    line_list = line.split(':')
                    sces_times = line_list[1].split("#")
                    for sce_time in sces_times:
                        times = sce_time.split(" ")
                        sce_times_in_multiple_cell_assemblies.append([int(t) for t in times])
                        sce_times_in_cell_assemblies.append([int(t) for t in times])
                elif line.startswith("cell"):
                    line_list = line.split(':')
                    cell = int(line_list[1])
                    sce_times_in_cell_assemblies_by_cell[cell] = []
                    sces_times = line_list[2].split("#")
                    for sce_time in sces_times:
                        times = sce_time.split()
                        sce_times_in_cell_assemblies_by_cell[cell].append([int(t) for t in times])

    results = list()
    results.append(cell_assemblies)
    results.append(sce_times_in_single_cell_assemblies)
    results.append(sce_times_in_multiple_cell_assemblies)
    results.append(sce_times_in_cell_assemblies)
    results.append(sce_times_in_cell_assemblies_by_cell)
    return results
