# Notatie
def SuperScript(number):
    number = str(number)
    return number.replace('0', '⁰').replace('1', '¹').replace('2', '²').replace('3', '³').replace('4', '⁴').replace('5', '⁵').replace('6', '⁶').replace('7', '⁷').replace('8', '⁸').replace('9', '⁹').replace('-', '⁻')


def sci_notation(number, num_significant, decimal=','):
    ret_string = "{0:.{1:d}e}".format(number, num_significant)
    a, b = ret_string.split("e")
    a = a.replace('.', decimal)
    if b == str('+00'): return a 
    else:
        b = int(b)
        return a + "·10" + notation.SuperScript(b)

# Formules
def ev_to_joule(ev):
    return ev*1.602*10**-19

def joule_to_ev(joule):
    return joule/(1.602*10**-19)

def exp(number):
    return 2.71828182845904523536028747135266249**number

def root(number, macht=2):
    return number**(1/macht)


class c: 
    '''Constanten die handig zijn bij natuurkundige berekeningen'''
    #Natuurconstante
    G = 6.67384*10**-11
    g = 9.81
    p_0 = 1.01325*10**5
    N_A = 6.02214129*10**23
    R = 8.3144621
    k_B = 1.3806488*10**-23
    sigma = 5.670373*10**-8
    k_W = 2.8977721*10**-3
    h = 6.62606957*10**-34
    c = 2.99792458*10**8
    epsilon = 8.854187817*10**-12
    f = 8.987551787*10**9
    mu_0 = 1.25664*10**-6
    e = 1.602176565*10**-19
    F = 9.64853365*10**4
    a_0 = 5.2917721092*10**-11
    R_H = 1.096775834*10**7
    
    #Massa's
    m_e = 9.10938*10**-31
    m_p = 1.67262*10**-27
    m_n = 1.67493*10**-27
    
    #Overig
    pi = 3.14159265358979323846264338327950288
