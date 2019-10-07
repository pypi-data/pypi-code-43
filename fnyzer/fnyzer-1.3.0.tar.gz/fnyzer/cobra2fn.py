# Transform a cobra model (https://opencobra.github.io/cobrapy/) into 
# a flexible net

def cobra2fn(comodel, knockouts = [], solver = 'cplex'):
    """
    Create and return a dictionary with flexible net format from cobra 
    model comodel.
    Parameters:
       comodel: cobra model
       knockouts: list of genes to knock out (the flux of the associated
                  reactions will be set to 0)
       solver: name of the solver to be used for optimization (at a later stage)
    """

    ## State of the genes. True: active, False: knocked out
    genestate = {gene.id:True for gene in comodel.genes}
    for gene in knockouts:
        genestate[gene] = False

    fnet = {} # The net will be stored here
    # FN parameters
    fnet['name'] = comodel.id
    fnet['solver'] = solver
    fnet['options'] = {
        'antype': 'cst',
        'writevars': {'l0': 'all'}
        }
    #fnet['actfplaces'] = 'all'
    #fnet['actavplaces'] = 'all'
    fnet['exftrans'] = 'all'
    fnet['exavtrans'] = 'all'
    
    # Places
    fnet['places'] = {}
    for meta in comodel.metabolites:
        fnet['places']['p_'+meta.id] = {
            'full_name': meta.name,
            'charge': meta.charge,
            'formula': meta.formula,
            'compartment': meta.compartment
            }
    
    # Transitions and event handlers
    fnet['trans'] = {}
    fnet['vhandlers'] = {}
    fnet['l0cons'] = []
    for reac in comodel.reactions:
        if reac.gene_reaction_rule == '': # Set rule to True if there is no rule
            reac.gene_reaction_rule = 'True'
        onreaction = eval(reac.gene_reaction_rule, genestate) # Is the reaction active?
        if reac.lower_bound >= 0: # Not reversible, forward reaction only
            fnet['trans']['t_'+reac.id+'_f'] = {
                'a0': 0.0,
                'full_name': reac.name+' (not reversible, only forward)' if reac.name != None else '(not reversible, only forward)',
                'subsystem': reac.subsystem,
                'lower_bound': reac.lower_bound,
                'upper_bound': reac.upper_bound,
                'gene_reaction_rule': reac.gene_reaction_rule
                }
            if onreaction: # If the reaction is active
                fnet['l0cons'].append("l0['t_"+reac.id+'_f'+"'] >= "+str(abs(reac.lower_bound)))
                fnet['l0cons'].append("l0['t_"+reac.id+'_f'+"'] <= "+str(abs(reac.upper_bound)))   
            else:
                fnet['l0cons'].append("l0['t_"+reac.id+'_f'+"'] <= 0")                        
            fnet['vhandlers']['v_'+reac.id+'_f'] = [{'v': ('t_'+reac.id+'_f','v_'+reac.id+'_f')}]
            ridx, pidx = 0, 0 # current reactant and product indices
            for meta in reac.metabolites:
                if reac.metabolites[meta] < 0: # reactant
                    nickn = 'r'+str(ridx) # nickname
                    fnet['vhandlers']['v_'+reac.id+'_f'][0][nickn] = ('p_'+meta.id,'v_'+reac.id+'_f')
                    fnet['vhandlers']['v_'+reac.id+'_f'].append(nickn+'== v*'+str(abs(reac.metabolites[meta])))
                    ridx = ridx + 1
                else: # product                
                    nickn = 'p'+str(pidx) # nickname
                    fnet['vhandlers']['v_'+reac.id+'_f'][0][nickn] = ('v_'+reac.id+'_f','p_'+meta.id)
                    fnet['vhandlers']['v_'+reac.id+'_f'].append(nickn+'== v*'+str(abs(reac.metabolites[meta])))
                    pidx = pidx + 1
        elif reac.upper_bound <= 0: # Not reversible, backward reaction only
            fnet['trans']['t_'+reac.id+'_b'] = {
                'a0': 0.0,
                'full_name': reac.name+' (not reversible, only backward)' if reac.name != None else '(not reversible, only backward)',
                'subsystem': reac.subsystem,
                'lower_bound': -reac.upper_bound,
                'upper_bound': -reac.lower_bound,
                'gene_reaction_rule': reac.gene_reaction_rule
                }
            if onreaction: # If the reaction is active
                fnet['l0cons'].append("l0['t_"+reac.id+'_b'+"'] >= "+str(-reac.upper_bound))
                fnet['l0cons'].append("l0['t_"+reac.id+'_b'+"'] <= "+str(-reac.lower_bound))   
            else:
                fnet['l0cons'].append("l0['t_"+reac.id+'_b'+"'] <= 0")                        
            fnet['vhandlers']['v_'+reac.id+'_b'] = [{'v': ('t_'+reac.id+'_b','v_'+reac.id+'_b')}]
            ridx, pidx = 0, 0 # current reactant and product indices
            for meta in reac.metabolites:
                if reac.metabolites[meta] > 0: # reactant
                    nickn = 'r'+str(ridx) # nickname
                    fnet['vhandlers']['v_'+reac.id+'_b'][0][nickn] = ('p_'+meta.id,'v_'+reac.id+'_b')
                    fnet['vhandlers']['v_'+reac.id+'_b'].append(nickn+'== v*'+str(abs(reac.metabolites[meta])))
                    ridx = ridx + 1
                else: # product                
                    nickn = 'p'+str(pidx) # nickname
                    fnet['vhandlers']['v_'+reac.id+'_b'][0][nickn] = ('v_'+reac.id+'_b','p_'+meta.id)
                    fnet['vhandlers']['v_'+reac.id+'_b'].append(nickn+'== v*'+str(abs(reac.metabolites[meta])))
                    pidx = pidx + 1
        else: # (reac.lower_bound < 0) and (reac.upper_bound > 0): # The reaction is considered reversible if its lower
                                                              # bound is negative and its upper bound is positive.
                                                              # Checking the value of reac.reversibility is
                                                              # not advisable as it can be False with
                                                              # upper bound equal to 0.
            # Unfold into forward and backward reactions
            # Forward
            fnet['trans']['t_'+reac.id+'_f'] = {
                'a0': 0.0,
                'full_name': reac.name+' (forward)' if reac.name != None else '(forward)',
                'subsystem': reac.subsystem,
                'lower_bound': 0.0,
                'upper_bound': reac.upper_bound,
                'gene_reaction_rule': reac.gene_reaction_rule
                }
            if onreaction: # If the reaction is active
                fnet['l0cons'].append("l0['t_"+reac.id+"_f'] <= "+str(abs(reac.upper_bound)))
            else:
                fnet['l0cons'].append("l0['t_"+reac.id+"_f'] <= 0")                        
            fnet['vhandlers']['v_'+reac.id+'_f'] = [{'v': ('t_'+reac.id+'_f','v_'+reac.id+'_f')}]
            ridx, pidx = 0, 0 # current reactant and product indices
            for meta in reac.metabolites:
                if reac.metabolites[meta] < 0: # reactant
                    nickn = 'r'+str(ridx) # nickname
                    fnet['vhandlers']['v_'+reac.id+'_f'][0][nickn] = ('p_'+meta.id,'v_'+reac.id+'_f')
                    fnet['vhandlers']['v_'+reac.id+'_f'].append(nickn+'== v*'+str(abs(reac.metabolites[meta])))
                    ridx = ridx + 1
                else: # product                
                    nickn = 'p'+str(pidx) # nickname
                    fnet['vhandlers']['v_'+reac.id+'_f'][0][nickn] = ('v_'+reac.id+'_f','p_'+meta.id)
                    fnet['vhandlers']['v_'+reac.id+'_f'].append(nickn+'== v*'+str(abs(reac.metabolites[meta])))
                    pidx = pidx + 1                
            # Backward
            fnet['trans']['t_'+reac.id+'_b'] = {
                'a0': 0.0,
                'full_name': reac.name+' (backward)' if reac.name != None else '(backward)',
                'subsystem': reac.subsystem,
                'lower_bound': 0.0,
                'upper_bound': -reac.lower_bound,
                'gene_reaction_rule': reac.gene_reaction_rule
                }
            if onreaction: # If the reaction is active
                fnet['l0cons'].append("l0['t_"+reac.id+"_b'] <= "+str(-reac.lower_bound))  
            else:
                fnet['l0cons'].append("l0['t_"+reac.id+"_b'] <= 0")                        
            fnet['vhandlers']['v_'+reac.id+'_b'] = [{'v': ('t_'+reac.id+'_b','v_'+reac.id+'_b')}]
            ridx, pidx = 0, 0 # current reactant and product indices
            for meta in reac.metabolites:
                if reac.metabolites[meta] > 0: # reactant
                    nickn = 'r'+str(ridx) # nickname
                    fnet['vhandlers']['v_'+reac.id+'_b'][0][nickn] = ('p_'+meta.id,'v_'+reac.id+'_b')
                    fnet['vhandlers']['v_'+reac.id+'_b'].append(nickn+'== v*'+str(abs(reac.metabolites[meta])))
                    ridx = ridx + 1
                else: # product                
                    nickn = 'p'+str(pidx) # nickname
                    fnet['vhandlers']['v_'+reac.id+'_b'][0][nickn] = ('v_'+reac.id+'_b','p_'+meta.id)
                    fnet['vhandlers']['v_'+reac.id+'_b'].append(nickn+'== v*'+str(abs(reac.metabolites[meta])))
                    pidx = pidx + 1                
                    
    return fnet

