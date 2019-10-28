#
# IDAPython Core Utils
#

from idc import *
from idaapi import *
from idautils import *

import core


def comments_in_function(ea=None):
    """
    Searches the current function for IDA generated annotations
    Useful when dealing with large functions doing lots of logging
    @return: a dict {addr: comment}
    """

    comments = {}

    for addr, dis in core.iter_disasm(ea=ea):
        comm = Comment(addr)
        # Comment returns None if no comment
        if comm:
            comments[addr] = comm

    return comments


def calls_in_function(ea=None, unique=True):
    """
    Find calls within current function
    Execution transfer like jmp sub_xxx included
    @return: dictionary, d[addr] = dis
    """

    calls = {}

    for addr, dis in core.iter_disasm(ea=ea):
        if is_call_insn(addr) or core.is_external_jmp(addr):
            calls[addr] = dis

    return calls


def calculate_strings_list():
    """
    It finds all strings within a binary
    @return: dictionary {s_ea, string}
    """

    strings_d = {}

    s = Strings(False)
    s.setup()

    for v in s:
        try:
            str_t = GetStringType(v.ea)
            if str_t in (ASCSTR_C, ASCSTR_UNICODE):
                my_str = GetString(v.ea)
                strings_d[v.ea] = my_str

        except Exception as e:
            print "Error processing string at {:X}".format(v.ea)

    return strings_d


def most_referenced_functions(how_many=10):
    """
    Identifying these is an important first step
    @return: dict {f_ea: nr_of_refs}
    """
    references_d = {}

    for funcAddr in Functions():
        # stackoverflow ;)
        nr_of_refs = sum(1 for e in XrefsTo(funcAddr, True))
        references_d[funcAddr] = nr_of_refs

    # Let's order this stuff nicely
    sd = sorted(
        references_d.iteritems(),
        reverse=True,
        key=lambda (k, v): (v[0], k))

    top_ref_list = list(itertools.islice(sd, how_many))

    return top_ref_list


def find_imm_compares(ea=None):
    """
    Find all immediate compares in the current function.
    Very useful when debugging parsers, for example.
    @return: dict {address: disassembly}
    """
    cmp_addr = {}

    for addr, dis in core.iter_disasm(ea):
        if "cmp" in dis:
            if GetOpType(addr, 1) == o_imm:  # 5: immediate value
                # If this is ASCII, display for convenience
                v = GetOperandValue(addr, 1)
                if v > 0x20 and v <0x7F:
                    msg = "{0} ({1})".format(addr, chr(v))
                else:
                    msg = dis
                cmp_addr[addr] = msg

    return cmp_addr


def get_dword_compares(self):
    """
    Inspects the *whole* binary looking for comparisons between
    global dwords and immediate values. These usually contain error
    codes or alike and appear constantly through the code.
    @return: dict {op: ins}
    """
    dword_dict = defaultdict(list)

    # TODO: This is too x86...
    for f_addr in Functions():
        for ins in FuncItems(f_addr):
            m = GetMnem(ins)
            if m == 'cmp' or m == 'test':
                if GetOpType(ins, 1) == 5:  # o_imm: immediate value
                    if GetOpType(ins, 0) == 2:  # o_mem: memory ;)
                        op1, op2 = GetOpnd(ins, 0), GetOpnd(ins, 1)
                        if 'dword_' in op1:
                            # ex: cmp dword_xxx, 1000
                            # ex2: cmp cs:dword_xxx, 0
                            # Just unique values
                            if op2 not in dword_dict[op1]:
                                dword_dict[op1].append((op2, ins))

    return dword_dict


def get_all_functions():
    """
    It returns a list of all functions in a binary.
    This will not be cached since the names can change.
    @return: dict {f_ea: f_name}
    """

    func_d = {}

    for f_ea in Functions():
        f_name = GetFunctionName(f_ea) or "unknown_name"
        func_d[f_ea] = f_name

    return func_d


def get_dangerous_functions():
    """
    Gets a list of functions calling dangerous ones
    @returns: a *set* of func_addr's
    """

    all_funcs = get_all_functions()

    # TODO: use a centralized list for the dangerous functions?
    # TODO: this whole process must be O(mfg).
    bad_funcs = set([])

    dangerous_funcs = ["wcsncpy", "strcpy", "strncpy", "memmove", "memcpy"]

    for f_ea, f_name in all_funcs.items():
        for d_name in dangerous_funcs:
            # Use `in` to catch several variants of
            # the function name
            if d_name in f_name:
                func_addr = f_ea

            # find all code references to this dangerous function
            for ref in CodeRefsTo(func_addr, True):
                func_addr = core.function_boundaries(ea=ref.frm)[0]
                bad_funcs.add(func_addr)

    return bad_funcs
