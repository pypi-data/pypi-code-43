import re
from .lmnts import atomZlist, atomWeightlist


def get_z(atom='Fe'):
    return atomZlist[atom]


def get_wt(atom='Fe'):
    return atomWeightlist[atom]/12.0107*12


def formula_parser(formula):
    """
    Takes a string containing a brute formula, e.g. e.g. Sr0.85Pr0.15TiO3 or CaO.
    Returns a dictionary of atom labels and stoichiometric coefficients & formula weight.
    """
    stoi_dict = {}
    fw = 0.0   # formula weight
    formula.replace("""'""",'')
    formula.replace('''"''','')
    is_stoi = re.search(r'\.', formula)
    if is_stoi is None:
        mix = [a for a in re.split(r'([A-Z][a-z]*\d*)', formula) if a]
    else:
        mix = [a for a in re.split(r'([A-Z][a-z]*[\d\.\d+]*)', formula) if a]
    # mix looks like ['Ti3.2','Fe4','O7.12']
    for aok in mix: # separate 'Ti' (dump to var u) from '3.2' (dump to var v)
        if any([ch.isdigit() for ch in aok]) == True:  # if there is at least one number
            u, v, w = re.split(r'(\d.*)', aok)   #split string in u:before numeric(&point) and v:numeric&point; w must be there to collect a blank str.
            v = float(v)                         #make sure the coef is a float
            if u in stoi_dict:                   #if an element u is repeated in the formula
                stoi_dict['%s' %u] = stoi_dict['%s' %u]+v #: sum v to the old value
            else:                                 #otherwise create dict entry: elem name = number
                stoi_dict['%s' %u] = v               #case in which u occurs for the first time
            fw += get_wt(u)*v                  #atoms per formula times atomic weight
        elif any([ch.isdigit() for ch in aok]) == False:  #case in which v is not expressed in the formula, as in CaO
            u = aok; v = 1.0
            if u in stoi_dict:
                stoi_dict['%s' %u] = float(stoi_dict['%s' %u])+v 
            else:
                stoi_dict['%s' %u] = v
            fw += get_wt(u)*v
    return stoi_dict, fw