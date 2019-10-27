from typing import Callable, Union, Optional, List, Type
import random


class EvaluationCaseResult:

    def __init__(self,
                 is_successful: bool = False,
                 performance: Optional[Union[float, int]] = None,
                 e: Optional[Exception] = None):

        self.is_successful = is_successful
        self.performance = performance
        self.exception_thrown = e


class CasePerformance:

    def __init__(self,
                 is_successful: bool = False,
                 performance: Optional[Union[float, int]] = None):

        self.is_successful = is_successful
        self.performance = performance


class EvalCase:

    performance_bigger_better = False
    main_complexity_var = None

    def _evaluate(self, solution: Callable) -> CasePerformance:

        return CasePerformance()

    def evaluate(self, solution: Callable) -> EvaluationCaseResult:

        try:
            out = self._evaluate(solution)
            e = None
        except Exception as _e:
            e = _e
            out = CasePerformance()

        return EvaluationCaseResult(
            is_successful=out.is_successful,
            e=e,
            performance=out.performance
        )

    def describe_case(self):
        pass


class CompleteEvaluation:

    def __init__(self,
                 case_kwarg_list: List[dict],
                 case: Type[EvalCase]):

        self.case = case
        self.case_kwarg_list = case_kwarg_list
        self.case_results_list = [EvaluationCaseResult()] * len(case_kwarg_list)
        self.success_list = [False] * len(case_kwarg_list)
        self.error_list = [None] * len(case_kwarg_list)
        self.performance_list = [None] * len(case_kwarg_list)

    def evaluate(self, solution: Callable):
        self._run_all(solution)
        print(self)

    def visualize(self, solution: Callable):

        import matplotlib.pyplot as plt
        self._run_all(solution)

        data = self._get_performance_plot()
        plt.figure(figsize=(11, 7))

        for label, ser in data.items():
            if label != self.case.main_complexity_var:
                if label == '-Successes':
                    marker = None
                else:
                    marker = 'o'
                plt.plot(self.case.main_complexity_var,
                         label,
                         marker=marker,
                         linestyle='',
                         data=data)
        plt.ylabel('performance')
        plt.xlabel(self.case.main_complexity_var)
        plt.legend()
        plt.show()

    def _run_all(self, solution: Callable):

        num_kwargs = len(self.case_kwarg_list)
        self.case_results_list = [EvaluationCaseResult()] * num_kwargs
        self.success_list = [False] * num_kwargs
        self.error_list = [None] * num_kwargs
        self.performance_list = [None] * num_kwargs

        iterable = random.sample(list(enumerate(self.case_kwarg_list)),
                                 num_kwargs)

        for kwarg_idx, case_kwargs in iterable:
            case = self.case(**case_kwargs)
            act_case_results = case.evaluate(solution)
            self.case_results_list[kwarg_idx] = act_case_results

            if act_case_results.exception_thrown is not None:
                self.error_list[kwarg_idx] = act_case_results.exception_thrown
            self.success_list[kwarg_idx] = act_case_results.is_successful
            self.performance_list[kwarg_idx] = act_case_results.performance

    def _get_str_results(self) -> str:

        numeric_performances = [p for p in self.performance_list
                                if p is not None]

        if len(numeric_performances) > 0:

            if self.case.performance_bigger_better:
                bestfun = max
                worstfun = min
            else:
                bestfun = min
                worstfun = max

            performance_summas = [
                '- best performance: {}'.format(bestfun(numeric_performances)),
                '- worst performance: {}'.format(worstfun(numeric_performances)),
                '- mean performance: {}'.format(sum(numeric_performances) /
                                                len(numeric_performances)),
            ]
        else:
            performance_summas = []

        error_strings = []
        miss_strings = []
        for idx, succ in enumerate(self.success_list):

            if not succ:
                e = self.error_list[idx]
                act_kwargs = self.case_kwarg_list[idx]
                if e is not None:
                    error_strings.append(
                        '\n\n ERROR at: \n {} \n - {} ({})'.format(act_kwargs,
                                                                   type(e).__name__,
                                                                   e)
                    )
                else:
                    miss_strings.append(
                        '\n\n BAD SOLUTION at: \n {}'.format(act_kwargs)
                    )

        return '\n'.join(
            ['- success rate: {}/{} ({}%)'.format(sum(self.success_list),
                                                  len(self.case_kwarg_list),
                                                  round(sum(self.success_list) /
                                                        len(self.case_kwarg_list),
                                                        2) * 100),
             '- error count: {}'.format(sum([e is not None for e in self.error_list])),
             *performance_summas,
             *miss_strings[:10],
             *error_strings[:10]]
        )

    def _get_performance_plot(self) -> dict:

        if self.case.main_complexity_var is None:
            return {}
        else:
            cvar = self.case.main_complexity_var
            successes = []
            fails = []
            errors = []
            c_values = []
            for idx, case_kwargs in enumerate(self.case_kwarg_list):

                perf_value = self.performance_list[idx]
                if self.success_list[idx]:
                    successes.append(perf_value)
                    fails.append(None)
                    errors.append(None)
                elif self.error_list[idx] is not None:
                    successes.append(None)
                    fails.append(None)
                    errors.append(0)
                else:
                    successes.append(None)
                    fails.append(0)
                    errors.append(None)

                c_values.append(case_kwargs.get(cvar))

        out = {
            cvar: c_values
        }
        for ser, label in [(successes, 'Successes'),
                           (fails, 'Bad solutions'),
                           (errors, 'Errors')]:
            if sum([e is None for e in ser]) < len(ser):
                out[label] = ser
        return out

    def __str__(self):

        if len(self.case_results_list) > 0:
            return self._get_str_results()
        else:
            return 'not yet evaluated'

    def __repr__(self):

        return self.__str__()
