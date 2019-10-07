"""Module containing base functions to lint
    and dectect broken formatting rules
"""
import re
import yaml
import pkg_resources



def _compile_format_rule(rule, syntax):
    if rule['message'] is not None:
        rule['message'] = rule['message'].format(**syntax)
    else:
        rule['message'] = None

    rule['regexp'] = re.compile(rule['regexp'].format(**syntax))

    return rule

def _init_format_rules(line_length=132):
    """todo : inspect to get path to files"""

    syntax_rules = pkg_resources.resource_filename("flint", "rules/syntax.yaml")
    format_rules = pkg_resources.resource_filename("flint", "rules/format_rules.yaml")
    with open(syntax_rules) as fin:
        syntax = yaml.load(fin, Loader=yaml.FullLoader)
    with open(format_rules) as fin:
        rules = yaml.load(fin, Loader=yaml.FullLoader)

    for key in syntax:
        syntax[key] = r'|'.join(syntax[key])

    keys = ['message', 'regexp', 'replacement']
    syntax['types_upper'] = syntax['types'].upper()
    syntax['linelen'] = "%s" %line_length
    syntax['linelen_re'] = "{%s}" %line_length
    for key in rules:
        if all([desc in rules[key] for desc in keys]):
            rules[key] = _compile_format_rule(rules[key], syntax)
            rules[key]['subrules'] = False
        else:
            for subkey in rules[key]:
                rule = rules[key][subkey]
                rules[key][subkey] = _compile_format_rule(rule, syntax)
            rules[key]['subrules'] = True
    return rules

def _parse_format_line(filename, line, line_no, rules):
    msg_info = {'line_no': line_no,
                'line': line.replace('\n', ''),
                'filename': filename}
    format_stats = {"errors" : 0,
                    "modifs" : 0}
    for key in rules:
        if not rules[key]['subrules']:
            rule = rules[key]
            rule_stats = _parse_format_rule(line, msg_info, rule)
        else:
            subrules = [subkey for subkey in rules[key]
                        if subkey != "subrules"]
            for subkey in subrules:
                rule = rules[key][subkey]
                rule_stats = _parse_format_rule(line, msg_info, rule)
                if rule_stats["broken_rule"]:
                    break
        format_stats['errors'] += rule_stats["errors"]
        format_stats['modifs'] += rule_stats["modifs"]
    return  format_stats

def _parse_format_rule(line, msg_info, rule):
    rule_stats = {"broken_rule":False,
                  "errors" : 0,
                  "modifs" : 0}
    replacement = line
    for res in rule['regexp'].finditer(line):
        msg_info['column'] = res.start() + 1
        rule_stats["broken_rule"] = True
        if rule['replacement'] is not None:
            rule_stats['modifs'] += 1
            replacement = rule['regexp'].sub(rule['replacement'],
                                             replacement)

        msg_info['replacement'] = replacement
        if rule['message'] is not None:
            _show_msg(rule['message'], msg_info)
            rule_stats["errors"] += 1
    return rule_stats

def _show_msg(msg, info):
    pos = ' '*(info['column']) + '^'
    template = "{info[line_no]}:{info[column]}:"
    template = template +" {msg} :\n"
    template = template + " {info[line]}\n"
    template = template + "{pos}"

    show_msg = template.format(info=info, msg=msg, pos=pos)
    print(show_msg)
