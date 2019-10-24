import numpy as np
import numbers


def make_combinations_of_conditions_level_1(conditions_values=None, n_conditions=None, output_value=True,
                                        type_conditions_values=None, output_indexes=False, output_conditions=False,
                                        output_n_conditions=False, n_repetitions_combinations=1):
    # if (output_indexes is False) and (output_value is False):
    #     raise Exception('range and value are both False. Either one of them or both has to be True')
    # conditions_values = np.array([[1,2,3,4,6,8],[3,4,5]])
    # n_conditions = np.array([3, 5])

    if conditions_values is None and n_conditions is None:
        raise Exception(
            'conditions_values and n_conditions are both None.\n'
            'Either one of them or both has to be a list or an array')

    elif conditions_values is not None and n_conditions is not None:

        n_variables_from_conditions_values = len(conditions_values)
        n_variables_from_n_conditions = len(n_conditions)

        if n_variables_from_conditions_values != n_variables_from_n_conditions:
            raise Exception(
                'n_variables_from_conditions_values != n_variables_from_n_conditions\n'
                'n_variables_from_conditions_values = {}\nn_variables_from_n_conditions = {}\n'.format(
                    n_variables_from_conditions_values, n_variables_from_n_conditions))


        tmp_n_conditions = np.empty(n_variables_from_n_conditions, dtype=int)
        for i_variable in range(n_variables_from_n_conditions):
            tmp_n_conditions[i_variable] = len(conditions_values[i_variable])

        if np.any(tmp_n_conditions != n_conditions):
            raise Exception(
                'conditions_values and n_conditions are not compatible.\n'
                'conditions_values = {}\nn_conditions = {}\n'
                'If conditions_values = {},\nn_conditions has to be {} or None'.format(
                    conditions_values, n_conditions, conditions_values, tmp_n_conditions))

    else:
        # output_conditions = False

        if conditions_values is None and n_conditions is not None:

            # output_value = False
            # output_indexes = True
            # output_n_conditions = False

            n_variables = len(n_conditions)
            conditions_values = np.empty(n_variables, dtype=object)
            for i_variable in range(n_variables):
                conditions_values[i_variable] = np.arange(n_conditions[i_variable])

        if conditions_values is not None and n_conditions is None:



            n_variables = len(conditions_values)
            n_conditions = np.empty(n_variables, dtype=int)
            for i_variable in range(n_variables):
                n_conditions[i_variable] = len(conditions_values[i_variable])


        conditions_values = np.array(conditions_values)
        n_conditions = np.array(n_conditions)
        n_combinations = np.prod(n_conditions) * n_repetitions_combinations
        if n_combinations < 0:
            n_conditions = n_conditions.astype(np.int64)
            n_combinations = np.prod(n_conditions) * n_repetitions_combinations

        if output_value:
            # type_values = conditions_values.dtype
            # combinations_values = np.empty((n_combinations, n_variables), dtype=type_values)
            change_type_combinations_values = False

            if type_conditions_values is not None:
                combinations_values = np.empty((n_combinations, n_variables), dtype=type_conditions_values)

            else:

                if isinstance(conditions_values[0][0], str):
                    type_conditions_values = str
                    combinations_values = np.empty((n_combinations, n_variables), dtype=object)
                    change_type_combinations_values = True


                elif isinstance(conditions_values[0][0], numbers.Integral):

                    combinations_values = np.empty((n_combinations, n_variables), dtype=int)
                elif isinstance(conditions_values[0][0], numbers.Integral):

                    combinations_values = np.empty((n_combinations, n_variables), dtype=float)
                else:
                    type_conditions_values = type(conditions_values[0][0])
                    combinations_values = np.empty((n_combinations, n_variables), dtype=type_conditions_values)


            # combinations_values = np.empty((n_combinations, n_variables), dtype=object)
            combinations_values[:, -1] = np.resize(conditions_values[-1], n_combinations)

        if output_indexes:
            combinations_indexes = np.empty((n_combinations, n_variables), dtype=int)
            combinations_indexes[:, -1] = np.resize(np.arange(n_conditions[-1]), n_combinations)
        # print(n_variables)
        cumulative_n_combinations = n_conditions[-1]
        for i_variable in range(2, n_variables + 1):
            # print(i_variable)
            # cumulative_n_combinations *= n_conditions[-i_variable]
            if output_value:

                cumulative_combinations_values = np.empty(cumulative_n_combinations * n_conditions[-i_variable],
                                                            combinations_values.dtype)

                for i_condition in range(n_conditions[-i_variable]):
                    # combinations_values[:, -i_variable] = np.resize(
                    #     np.array([i for i in conditions_values[-i_variable] for j in range(cumulative_n_combinations)]),
                    #     n_combinations)
                    cumulative_combinations_values[
                        i_condition * cumulative_n_combinations : (i_condition + 1) * cumulative_n_combinations] = \
                        conditions_values[-i_variable][i_condition]

                combinations_values[:, -i_variable] = np.resize(cumulative_combinations_values, n_combinations)

            if output_indexes:
                combinations_indexes[:, -i_variable] = np.resize(
                    np.arange(
                        n_conditions[-i_variable] * cumulative_n_combinations) // cumulative_n_combinations,
                    n_combinations)

            cumulative_n_combinations *= n_conditions[-i_variable]

        list_outputs = []
        if output_value:

            if change_type_combinations_values:

                combinations_values = combinations_values.astype(type_conditions_values)

            list_outputs.append(combinations_values)

        if output_indexes:
            list_outputs.append(combinations_indexes)

        if output_conditions:
            list_outputs.append(conditions_values)

        if output_n_conditions:
            list_outputs.append(n_conditions)

        n_outputs = len(list_outputs)

        if n_outputs == 1:
            return list_outputs[0]
        elif n_outputs > 1:
            return list_outputs
        else:
            print('Warning: you did not ask any output in make_all_combinations_of_conditions().\n'
                  'To return something set the output options () to True.\n'
                  'by default, the outputs options are defined as:\n'
                  'output_value=True, output_indexes=False, output_conditions=False, output_n_conditions=False,')





