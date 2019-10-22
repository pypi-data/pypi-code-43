def enot(p):
    return(not p)

def exist(conds):
    rslt = False
    for cond in conds:
        if(cond):
            return(True)
        else:
            pass
    return(rslt)


def eone(conds):
    rslt = (conds.count == 1)
    return(rslt)


def eall(conds):
    rslt = True
    for cond in conds:
        if(cond):
            pass
        else:
            return(False)
    return(rslt)





def pandq(p,q):
    return(p and q)

def porq(p,q):
    return(p or q)



def if_p_then_notq_else_q(p,q):
    rslt= (p and not(q)) or (not(p) and q)
    return(rslt)

def if_p_then_notq_else_tru(p,q):
    rslt= not(p and q)
    return(rslt)

def if_p_then_fls_else_notq(p,q):
    rslt= not(p or q)
    return(rslt)

def if_p_then_q_else_tru(p,q):
    rslt= not(p) or q
    return(rslt)

def if_q_then_p_else_tru(p,q):
    rslt= p or not(q)
    return(rslt)

def if_p_then_notq_else_fls(p,q):
    rslt= p and not(q)
    return(rslt)

def if_q_then_notp_else_fls(p,q):
    rslt= not(p) and q
    return(rslt)

def if_p_then_q_else_notq(p,q):
    rslt= (not(p) or q) and (p or not(q))
    return(rslt)

def if_p_then_q_else_fls(p,q):
    rslt= (p and q)
    return(rslt)

def if_q_then_p_else_fls(p,q):
    rslt= (p and q)
    return(rslt)

def if_p_then_tru_else_q(p,q):
    rslt= (p or q)
    return(rslt)

def if_q_then_tru_else_p(p,q):
    rslt= (p or q)
    return(rslt)

def if_notp_then_notq_else_tru(p,q):
    rslt= (p or not(q))
    return(rslt)

def if_notq_then_notp_else_tru(p,q):
    rslt= (q or not(p))
    return(rslt)

def if_p_then_tru_else_fls(p,q):
    rslt= p
    return(rslt)

def if_q_then_tru_else_fls(p,q):
    rslt= q
    return(rslt)

def if_p_then_q_else_q(p,q):
    rslt= q
    return(rslt)

def if_q_then_p_else_p(p,q):
    rslt=p
    return(rslt)

def if_p_then_notq_else_notq(p,q):
    rslt=not(q)
    return(rslt)

def if_q_then_notp_else_notp(p,q):
    rslt=not(p)
    return(rslt)

def if_p_then_fls_else_tru(p,q):
    rslt=not(p)
    return(rslt)

def if_q_then_fls_else_tru(p,q):
    rslt=not(q)
    return(rslt)

def if_p_then_fls_else_q(p,q):
    rslt= not(p) and q
    return(rslt)

def if_q_then_fls_else_p(p,q):
    rslt=p and not(q)
    return(rslt)

