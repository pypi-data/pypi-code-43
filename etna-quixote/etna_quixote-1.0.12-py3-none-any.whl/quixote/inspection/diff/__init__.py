from typing import List, Mapping, Union
from os import remove
import enum
from subprocess import PIPE, STDOUT
from quixote.inspection import KOError
import quixote.inspection as inspection
from tempfile import NamedTemporaryFile


class DiffFormat(enum.Enum):
    CONTEXT = 0
    UNIFIED = 1


def diff(
        file1: str,
        file2: str,
        *,
        brief: bool = False,
        report_identical: bool = False,
        recursive: bool = False,
        absent_as_empty: bool = False,
        ignore_case: bool = False,
        ignore_tab_expansion: bool = False,
        ignore_trailing_space: bool = False,
        ignore_space_amount: bool = False,
        ignore_whitespace: bool = False,
        ignore_blank_lines: bool = False,
        treat_as_text: bool = False,
        output_format: DiffFormat = None
) -> inspection.CompletedProcess:
    """
    Use the diff(1) command to compare files line by line

    :param file1:                   the first file to consider
    :param file2:                   the second file to consider
    :param brief:                   whether the details of the comparison should be omitted (default is False, see diff -q)
    :param report_identical:        whether identical files should be reported (default is False, see diff -s)
    :param recursive:               whether directories should be recursively compared (default is False, see diff -r)
    :param absent_as_empty:         whether absent files should be treated as empty (default is False, see diff -N)
    :param ignore_case:             whether case in the files contents should be ignored (default is False, see diff -i)
    :param ignore_tab_expansion:    whether tab expansion should be ignored (default is False, see diff -E)
    :param ignore_trailing_space:   whether trailing white space should be ignored (default is False, see diff -Z)
    :param ignore_space_amount:     whether the amount of white space should be ignored (default is False, see diff -b)
    :param ignore_whitespace:       whether all the white space should be ignored (default is False, see diff -w)
    :param ignore_blank_lines:      whether blank lines should be ignored (default is False, see diff -B)
    :param treat_as_text:           whether file contents should be treated as text, or automatically detected (default is False, see diff -a)
    :param output_format:           the format to use to display the results (default is CONTEXT, see diff -c and diff -u)
    """
    options = []
    if brief is True:
        options.append('-q')
    if report_identical is True:
        options.append('-s')
    if recursive is True:
        options.append('-r')
    if absent_as_empty is True:
        options.append('-N')
    if ignore_case is True:
        options.append('-i')
    if ignore_tab_expansion is True:
        options.append('-E')
    if ignore_trailing_space is True:
        options.append('-Z')
    if ignore_space_amount is True:
        options.append('-b')
    if ignore_whitespace is True:
        options.append('-w')
    if ignore_blank_lines is True:
        options.append('-B')
    if treat_as_text is True:
        options.append('-a')
    if output_format is not None:
        options.append('-u' if output_format == DiffFormat.UNIFIED else '-c')

    return inspection._run(['diff', *options, file1, file2], capture_output=True)