def make_combinations_of_conditions_level_2(conditions_level_2, n_repetitions_combinations=1):

    n_variables = len(conditions_level_2)
    n_conditions_level_2 = np.empty(n_variables, dtype=object)

    for i_variable in range(n_variables):

        n_conditions_level_2[i_variable] = len(conditions_level_2[i_variable])

    combinations_of_groups_of_conditions = make_combinations_of_conditions_level_1(n_conditions=n_conditions_level_2)

    n_combinations = len(combinations_of_groups_of_conditions)

    combinations_of_conditions_level_2 = np.empty([n_combinations, n_variables], dtype=int)

    for i_variable in range(n_variables):

        for i_condition_level_2 in range(n_conditions_level_2[i_variable]):

            indexes_i_condition_level_2_in_combinations_of_groups = \
                np.argwhere(combinations_of_groups_of_conditions[:, i_variable] == i_condition_level_2)

            n_i_condition_level_2_in_combinations_of_groups = \
                len(indexes_i_condition_level_2_in_combinations_of_groups)

            combinations_of_conditions_level_2[indexes_i_condition_level_2_in_combinations_of_groups, i_variable] = \
                np.random.choice(conditions_level_2[i_variable][i_condition_level_2],
                                 n_i_condition_level_2_in_combinations_of_groups)[:, None]

    return combinations_of_conditions_level_2


def conditions_level_1_to_2(n_conditions_level_2, conditions_level_1):

    n_variables = len(n_conditions_level_2)

    # tmp_lower_conditions = np.copy(lower_conditions)

    conditions_level_2 = np.empty(n_variables, dtype=object)

    n_conditions_level_1 = np.empty(n_variables, dtype=int)

    n_conditions_level_1_in_1_condition_level_2 = np.empty(n_variables, dtype=float)

    for i_variable in range(n_variables):

        conditions_level_2[i_variable] = np.empty(n_conditions_level_2[i_variable], dtype=object)

        n_conditions_level_1[i_variable] = len(conditions_level_1[i_variable])

        n_conditions_level_1_in_1_condition_level_2[i_variable] = \
            n_conditions_level_1[i_variable] / n_conditions_level_2[i_variable]

        for i_condition_level_2 in range(n_conditions_level_2[i_variable]):

            conditions_level_2[i_variable][i_condition_level_2] = \
                conditions_level_1[i_variable][
                int(i_condition_level_2 * n_conditions_level_1_in_1_condition_level_2[i_variable]):
                int((i_condition_level_2 + 1) * n_conditions_level_1_in_1_condition_level_2[i_variable])]

    return conditions_level_2
