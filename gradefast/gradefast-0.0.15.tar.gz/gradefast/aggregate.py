from gradefast.result import Result, ResultGroup

class Aggregate:
    """
    Contains method to group multiple :class:`~gradefast.result.ResultGroup` in different 
    ways

    Methods from this class may be used to combine results of same test, for instance, if 
    the submissions were sliced and results computed paralelly to save time. One can also
    concatenate results from different tests for aggregating it to form a final result. 
    Finally one can aggregate parameters of a test to form a final grade.

    For all such cases, use :class:`Aggregate`

    """
    @staticmethod
    def combine(*result_groups):
        """
        Combine multiple :class:`ResultGroup` obtained from **same** :class:`~gradefast.test.GFTest` 
        or :class:`~gradefad.GFCliTest`

        Parameters
        ----------
        results_groups: tuple
            As many result groups as you like to combine belonging to same test type

        Returns
        -------
        :class:`ResultGroup`
            Combined results groups

        """
        final_dict = {}
        
        for group in result_groups:
            final_dict.update(group.dict_of_results)
        
        if len(result_groups) > 0: 
            combined_group = ResultGroup(result_groups[0].task_name, result_groups[0].theme_name, final_dict)
            return combined_group
        
        return None

    @staticmethod
    def add(*result_groups):
        """
        Add parameters in ``result_dict`` of all results present in :class:`ResultGroup`
        to form a final total

        Parameters
        ----------
        results_groups: tuple
            As many result groups as you like to combine belonging to same test type

        Returns
        -------
        :class:`ResultGroup`
            Combined results groups obtained after adding
        """
        return Aggregate.operate('add', *result_groups)

    @staticmethod
    def multiply(weightages, *result_groups):
        """
        Transform marks by multiplying parameters with weightages in ``result_dict`` for 
        all results present in :class:`ResultGroup`

        Parameters
        ----------
        results_groups: tuple
            As many result groups as you like to multiply with weightages

        Returns
        -------
        :class:`ResultGroup`
            Combined results groups obtained after multiplying

        """
        return Aggregate.operate('multiply', *result_groups, weightages=weightages)

    @staticmethod
    def flatten_test_cases(average=True, *result_groups):
        """
        Flatten test cases of ``result_dict`` for all results present in :class:`ResultGroup`

        Parameters
        ----------
        average: bool
            Whether to simply add or average the list of marks in test cases
        results_groups: tuple
            As many result groups as you like to combine belonging to same test type
        
        Returns
        -------
        :class:`ResultGroup`
            Combined results groups obtained after flattening test cases

        """
        return Aggregate.operate('flatten_test_cases', *result_groups, average=average)

    @staticmethod
    def operate(method, *result_groups, weightages={}, average=True):
        if len(result_groups) > 0:
            combined_group = Aggregate.combine(*result_groups)
            final_result = {}
            for result in combined_group:
                if method == 'flatten_test_cases':
                    final_result[result.team_id] = result.flat_result()
                elif method == 'multiply':
                    final_result[result.team_id] = result.multiply(weightages)
                elif method == 'add':
                    final_result[result.team_id] = result.add()
            combined_group.dict_of_results = final_result
            return combined_group

    @staticmethod
    def join(*result_groups):
        """
        Concatenate multiple :class:`ResultGroup` performed on **same** :class:`~gradefast.test.GFTest` 
        or :class:`~gradefad.GFCliTest`

        Parameters
        ----------
        results_groups: tuple
            As many result groups as you like to combine belonging to same test type

        Returns
        -------
        :class:`ResultGroup`
            Combined results groups

        """
        task_names = set(map(lambda group: group.task_name, result_groups))
        if len(task_names) > 1:
            raise Exception('Result groups you are joining should be for the same task')

        theme_names = set(map(lambda group: group.theme_name, result_groups))
        if len(theme_names) > 1:
            raise Exception('Result groups you are joining should be for the same theme')

        # select results with particular team_ids and run join method on them
        team_ids = set()
        for group in result_groups:
            team_ids = team_ids.union(set(map(lambda team_id: team_id, group.dict_of_results)))
            
        final_results_dict = {}
        for team_id in team_ids:
            joined_result = {}
            for group in result_groups:
                if joined_result == {}:
                    joined_result = Result.join(group[team_id])
                else:
                    joined_result = Result.join(group[team_id], joined_result)
            final_results_dict[team_id] = joined_result
        
        return ResultGroup(result_groups[0].task_name, result_groups[0].theme_name, final_results_dict)