def diff_bytes(
        bytes1: bytes,
        bytes2: bytes,
        *,
        brief: bool = False,
        report_identical: bool = False,
        recursive: bool = False,
        absent_as_empty: bool = False,
        ignore_case: bool = False,
        ignore_tab_expansion: bool = False,
        ignore_trailing_space: bool = False,
        ignore_space_amount: bool = False,
        ignore_whitespace: bool = False,
        ignore_blank_lines: bool = False,
        treat_as_text: bool = False,
        output_format: DiffFormat = None,
) -> inspection.CompletedProcess:
    """
    Use the diff(1) command to compare two byte-objects

    :param bytes1:                      the first byte-object to consider
    :param bytes2:                      the second byte-object to consider
    :param brief:                       whether the details of the comparison should be omitted (default is False, see diff -q)
    :param report_identical:            whether identical files should be reported (default is False, see diff -s)
    :param recursive:                   whether directories should be recursively compared (default is False, see diff -r)
    :param absent_as_empty:             whether absent files should be treated as empty (default is False, see diff -N)
    :param ignore_case:                 whether case in the files contents should be ignored (default is False, see diff -i)
    :param ignore_tab_expansion:        whether tab expansion should be ignored (default is False, see diff -E)
    :param ignore_trailing_space:       whether trailing white space should be ignored (default is False, see diff -Z)
    :param ignore_space_amount:         whether the amount of white space should be ignored (default is False, see diff -b)
    :param ignore_whitespace:           whether all the white space should be ignored (default is False, see diff -w)
    :param ignore_blank_lines:          whether blank lines should be ignored (default is False, see diff -B)
    :param treat_as_text:               whether file contents should be treated as text, or automatically detected (default is False, see diff -a)
    :param output_format:               the format to use to display the results (default is CONTEXT, see diff -c and diff -u)
    """
    tmp_file1 = NamedTemporaryFile().name
    tmp_file2 = NamedTemporaryFile().name
    with open(tmp_file1, "wb") as f:
        f.write(bytes1)
    with open(tmp_file2, "wb") as f:
        f.write(bytes2)

    completed_diff = diff(
        tmp_file1, tmp_file2,
        brief=brief,
        report_identical=report_identical,
        recursive=recursive,
        absent_as_empty=absent_as_empty,
        ignore_case=ignore_case,
        ignore_tab_expansion=ignore_tab_expansion,
        ignore_trailing_space=ignore_trailing_space,
        ignore_space_amount=ignore_space_amount,
        ignore_whitespace=ignore_whitespace,
        ignore_blank_lines=ignore_blank_lines,
        treat_as_text=treat_as_text,
        output_format=output_format,
    )

    remove(tmp_file1)
    remove(tmp_file2)

    return completed_diff


def diff_strings(
        str1: str,
        str2: str,
        *,
        brief: bool = False,
        report_identical: bool = False,
        recursive: bool = False,
        absent_as_empty: bool = False,
        ignore_case: bool = False,
        ignore_tab_expansion: bool = False,
        ignore_trailing_space: bool = False,
        ignore_space_amount: bool = False,
        ignore_whitespace: bool = False,
        ignore_blank_lines: bool = False,
        output_format: DiffFormat = None,
) -> inspection.CompletedProcess:
    """
    Use the diff(1) command to compare two strings line by line

    :param str1:                        the first string to consider
    :param str2:                        the second string to consider
    :param brief:                       whether the details of the comparison should be omitted (default is False, see diff -q)
    :param report_identical:            whether identical files should be reported (default is False, see diff -s)
    :param recursive:                   whether directories should be recursively compared (default is False, see diff -r)
    :param absent_as_empty:             whether absent files should be treated as empty (default is False, see diff -N)
    :param ignore_case:                 whether case in the files contents should be ignored (default is False, see diff -i)
    :param ignore_tab_expansion:        whether tab expansion should be ignored (default is False, see diff -E)
    :param ignore_trailing_space:       whether trailing white space should be ignored (default is False, see diff -Z)
    :param ignore_space_amount:         whether the amount of white space should be ignored (default is False, see diff -b)
    :param ignore_whitespace:           whether all the white space should be ignored (default is False, see diff -w)
    :param ignore_blank_lines:          whether blank lines should be ignored (default is False, see diff -B)
    :param output_format:               the format to use to display the results (default is CONTEXT, see diff -c and diff -u)
    """
    return diff_bytes(
        str1.encode(),
        str2.encode(),
        brief=brief,
        report_identical=report_identical,
        recursive=recursive,
        absent_as_empty=absent_as_empty,
        ignore_case=ignore_case,
        ignore_tab_expansion=ignore_tab_expansion,
        ignore_trailing_space=ignore_trailing_space,
        ignore_space_amount=ignore_space_amount,
        ignore_whitespace=ignore_whitespace,
        ignore_blank_lines=ignore_blank_lines,
        treat_as_text=True,
        output_format=output_format,
    )


