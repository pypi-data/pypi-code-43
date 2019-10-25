#!/usr/bin/env python3
import sys


class State:
    UNKNOWN = 3
    CRITICAL = 2
    WARNING = 1
    OK = 0


class Results:
    def format_and_print(self, output_strings, state, results=None):
        output = output_strings[state]
        if results != None:
            result_string = "|"
            for key, value in results.items():
                result_string = f'{result_string} {key}={value};'
            output = f'{output}{result_string}'
        print(output)
        sys.exit(state)


class Check(State):
    def numeric_check(self, count_result, warning, critical):
        if count_result >= critical:
            return self.CRITICAL
        elif count_result >= warning:
            return self.WARNING
        elif count_result < warning:
            return self.OK
        else:
            return self.UNKNOWN

    def numeric_low_high_check(self, count_result, low_warning, high_warning, low_critical, high_critical):
        if count_result <= low_critical:
            return self.CRITICAL
        elif count_result >= high_critical:
            return self.CRITICAL
        elif count_result <= low_warning:
            return self.WARNING
        elif count_result >= high_warning:
            return self.WARNING
        elif count_result > low_warning and count_result < high_warning:
            return self.OK
        else:
            return self.UNKNOWN

    def string_check(self, stringResult, asserStrings):
        if stringResult in asserStrings:
            return self.OK
        else:
            return self.CRITICAL



class Output(Results, Check):

    def numeric_output(self, count_result, output_strings, warning, critical, low_warning=None, low_critical=None, results=None):
        if low_warning and low_critical:
            check_result = self.numeric_low_high_check(count_result, low_warning, warning, low_critical, critical)
            self.format_and_print(output_strings, check_result, results)
        else:
            check_result = self.numeric_check(count_result, warning, critical)
            self.format_and_print(output_strings, check_result, results)

    def string_output(self, stringResult, assertStrings, output_strings, results=None):
        check_result = self.string_check(stringResult, assertStrings)
        self.format_and_print(output_strings, check_result, results)

    def simple_output(self, output_strings, exit_state, results=None):
        if exit_state == 0:
            self.format_and_print(output_strings, exit_state, results)
        elif exit_state == 1:
            self.format_and_print(output_strings, exit_state, results)
        elif exit_state == 2:
            self.format_and_print(output_strings, exit_state, results)
        else:
            self.format_and_print(output_strings, exit_state, results)