def diff_exec(
        exec1: Union[str, List[str]],
        exec2: Union[str, List[str]],
        arguments: List[str] = None,
        second_arguments: List[str] = None,
        brief: bool = False,
        report_identical: bool = False,
        recursive: bool = False,
        absent_as_empty: bool = False,
        ignore_case: bool = False,
        ignore_tab_expansion: bool = False,
        ignore_trailing_space: bool = False,
        ignore_space_amount: bool = False,
        ignore_whitespace: bool = False,
        ignore_blank_lines: bool = False,
        treat_as_text: bool = False,
        output_format: DiffFormat = None,
        timeout: int = None,
        redirect_stderr_in_stdout: bool = False,
        env: Mapping[str, str] = None,
        allowed_status: Union[int, List[int]] = 0
) -> inspection.CompletedProcess:
    """
    Use the diff(1) command to compare the output line by line of two executables

    :param exec1:                       the first executable to consider
    :param exec2:                       the second executable to consider
    :param arguments:                   the argument list to give to the executables (default is None, to give no arguments)
    :param second_arguments:            the argument list to give to the second executable (default is None, to use the value of ``arguments``)
    :param brief:                       whether the details of the comparison should be omitted (default is False, see diff -q)
    :param report_identical:            whether identical files should be reported (default is False, see diff -s)
    :param recursive:                   whether directories should be recursively compared (default is False, see diff -r)
    :param absent_as_empty:             whether absent files should be treated as empty (default is False, see diff -N)
    :param ignore_case:                 whether case in the files contents should be ignored (default is False, see diff -i)
    :param ignore_tab_expansion:        whether tab expansion should be ignored (default is False, see diff -E)
    :param ignore_trailing_space:       whether trailing white space should be ignored (default is False, see diff -Z)
    :param ignore_space_amount:         whether the amount of white space should be ignored (default is False, see diff -b)
    :param ignore_whitespace:           whether all the white space should be ignored (default is False, see diff -w)
    :param ignore_blank_lines:          whether blank lines should be ignored (default is False, see diff -B)
    :param treat_as_text:               whether file contents should be treated as text, or automatically detected (default is False, see diff -a)
    :param output_format:               the format to use to display the results (default is CONTEXT, see diff -c and diff -u)
    :param timeout:                     the timeout in seconds after which processes should be killed
    :param redirect_stderr_in_stdout:   whether stderr should be redirected in stdout for both executables
    :param env:                         the environment to pass to the executables
    :param allowed_status:              status or list of statuses considered successful for both executables

    :raise quixote.inspection.KOError:  if one of the executables' return status doesn't match one of the allowed statuses
    :raise quixote.inspection.TiemoutError: if timeout is not None and expires before a child process terminates
    """
    if isinstance(exec1, str):
        exec1 = [exec1]
    if isinstance(exec2, str):
        exec2 = [exec2]
    io_options = {"capture_output": True}
    if redirect_stderr_in_stdout is True:
        io_options = {"stdout": PIPE, "stderr": STDOUT}
    if isinstance(allowed_status, int):
        allowed_status = [allowed_status]

    arg1 = arguments or []
    try:
        completed_process_1 = inspection._run(exec1 + list(arg1), **io_options, timeout=timeout, env=env) \
            .check(f"unexpected exit code for process: {exec1}", allowed_status=allowed_status)
    except OSError as e:
        raise KOError(f"cannot execute process {exec1}: {e.strerror}")

    arg2 = second_arguments or arg1
    try:
        completed_process_2 = inspection._run(exec2 + list(arg2), **io_options, timeout=timeout, env=env) \
            .check(f"unexpected exit code for process: {exec2}", allowed_status=allowed_status)
    except OSError as e:
        raise KOError(f"cannot execute process {exec2}: {e.strerror}")

    return diff_bytes(
        completed_process_1.raw_stdout,
        completed_process_2.raw_stdout,
        brief=brief,
        report_identical=report_identical,
        recursive=recursive,
        absent_as_empty=absent_as_empty,
        ignore_case=ignore_case,
        ignore_tab_expansion=ignore_tab_expansion,
        ignore_trailing_space=ignore_trailing_space,
        ignore_space_amount=ignore_space_amount,
        ignore_whitespace=ignore_whitespace,
        ignore_blank_lines=ignore_blank_lines,
        treat_as_text=treat_as_text,
        output_format=output_format,
    )
