# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from six.moves import range
from sage.misc.cachefunc import cached_function

import itertools
from copy import copy, deepcopy

from sage.rings.all import Integer, Rational, RealNumber, PolynomialRing, QQ, ZZ
from sage.groups.perm_gps.permgroup import PermutationGroup
from sage.matrix.constructor import matrix
from sage.matrix.special import block_matrix
from sage.modules.free_module_element import vector
from sage.combinat.all import Permutations, Subsets
from sage.functions.other import floor, ceil, binomial
from sage.arith.all import factorial, bernoulli, gcd, lcm
from sage.misc.misc_c import prod
from sage.graphs.graph import Graph
from sage.symbolic.ring import SR
import pickle

_sage_const_3 = Integer(3); _sage_const_2 = Integer(2); _sage_const_1 = Integer(1); _sage_const_0 = Integer(0); _sage_const_10 = Integer(10); _sage_const_5 = Integer(5); _sage_const_4 = Integer(4); _sage_const_11 = Integer(11); _sage_const_0p2 = RealNumber('0.2'); _sage_const_0p4 = RealNumber('0.4'); _sage_const_0p7 = RealNumber('0.7'); _sage_const_20 = Integer(20); _sage_const_19 = Integer(19)

from . import DR
#from . import double_ramification_cycle

# graphics:
from sage.repl.rich_output.pretty_print import show
from sage.plot.polygon import polygon2d
from sage.plot.text import text
from sage.plot.bezier_path import bezier_path
from sage.plot.line import line
from sage.plot.circle import circle

initialized = True
g=_sage_const_0 
n=_sage_const_3 

def reset_g_n(gloc, nloc):
    gloc = Integer(gloc)
    nloc = Integer(nloc)
    if gloc < 0 or nloc < 0:
        raise ValueError
    global g, n
    g = gloc
    n = nloc

Hdatabase={}

# stgraph is a class modelling stable graphs G
# all vertices and all legs are uniquely globally numbered by integers, vertices numbered by 1,2...,m
# G.genera = list of genera of m vertices
# G.legs = list of length m, where ith entry is set of legs attached to vertex i
# CONVENTION: usually legs are labelled 1,2,3,4,....
# G.edges = edges of G, given as list of ordered 2-tuples, sorted in ascending order by smallest element
# TODO: do I really need sorted in ascending order ...
#
# G.g() = total genus of G

#  Examples
#  --------
#  Creating a stgraph with two vertices of genera 3,5 joined 
#  by an edge with a self-loop at the genus 3 vertex.
#     sage: stgraph([3,5],[[1,3,5],[2]],[(1,2),(3,5)])
#     [3, 5] [[1, 3, 5], [2]] [(1, 2), (3, 5)]
     
from .stable_graph import StableGraph as stgraph, GraphIsom

# returns the trivial graph in genus g with n markings
def trivgraph(g,n):
  return stgraph([g],[list(range(_sage_const_1 ,n+_sage_const_1 ))],[])


# gives a list of dual graphs for \bar M_{g,n} of codimension r, i.e. with r edges
#TODO: Huge potential for optimization, at the moment consecutively degenerate and check for isomorphisms
def list_strata(g,n,r):
  if r==_sage_const_0 :
    return [stgraph([g],[list(range(_sage_const_1 ,n+_sage_const_1 ))],[])]
  Lold=list_strata(g,n,r-_sage_const_1 )
  Lnew=[]
  for G in Lold:
    for v in range(len(G.genera)):
      Lnew+=G.degenerations(v)
  # now Lnew contains a list of all possible degenerations of graphs G with r-1 edges
  # need to identify duplicates
  
  if Lnew==[]:
    return []
  
  Ldupfree=[Lnew[0]]
  count=_sage_const_1 
  # duplicate-free list of strata
  
  for i in range(_sage_const_1 ,len(Lnew)):
    newgraph=True
    for j in range(count):
      if Lnew[i].is_isomorphic(Ldupfree[j]):
        newgraph=False
        break    
    if newgraph:
      Ldupfree+=[Lnew[i]]
      count+=_sage_const_1 

  return Ldupfree      

# degeneration_graph computes a data structure containing all isomorphism classes of stable graphs of genus g with n markings 1,...,n and the information about one-edge degenerations between them as well as a lookup table for graph-invariants, to quickly identify the index of a given graph
# optional argument: rmax = maximal number of edges that should be computed (so rmax < 3*g-3+n means only a partial degeneration graph is computed - if function had been called with higher rmax before, a larger degeneration_graph will be returned
# the function will look for previous calls in the dictionary of cached_function and restart from there
# output = (deglist,invlist)
# deglist is a list [L0,L1,L2,...] where Lk is itself a list [G0,G1,G2,...] with all isomorphism classes of stable graphs having k edges
# the entries Gj have the form [stgraph Gr, (tuple of the half-edges of Gr), set of morphisms to L(j-1), set of morphisms from L(j+1)]
# a morphism A->B is of the form (DT,halfedgeimages), where 
#   * DT is the number of B in L(j-1) or of A in L(j+1)
#   * halfedgeimages is a tuple (of length #halfedges(B)) with entries 0,1,...,#halfedges(A)-1, where halfedgeimages[i]=j means halfedge number i of B corresponds to halfedge number j in A
# invlist is a list [I0,I1,I2,...] where Ik is a list [invariants,boundaries], where
#   * invariants is a list of all Gr.invariant() for Gr in Lk
#   * boundaries is a list [i0,i1,i2,...] of indices such that the Graphs in Lk with invariant number N (in invariants) are G(i(N)+1), ..., G(i(N+1))

@cached_function
def degeneration_graph(g,n,rmax=None):
  if rmax==None:
    rmax = _sage_const_3 *g-_sage_const_3 +n
  if rmax>_sage_const_3 *g-_sage_const_3 +n:
    rmax = _sage_const_3 *g-_sage_const_3 +n  
  
  # initialize deglist and invlist
  try:
    deglist, invlist = degeneration_graph.cached(g,n)
    r0 = _sage_const_3 *g-_sage_const_3 +n
  except KeyError:  
    for r0 in range(_sage_const_3 *g-_sage_const_3 +n,-_sage_const_2 ,-_sage_const_1 ):    
      try:
        deglist, invlist = degeneration_graph.cached(g,n,r0)
        break
      except KeyError:
        pass  
    
  if r0==-_sage_const_1 :  # function has not been called before
    deglist=[[[stgraph([g],[list(range(_sage_const_1 ,n+_sage_const_1 ))],[]), (), set(), set() ]]]
    invlist=[[[deglist[0][0][0].invariant()],[-_sage_const_1 ,_sage_const_0 ]]]
  

    
  for r in range(r0+_sage_const_1 ,rmax+_sage_const_1 ):
    deglist+=[[]]  # add empty list L(r)
    templist=[]
    
    # first we must degenerate all stgraphs in degree r-1 and record how the degeneration went
    for i in range(len(deglist[r-_sage_const_1 ])):
      Gr=deglist[r-_sage_const_1 ][i][0]
      deg_Gr=Gr.degenerations()
      for dGr in deg_Gr:
        # since all degenerations deg_Gr have the same list of edges as Gr with the new edge appended and since stgraph.halfedges() returns the half-edges in this order, half-edge alpha of Gr corresponds to half-edge alpha in deg_Gr
        lis=tuple(range(len(deglist[r-_sage_const_1 ][i][1])))
        templist+=[[dGr,dGr.halfedges(),set([(i,lis)]),set([])]]
    
    # now templist contains a temporary list of all possible degenerations of deglist[r-1]
    # we now proceed to consolidate this list to deglist[r], combining isomorphic entries    
    def inva(o):
      return o[0].invariant()
    templist.sort(key=inva)
    
    # first we reconstruct the blocks of entries having the same graph invariants
    current_invariant=None
    tempbdry=[]
    tempinv=[]
    count=_sage_const_0 
    for Gr in templist:
      inv=Gr[0].invariant()
      if inv != current_invariant:
        tempinv+=[inv]
        tempbdry+=[count-_sage_const_1 ]
        current_invariant=inv
      count+=_sage_const_1   
    tempbdry+=[len(templist)-_sage_const_1 ]
    
    # now go through blocks and check for actual isomorphisms
    count=_sage_const_0   # counts the number of isomorphism classes already added to deglist[r]
    
    invlist+=[[[],[]]]
    for i in range(len(tempinv)):
      # go through templist[tempbdry[i]+1], ..., templist[tempbdry[i+1]]
      isomcl=[]
      for j in range(tempbdry[i]+_sage_const_1 ,tempbdry[i+_sage_const_1 ]+_sage_const_1 ):
        Gr=templist[j][0]  # must check if stgraph Gr is isomorphic to any of the graphs in isomcl
        new_graph=True
        for k in range(len(isomcl)):
          Gr2=isomcl[k]
          ans, Iso = Gr.is_isomorphic(Gr2[0], certificate=True)
          if ans:
            new_graph=False
            dicl = Iso[1]
            # modify isomcl[k] to add new graph upstairs, and record this isomorphism in the data of this upstairs graph
            upstairs=list(templist[j][2])[0][0]   # number of graph upstairs
            # h runs through the half-edges of the graph upstairs, which are included via the same name in Gr, so dicl translates them to legs of Gr2
            # and we record the index of this image leg in the list of half-edges of Gr2
            lisnew=tuple((Gr2[1].index(dicl[h]) for h in deglist[r-_sage_const_1 ][upstairs][1])  )
            Gr2[2].add((upstairs, lisnew))
            deglist[r-_sage_const_1 ][upstairs][3].add((count+k,lisnew))            
            break
        if new_graph:
          isomcl+=[templist[j]]  
          # now also add the info upstairs
          upstairs=list(templist[j][2])[0][0] 
          lisnew=list(templist[j][2])[0][1] 
          deglist[r-_sage_const_1 ][upstairs][3].add((count+len(isomcl)-_sage_const_1 ,lisnew))   
      
      deglist[r]+=isomcl   
      invlist[r][0]+=[isomcl[0][0].invariant()]
      invlist[r][1]+=[count-_sage_const_1 ]
      
      count+=len(isomcl)
    
    invlist[r][1]+=[count-_sage_const_1 ]  
  
  # remove old entry from cache_function dict if more has been computed now
  if rmax > r0 and r0!=-_sage_const_1 :
    degeneration_graph.cache.pop(((g,n,r0),()))
  
  return (deglist,invlist)          

# finds Gr in the degeneration_graph of the corresponding (g,n), where markdic is a dictionary sending markings of Gr to 1,2,..,n
# returns a tuple (r,i,dicv,dicl), where
#   * the graph isomorphic to Gr is in degeneration_graph(g,n)[0][r][i][0]
#   * dicv, dicl are dictionaries giving the morphism of stgraphs from Gr to degeneration_graph(g,n)[0][r][i][0]
def deggrfind(Gr,markdic=None):
  #global Graph1
  #global Graph2
  #global Grdeggrfind
  #Grdeggrfind = deepcopy(Gr)
  g = Gr.g()
  n = len(Gr.list_markings())
  r = len(Gr.edges)
  
  if markdic != None:  
    Gr_rename=deepcopy(Gr)
    Gr_rename.rename_legs(markdic)
  else:
    markdic={i:i for i in range(_sage_const_1 ,n+_sage_const_1 )}
    Gr_rename=Gr
  Inv=Gr_rename.invariant()
  (deglist,invlist) = degeneration_graph(g,n,r)
   
  InvIndex=invlist[r][0].index(Inv)
  for i in range(invlist[r][1][InvIndex]+_sage_const_1 ,invlist[r][1][InvIndex+_sage_const_1 ]+_sage_const_1 ):
    #(Graph1,Graph2)= (Gr_rename,deglist[r][i][0])
    ans, Isom = Gr_rename.is_isomorphic(deglist[r][i][0], certificate=True)
    if ans:
      dicl={l:Isom[1][markdic[l]] for l in markdic}
      dicl.update({l:Isom[1][l] for l in Gr.halfedges()})
      return (r,i,Isom[0],dicl)
  print('Help, cannot find ' + repr(Gr))  
  print((g,n,r))
  print((Inv,list_strata(_sage_const_2 ,_sage_const_2 ,_sage_const_0 )[0].invariant()))


# returns the list of all A-structures on Gamma, for two stgraphs A,Gamma
# the output is a list [(dicv1,dicl1),(dicv2,dicl2),...], where 
#   * dicv are (surjective) dictionaries from the vertices of Gamma to the vertices of A
#   * dicl are (injective)  dictionaries from the legs of A to the legs of Gamma    
# optional input: identGamma, identA of the form  (rA,iA,dicvA,diclA) are result of deggrfind(A,markdic)
# TODO: for now assume that markings are 1,2,...,n 
def Astructures(Gamma,A,identGamma=None,identA=None):
  if len(A.edges)>len(Gamma.edges):
    return []
  g = Gamma.g()
  mark = Gamma.list_markings()
  n=len(mark)
  
  if g != A.g():
    print('Error, Astructuring graphs of different genera')
    print(Gamma)
    print(A)
    raise ValueError('A very specific bad thing happened')
    return []
  if set(mark) != set(A.list_markings()):
    print('Error, Astructuring graphs with different markings')
    return []
  markdic={mark[i-_sage_const_1 ]:i for i in range(_sage_const_1 ,n+_sage_const_1 )}
  
  
  # first identify A and Gamma inside the degeneration graph  
  (deglist,invlist) = degeneration_graph(g,n,len(Gamma.edges))
  
  if identA==None:
    (rA,iA,dicvA,diclA)=deggrfind(A,markdic)
  else:
    (rA,iA,dicvA,diclA)=identA
  if identGamma==None:  
    (rG,iG,dicvG,diclG)=deggrfind(Gamma,markdic)
  else:
    (rG,iG,dicvG,diclG)=identGamma
  
  # go through the graph in deglist, starting from Gamma going upwards the necessary amount of steps and collect all morphisms in a set
  # a morphism is encoded by a tuple (j,(i0,i1,...,im)), where j is the number of the current target of the morphism (in the list deglist[r])
  # and i0,i1,..,im give the numbers of the half-edges in Gamma, to which the m+1 half-edges of the target correspond
  
  morphisms=set([(iG,tuple(range(len(deglist[rG][iG][1]))))])  # start with the identity on Gamma
  
  
  for r in range(rG,rA,-_sage_const_1 ):
    new_morphisms=set()
    for mor in morphisms:
      # add to new_morphisms all compositions of mor with a morphism starting at the target of mor
      for (tar,psi) in deglist[r][mor[0]][2]:
        composition=tuple((mor[1][j] for j in psi))
        new_morphisms.add((tar,composition))
    morphisms=new_morphisms    
  
  # now pick out the morphisms actually landing in position (rA,iA)
  new_morphisms = set([mor for mor in morphisms if mor[0]==iA])
  morphisms=new_morphisms
  
  # at the end we have to precompose with the automorphisms of Gamma
  Auto = GraphIsom(deglist[rG][iG][0],deglist[rG][iG][0])
  new_morphisms=set()
  for (Autov,Autol) in Auto:
    for mor in morphisms:
      # now composition is no longer of the format above
      # instead composition[i] is the label of the half-edge in deglist[rG][iG][0] to which half-edge number i in the target corresponds
      composition=tuple((Autol[deglist[rG][iG][1][j]] for j in mor[1]))
      new_morphisms.add((mor[0],composition))
  morphisms=new_morphisms
  
  
  # now we must translate everything back to the original graphs Gamma,A and their labels, 
  # also reconstructing the vertex-action from the half-edge action 
  finalmorphisms=[]
  dicmarkings={h:h for h in mark}
  Ahalfedges=A.halfedges()
  Ghalfedges=Gamma.halfedges()
  dicAtild={deglist[rA][iA][1][i]:i for i in range(len(deglist[rA][iA][1]))}
  diclGinverse={diclG[h]:h for h in Gamma.halfedges()}
  
     
  for (targ,mor) in morphisms:
    dicl={ h: diclGinverse[mor[dicAtild[diclA[h]]]] for h in Ahalfedges}  # final dictionary for the half-edges
    dicl.update(dicmarkings)
    
    #now reconstruct dicv from this
    if len(A.genera)==_sage_const_1 :
      dicv={ver:_sage_const_0  for ver in range(len(Gamma.genera))}
    else:  
      # Now we pay the price for not recording the morphisms on the vertices before
      # we need to reconstruct it by the known morphisms of half-edges by determining the connected components of the complement of beta(H_A)
      # TODO: do we want to avoid this reconstruction by more bookkeeping?
      
      dicv={Gamma.vertex(dicl[h]) : A.vertex(h) for h in dicl}
      remaining_vertices=set(range(len(Gamma.genera)))-set(dicv)
      remaining_edges=set([e for e in Gamma.edges if e[0] not in dicl.values()])
      current_vertices=set(dicv)
      
      while remaining_vertices!=set():
        newcurrent_vertices=set()
        for e in deepcopy(remaining_edges):
          if Gamma.vertex(e[0]) in current_vertices:
            vnew=Gamma.vertex(e[1])
            remaining_edges.remove(e)
            # if vnew is in current vertices, we don't have to do anything (already know it)
            # otherwise it must be a new vertex (cannot reach old vertex past the front of current vertices)
            if vnew not in current_vertices:  
              dicv[vnew]=dicv[Gamma.vertex(e[0])]
              remaining_vertices.discard(vnew)
              newcurrent_vertices.add(vnew)
            continue
          if Gamma.vertex(e[1]) in current_vertices:
            vnew=Gamma.vertex(e[0])
            remaining_edges.remove(e)
            # if vnew is in current vertices, we don't have to do anything (already know it)
            # otherwise it must be a new vertex (cannot reach old vertex past the front of current vertices)
            if vnew not in current_vertices:  
              dicv[vnew]=dicv[Gamma.vertex(e[1])]
              remaining_vertices.discard(vnew)
              newcurrent_vertices.add(vnew)  
        current_vertices=newcurrent_vertices
    # now dicv and dicl are done, so they are added to the list of known A-structures
    finalmorphisms+=[(dicv,dicl)]
  return finalmorphisms                        
              

# find a list commdeg of generic (G1,G2)-stgraphs G3
# Elements of this list will have the form (G3,vdict1,ldict1,vdict2,ldict2), where
#   * G3 is a stgraph 
#   * vdict1, vdict2 are the vertex-maps from vertices of G3 to G1 and G2
#   * ldict1, ldict2 are the leg-maps from legs of G1 and G2 to G3    
# modiso = True means we give a list of generic (G1,G2)-stgraphs G3 up to isomorphisms of G3
# if rename=True, the operation will also work if the markings of G1,G2 are not labelled 1,2,...,n; since this involves more bookkeeping, rename=False should run slightly faster
def common_degenerations(G1,G2,modiso=False,rename=False):
  #TODO: fancy graph-theoretic implementation in case that G1 has a single edge?
  
  # almost brute force implementation below
  g=G1.g()
  mkings=G1.list_markings()
  n=len(mkings)
  
  
  # for convenience, we want r1 <= r2
  switched = False
  if len(G1.edges)>len(G2.edges):
    temp=G1
    G1=G2
    G2=temp
    switched = True

  if rename:
    markdic={mkings[i]:i+_sage_const_1  for i in range(n)}
    renamedicl1={l:l+n+_sage_const_1  for l in G1.leglist()}
    renamedicl2={l:l+n+_sage_const_1  for l in G2.leglist()}
    renamedicl1.update(markdic)
    renamedicl2.update(markdic)
    
    G1=deepcopy(G1)
    G2=deepcopy(G2)
    G1.rename_legs(renamedicl1)
    G2.rename_legs(renamedicl2)
    

  (r1,i1,dicv1,dicl1)=deggrfind(G1)
  (r2,i2,dicv2,dicl2)=deggrfind(G2)
  
  (deglist,invlist)=degeneration_graph(g,n,r1+r2)
  
  commdeg=[]
  
  descendants1=set([i1])
  for r in range(r1+_sage_const_1 ,r2+_sage_const_1 ):
    descendants1=set([d[0] for i in descendants1 for d in deglist[r-_sage_const_1 ][i][3] ])
    
  descendants2=set([i2])
  
  
  for r in range(r2,r1+r2+_sage_const_1 ):
    # look for intersection of descendants1, descendants2 and find generic (G1,G2)-struct  
    for i in descendants1.intersection(descendants2):
      Gamma=deglist[r][i][0]
      Gammafind=(r,i,{j:j for j in range(len(Gamma.genera))}, {l:l for l in Gamma.leglist()})
      G1structures=Astructures(Gamma,G1,identGamma=Gammafind,identA=(r1,i1,dicv1,dicl1))
      G2structures=Astructures(Gamma,G2,identGamma=Gammafind,identA=(r2,i2,dicv2,dicl2))
      
      if modiso==True:
        AutGamma=GraphIsom(Gamma,Gamma)
        AutGammatild=[(dicv,{dicl[l]:l for l in dicl}) for (dicv,dicl) in AutGamma]
      tempdeg=[]  
      
      # now need to identify the generic G1,G2-structures
      numlegs=len(Gamma.leglist())
      for (dv1,dl1) in G1structures:
        for (dv2,dl2) in G2structures:
          numcoveredlegs=len(set(list(dl1.values())+list(dl2.values())))
          if numcoveredlegs==numlegs:
            if switched:
              if rename:
                tempdeg.append((Gamma,dv2,{l:dl2[renamedicl2[l]] for l in renamedicl2},dv1,{l:dl1[renamedicl1[l]] for l in renamedicl1}))
              else:
                tempdeg.append((Gamma,dv2,dl2,dv1,dl1))
            else:
              if rename:
                tempdeg.append((Gamma,dv1,{l:dl1[renamedicl1[l]] for l in renamedicl1},dv2,{l:dl2[renamedicl2[l]] for l in renamedicl2})) 
              else:
                tempdeg.append((Gamma,dv1,dl1,dv2,dl2)) 
              
      
      if modiso==True:        
        # eliminate superfluous isomorphic elements from tempdeg
        while tempdeg!=[]:
          (Gamma,dv1,dl1,dv2,dl2)=tempdeg.pop(_sage_const_0 )
          commdeg.append((Gamma,dv1,dl1,dv2,dl2))
          for (dicv,dicltild) in AutGammatild:
            try:
              tempdeg.remove((Gamma,{v: dv1[dicv[v]] for v in dicv},{l: dicltild[dl1[l]] for l in dl1},{v: dv2[dicv[v]] for v in dicv},{l: dicltild[dl2[l]] for l in dl2}))
            except:
              pass  
      else:
        commdeg+=tempdeg  
    
    # (except in last step) compute new descendants
    if r<r1+r2:
      descendants1=set([d[0] for i in descendants1 for d in deglist[r][i][3] ])
      descendants2=set([d[0] for i in descendants2 for d in deglist[r][i][3] ])
  
  return commdeg  
    

# Gstgraph is a class modelling stable graphs Gamma with action of a group G and character data at legs
# 
# Gamma.G = finite group acting on Gamma
# Gamma.gamma = underlying stable graph gamma of type stgraph
# Gamma.vertact and G.legact = dictionary, assigning to tuples (g,x) of g in G and x a vertex/leg a new vertex/leg
# Gamma.character = dictionary, assigning to leg l a tuple (h,e,k) of 
#   * a generator h in G of the stabilizer of l
#   * the order e of the stabilizer
#   * an integer 0<=k<e such that h acts on the tangent space of the curve at the leg l by exp(2 pi i/e * k)

class Gstgraph:
  def __init__(self,G,gamma,vertact,legact,character,hdata=None):
    self.G=G
    self.gamma=gamma
    self.vertact=vertact
    self.legact=legact
    self.character=character
    if hdata==None:
      self.hdata=self.hurwitz_data()
    else:
      self.hdata=hdata

  def __repr__(self):
    return repr(self.gamma)
  
  def __deepcopy__(self,memo):
    return Gstgraph(self.G,deepcopy(self.gamma),deepcopy(self.vertact),deepcopy(self.legact),deepcopy(self.character),hdata=deepcopy(self.hdata))  
  
  # returns dimension of moduli space at vertex v; if v==None, return dimension of entire stratum for self
  def dim(self,v=None):  
    if v==None:
      return self.quotient_graph().dim()
    #TODO: optimization potential
    return self.extract_vertex(v).dim()  

  # renames legs according to dictionary di
  # TODO: no check that this renaming is legal, i.e. produces well-defined graph
  def rename_legs(self,di):
    self.gamma.rename_legs(di)
    temp_legact={}
    temp_character={}
    for k in self.legact:
      # the operation temp_legact[(k[0],k[1])]=self.legact[k] would produce copy of self.legact, di.get replaces legs by new name, if applicable, and leaves leg invariant otherwise
      temp_legact[(k[0],di.get(k[1],k[1]))]=di.get(self.legact[k],self.legact[k])
    for k in self.character:
      temp_character[di.get(k,k)]=self.character[k]
    
  
  # returns the stabilizer group of vertex i
  def vstabilizer(self,i):
    gen=[]
    for g in self.G:
      if self.vertact[(g,i)]==i:
        gen+=[g]
    try:
      return self.G.ambient_group().subgroup(gen)
    except AttributeError:  
      return self.G.subgroup(gen)
  
  # returns the stabilizer group of leg j
  def lstabilizer(self,j):      
    try:
      return self.G.ambient_group().subgroup([self.character[j][0]])
    except AttributeError:  
      return self.G.subgroup([self.character[j][0]])
    
  
  # converts self into a prodHclass (with gamma0 being the corresponding trivial graph)
  def to_prodHclass(self):  
    return prodHclass(stgraph([self.gamma.g()],[list(self.gamma.list_markings())],[]),[self.to_decHstratum()])
  
  # converts self into a decHstratum (with gamma0 being the corresponding trivial graph)
  def to_decHstratum(self):
    dicv={}
    dicvinv={}
    dicl={}
    quotgr=self.quotient_graph(dicv, dicvinv, dicl)  
    
    spaces={v: (self.gamma.genera[dicvinv[v]], HurwitzData(self.vstabilizer(dicvinv[v]),[self.character[l] for l in quotgr.legs[v]])) for v in range(len(quotgr.genera))}
    
    masterdicl={}
    
    
    
    for v in range(len(quotgr.genera)):
      n=_sage_const_1 
      gord=spaces[v][1].G.order()
      tGraph=trivGgraph(*spaces[v])
      vinv=dicvinv[v]
      
      # for l in quotgr.legs[v] find one leg l' in the orbit of l which belongs to vinv
      legreps=[]
      for l in quotgr.legs[v]:
        for g in self.G:
          if self.legact[(g,l)] in self.gamma.legs[vinv]:
            legreps.append(self.legact[(g,l)])
            break
      
      # make a list quotrep of representatives of self.G / spaces[v][1].G (quotient by Stab(vinv))
      (quotrep,di)=rightcosetaction(self.G,spaces[v][1].G)      
      
      for l in legreps:
        for g in spaces[v][1].G:
          for gprime in quotrep:
            masterdicl[ self.legact[(gprime*g,l)] ]  = tGraph.legact[(g,n)]
        n+=floor(QQ(gord)/self.character[l][1])
      
    
    vertdata=[]
    for w in range(len(self.gamma.genera)):
      a=dicv[w]
      
      wdicl={l:masterdicl[l] for l in self.gamma.legs[w]}
      
      vertdata.append([a,wdicl])
    
    return decHstratum(deepcopy(self.gamma),spaces,vertdata)
  
  
  # takes vertex v_i of the stable graph and returns a one-vertex Gstgraph with group G_{v_i} and all the legs and self-loops attached to v_i
  def extract_vertex(self,i):  
    G_new=self.vstabilizer(i)
    lgs=deepcopy(self.gamma.legs[i])  # takes list of legs attached to i
    egs=self.gamma.edges_between(i,i)
    gamma_new=stgraph([self.gamma.genera[i]],[lgs],egs)
    
    vertact_new={}
    for g in G_new:
      vertact_new[(g,_sage_const_0 )]=_sage_const_0 
    
    legact_new={}
    for g in G_new:
      for j in lgs:
        legact_new[(g,j)]=self.legact[(g,j)]
    
    character_new={}    
    for j in lgs:
      character_new[j]=deepcopy(self.character[j])
      
    return Gstgraph(G_new,gamma_new,vertact_new,legact_new,character_new)  
  
  # glues the Gstgraph Gr (with group H) at the vertex i of a Gstgraph self 
  # and performs this operation equivariantly under the G-action on self
  # all legs at the elements of the orbit of i are not renamed and the G-action and character on them is not changed
  # optional arguments: if divGr/dil are given they are supposed to be a dictionary, which will be cleared and updated with the renaming-convention to pass from leg/vertex-names in Gr to leg/vertex-names in the glued graph (at former vertex i)
  # similarly, divs will be a dictionary assigning vertex numbers in the old self (not in the orbit of i) the corresponding number in the new self  
  # necessary conditions: 
  #   * the stabilizer of vertex i in self = H
  #   * every leg of i is also a leg in Gr
  # note that legs of Gr which belong to an edge in Gr are not identified with legs of self, even if they have the same name
  def equivariant_glue_vertex(self,i,Gr,divGr={},divs={},dil={}):
    divGr.clear()
    divs.clear()
    dil.clear()    
    
    for j in range(len(self.gamma.genera)):
      divs[j]=j
      
    G=self.G
    H=Gr.G
    
    # the orbit of vertex i is given by gH*i for g in L
    (L,di)=rightcosetaction(G,H)
    oldvertno=len(self.gamma.genera)-len(L)  # number of old vertices that will remain in end
    
    # first we rename every leg in Gr that is not a leg of i such that the new leg-names do not appear in self
    Gr_mod=deepcopy(Gr)
    m=max(self.gamma.maxleg, Gr.gamma.maxleg)
    
    a=[]
    for l in Gr.gamma.legs:
      a+=l
    a=set(a)  # legs of Gr
    b=set(self.gamma.legs[i]) # legs of self at vertex i
    e=a-b    # contains the set of legs of Gr that are not legs of vertex i
    augment_dic={}
    for l in e:
      m+=_sage_const_1 
      augment_dic[l]=m
    
    Gr_mod.rename_legs(augment_dic) 
    
    # collects the dictionaries translating legs in Gr_mod not belonging to vertex i to legs in the glued graph at elements g in L 
    legdiclist={}  
    
    # records orbit of i under elements of L
    orbi={}
    oldlegsi=self.gamma.legs[i]
    
    # go through the orbit of i
    for g in L:
      orbi[g]=self.vertact[(g,i)]
      # create a translated copy of Gr using the information of the G-action on self
      Gr_transl=deepcopy(Gr_mod)
      transl_dic={l:self.legact[(g,l)] for l in oldlegsi}
      Gr_transl.rename_legs(transl_dic)
      
      # glue G_transl to vertex g*i of self (use divs to account for deletions in meantime) and remember how internal edges are relabelled
      divGr_temp={}
      divs_temp={}
      dil_temp={}
      self.gamma.glue_vertex(divs[self.vertact[(g,i)]], Gr_transl.gamma, divGr=divGr_temp, divs=divs_temp, dil=dil_temp)
      
      # update various dictionaries now
      divs.pop(self.vertact[(g,i)])  # no longer needed
      for j in divs:
        divs[j]=divs_temp[divs[j]]
      legdiclist.update({(g,j):dil_temp[j] for j in dil_temp})  
    
    # adjust vertact
    # ERROR here, from renaming vetices -> rather use vertact_reconstruct()
#    for g in L:  
#      for h in G:
#        self.vertact.pop((h,orbi[g]))  # remove action of h on g*i
#
#    
#    for g1 in range(len(L)):
#      for g2 in range(len(L)):    
#        for h in H:
#          for j in range(len(Gr.gamma.genera)):
#            # record where vertex number j in Gr(translated by g1) goes under g2*h
#            self.vertact[(L[g2]*h,oldvertno+g1*len(Gr.gamma.genera)+j)]=oldvertno+di[(L[g2]*h,g1)]*len(Gr.gamma.genera)+j
    
    # adjust legact and character
    for j in e:
      for g1 in range(len(L)):
        # we are adjusting here the data for the leg corresponding to j in Gr that was glued to vertex g1*i
        for g2 in range(len(L)):
          for h in H:
            # the element g2*h*(g1)**{-1} acts on g1*i resulting in g2*h*i
            # for g1 fixed, the expression g2*h*(g1)^{-1} runs through the elements of G
            self.legact[(L[g2]*h*L[g1].inverse(),legdiclist[(L[g1],augment_dic[j])])]=legdiclist[(L[g2],augment_dic[Gr.legact[(h,j)]])]
        # character given by conjugation
        self.character[legdiclist[(L[g1],augment_dic[j])]]=(L[g1]*Gr.character[j][0]*L[g1].inverse(),Gr.character[j][1],Gr.character[j][2])
    
    self.vertact_reconstruct()
    
    dil.update({j:legdiclist[(L[0],augment_dic[j])] for j in e})    # here we assume that L[0]=id_G
    divGr.update({j:oldvertno+j for j in range(len(Gr.gamma.genera))})  
  
  # computes the quotient graph of self under the group action
  # dicv, dicl are dictionaries that record the quotient map of vertices and legs
  # dicvinv is a dictionary giving some section of dicv (going from vertices of quotient to vertices of self)
  def quotient_graph(self, dicv={}, dicvinv={}, dicl={}):
    dicv.clear()
    dicvinv.clear()
    dicl.clear()
    
    vertlist=list(range(len(self.gamma.genera)))
    leglist=[]
    for v in vertlist:
      leglist+=self.gamma.legs[v]
    
    countv=_sage_const_0 
    # compute orbits of G-action
    for v in deepcopy(vertlist):
      if v in vertlist:  # has not yet been part of orbit of previous point
        dicvinv[countv]=v
        for g in self.G:
          if self.vertact[(g,v)] in vertlist:
            dicv[self.vertact[(g,v)]]=countv
            vertlist.remove(self.vertact[(g,v)])
        countv+=_sage_const_1 

    for l in deepcopy(leglist):
      if l in leglist:  # has not yet been part of orbit of previous point
        for g in self.G:
          if self.legact[(g,l)] in leglist:
            dicl[self.legact[(g,l)]]=l  # note that leg-names in quotient graph equal the name of one preimage in self
            leglist.remove(self.legact[(g,l)])
    
    # create new stgraph with vertices/legs given by values of dicv, dicl   
    quot_leg=[[] for j in range(countv)]  # list of legs of quotient
    legset=set(dicl.values())
    for l in legset:
      quot_leg[dicv[self.gamma.vertex(l)]]+=[l]
    
    quot_genera=[]
    for v in range(countv):
      Gv=self.vstabilizer(dicvinv[v]).order()
      b=sum([_sage_const_1 -QQ(_sage_const_1 )/(self.character[l][1]) for l in quot_leg[v] ])  # self.character[l][1] = e = order of Stab_l
      # genus of quotient vertex by Riemann-Hurwitz formula, floor to achieve integer (should not round anything)
      quot_genera+=[floor(((_sage_const_2 *self.gamma.genera[dicvinv[v]]-_sage_const_2 )/QQ(Gv)+_sage_const_2 -b)/QQ(_sage_const_2 ))]  
    
    quot_edges=[]
    for e in self.gamma.edges:
      if e[0] in legset:
        quot_edges+=[(e[0],dicl[e[1]])]
    
    quot_graph=stgraph(quot_genera,quot_leg, quot_edges)
    quot_graph.tidy_up()
    
    return quot_graph
  
  # returns Hurwitz data corresponding to the Hurwitz space in which self is a boundary stratum
  # HOWEVER: since names of legs are not necessarily canonical, there is no guarantee that they will be compatible
  # i.e. self is not necessarily a degeneration of trivGgraph(g,hurwitz_data(self))
  def hurwitz_data(self):
    quotgr=self.quotient_graph()
    marks=list(quotgr.list_markings() )
    marks.sort()
    return HurwitzData(self.G,[self.character[l] for l in marks])
  
  # gives the degree of the delta-map from the Hurwitz space parametrizing the curve placed on vertex v to the corresponding stable-maps space
  # currently, if self has more than one vertex, extract v and call procedure again; if self has exactly one vertex, compute
  # TODO: currently ONLY works for cyclic groups G
  def delta_degree(self,v):
    if len(self.gamma.genera)>_sage_const_1 :
      return self.extract_vertex(v).delta_degree(_sage_const_0 )
    quotgr=self.quotient_graph()
    gprime=quotgr.genera[0]
    n=self.G.order()
    
    # compute number of homomorphisms of pi_1(punctured base curve) to G giving correct Hurwitz datum by inclusion-exclusion type formula
    sigmagcd=ceil(QQ(n)/lcm([self.character[l][1] for l in quotgr.legs[0]]))
    primfac=set(sigmagcd.prime_factors())
    numhom=_sage_const_0 
    for S in Subsets(primfac):
      numhom+=(-_sage_const_1 )**len(S)*(QQ(n)/prod(S))**(_sage_const_2 *gprime)    
    
    return numhom*prod([QQ(n)/self.character[l][1] for l in quotgr.legs[0]])/QQ(n)  #TODO: why not divide by gcd([self.character[l][1] for l in quotgr.legs[0]]) instead???
  
  # reconstructs action of G on vertices from action on legs. Always possible for connected stable graphs
  def vertact_reconstruct(self):
    if len(self.gamma.genera)==_sage_const_1 :
      # only one vertex means trivial action
      self.vertact={(g,_sage_const_0 ):_sage_const_0  for g in self.G}
    else:  
      self.vertact={(g,v):self.gamma.vertex(self.legact[(g,self.gamma.legs[v][0])]) for g in self.G for v in range(len(self.gamma.genera))}  
  
  
  
  # returns a list of all possible codimension 1 degenerations of the Gstgraph self occuring at the vertex v (and the elements of the orbit of v under G
  # for this, v is extracted and seen as a Gstgraph with its own stabilizer group as symmetries and then split up according to the classification of boundary divisors in Hurwitz stacks. Then all possible degenerations of v are glued back in equivariantly to the original graph
  # NOTE: we do not guarantee that (by global symmetries of the graph) all these degenerations are nonisomorphic
  # TODO: Guarantee that for codim 0 to codim 1 all boundary components are only listed exactly once?
  def degenerations(self,v):
    # for more than one vertex, extract v and proceed as described above
    if len(self.gamma.genera)>_sage_const_1 :
      v0=self.extract_vertex(v)
      L=v0.degenerations(_sage_const_0 )
      M=[deepcopy(self) for j in range(len(L))]
      for j in range(len(L)):
        M[j].equivariant_glue_vertex(v,L[j])
      return M
    if len(self.gamma.genera)==_sage_const_1 :    
      dicv={}
      dicvinv={}
      dicl={}
      quot_Graph=self.quotient_graph(dicv=dicv, dicvinv=dicvinv, dicl=dicl)
      
      quot_degen=quot_Graph.degenerations(_sage_const_0 )
      
      degen=[]  #list of degenerations
      
      if self.G.is_cyclic():
        # first create dictionaries GtoNum, NumtoG translating elements of G to numbers 0,1, ..., G.order()-1
        G=self.G
        n=G.order()
        
        
        # cumbersome method to obtain some generator. since G.gens() is not guaranteed to be minimal, go through and check order
        Ggenerators=G.gens()
        for ge in Ggenerators:
          if ge.order()==n:
            sigma=ge
            break
        
        # now sigma is fixed generator of G, want to have dictionaries such that sigma <-> 1, sigma**2 <-> 2, ..., sigma**n <-> 0
        GtoNum={}
        NumtoG={}
        mu=sigma
        
        for j in range(_sage_const_1 ,n+_sage_const_1 ):
          GtoNum[mu]=j % n
          NumtoG[j % n]=mu
          mu=mu*sigma
        
        
        # extract data of e_alpha, k_alpha, nu_alpha, where alpha runs through legs of dege
        e={}
        k={}
        nu={}
        
                
        for dege in quot_degen:
          # all legs in dege come from legs of self, except the one added by the degeneration, which is last in the list dege.edges
          for alpha in (set(dege.leglist())-set(dege.edges[len(dege.edges)-_sage_const_1 ])):  
            e[alpha]=self.character[alpha][1]
            r=floor(GtoNum[self.character[alpha][0]]*e[alpha]/QQ(n))
            k[alpha]=(self.character[alpha][2]*r.inverse_mod(e[alpha]))% e[alpha]
            nu[alpha]=k[alpha].inverse_mod(e[alpha])  # case e[alpha]=1 works, produces nu[alpha]=0
                  
          if len(dege.genera)==_sage_const_2 :  # case of separating edge
            I1=deepcopy(dege.legs[0])
            I1.remove(dege.edges[len(dege.edges)-_sage_const_1 ][0])
            I2=deepcopy(dege.legs[1])
            I2.remove(dege.edges[len(dege.edges)-_sage_const_1 ][1])
            I=I1+I2
            
            
            n1_min=lcm([e[alpha] for alpha in I1])
            n2_min=lcm([e[alpha] for alpha in I2])
                        
            
            #TODO: following for-loop has great optimization potential, but current form should be sufficient for now
            for n1_add in range(_sage_const_1 ,floor(QQ(n)/n1_min +_sage_const_1) ):
              for n2_add in range(_sage_const_1 ,floor(QQ(n)/n2_min+_sage_const_1) ):
                n1=n1_add*n1_min  # nj is the order of the stabilizer of the preimage of vertex j-1 in dege
                n2=n2_add*n2_min
                if n1.divides(n) and n2.divides(n) and lcm(n1,n2)==n:  # lcm condition from connectedness of final graph
                  # we must make sure that the order e of the stabilizer of the preimage of the separating edge and the 
                  # corresponding characters (described by k1,k2) at the legs produce nonempty Hurwitz spaces
                  # this amounts to a congruence relation mod n1, n2, which can be explicitly solved
                  A1=-floor(sum([QQ(n1)/e[alpha]*nu[alpha] for alpha in I1]))
                  e_new=floor(QQ(n1)/gcd(n1,A1))
                  nu1=floor(QQ(A1%n1)/(QQ(n1)/e_new))
                  nu2=e_new-nu1
                  k1=nu1.inverse_mod(e_new)
                  k2=nu2.inverse_mod(e_new)
                  
                  # now we list all ways to distribute the markings, avoiding duplicates by symmetries
                  I1_temp=deepcopy(I1)
                  I2_temp=deepcopy(I2)
                  possi={}  #dictionary associating to a leg l in I the possible positions of l (from 0 to n/n1-1 if l in I1, ...)
                  
                  if len(I1)>_sage_const_0 :
                    possi[I1[0]]=[0]  # use G-action to move marking I1[0] to zeroth vertex on the left
                    I1_temp.pop(_sage_const_0 )
                    if len(I2)>_sage_const_0 : # if there is one more leg on the other vertex, use stabilizer of zeroth left vertex to move 
                      possi[I2[0]]=list(range(gcd(n1,QQ(n)/n2)))
                      I2_temp.pop(_sage_const_0 )
                  else:
                    if len(I2)>_sage_const_0 :
                      possi[I2[0]]=[0]
                      I2_temp.pop(_sage_const_0 )
                  for i in I1_temp:
                    possi[i]=list(range(QQ(n)/n1))    
                  for i in I2_temp:
                    possi[i]=list(range(QQ(n)/n2))
                  
                  
                  # mark_dist is a list of the form [(v1,v2,...), ...] where leg I[0] goes to vertex number v1 in its orbit, ....
                  mark_dist=itertools.product(*[possi[j] for j in I]) 
                  
                  # now all choices are made, and we construct the degenerated graph, to add it to degen
                  # first: use Riemann-Hurwitz to compute the genera of the vertices above 0,1
                  g1=floor((n1*(_sage_const_2 *dege.genera[0]-_sage_const_2 )+n1*(sum([_sage_const_1 -QQ(_sage_const_1 )/e[alpha] for alpha in I1])+_sage_const_1 -QQ(_sage_const_1 )/e_new))/QQ(_sage_const_2 )+_sage_const_1  )
                  g2=floor((n2*(_sage_const_2 *dege.genera[1]-_sage_const_2 )+n2*(sum([_sage_const_1 -QQ(_sage_const_1 )/e[alpha] for alpha in I2])+_sage_const_1 -QQ(_sage_const_1 )/e_new))/QQ(_sage_const_2 )+_sage_const_1  )
                  
                  # nonemptyness condition #TODO: is this the only thing you need to require?
                  if g1<_sage_const_0  or g2<_sage_const_0 :
                    continue
                  
                  new_genera=[g1 for j in range(QQ(n)/n1)]+[g2 for j in range(QQ(n)/n2)]
                  new_legs=[[] for j in range(QQ(n)/n1+QQ(n)/n2)]
                  new_legact=deepcopy(self.legact)
                  new_edges=deepcopy(self.gamma.edges)
                  new_character=deepcopy(self.character)
                  
                  # now go through the orbit of the edge and adjust all necessary data
                  m0=self.gamma.maxleg+_sage_const_1 
                  m=self.gamma.maxleg+_sage_const_1 
                  
                  for j in range(QQ(n)/e_new):
                    new_legs[j % (QQ(n)/n1)]+=[m]
                    new_legs[(j % (QQ(n)/n2))+(QQ(n)/n1)]+=[m+_sage_const_1 ]
                    new_edges+=[(m,m+_sage_const_1 )]
                    new_legact[(sigma,m)]=m0+((m+_sage_const_2 -m0)%(_sage_const_2 *QQ(n)/e_new))
                    new_legact[(sigma,m+_sage_const_1 )]=new_legact[(sigma,m)]+_sage_const_1 
                    new_character[m]=(NumtoG[(QQ(n)/e_new)%n],e_new, k1)
                    new_character[m+_sage_const_1 ]=(NumtoG[(QQ(n)/e_new)%n],e_new, k2)
                    
                    m+=_sage_const_2 
                  
                  
                  # take care of remaining actions of g in G-{sigma} on legs belonging to orbit of new edge  
                  for jplus in range(_sage_const_2 ,n+_sage_const_1 ):
                    for m in range(m0,m0+_sage_const_2 *QQ(n)/e_new):
                      new_legact[(NumtoG[jplus%n],m)]=new_legact[(sigma,new_legact[(NumtoG[(jplus-_sage_const_1 )%n],m)])]
                                      
                  for md in mark_dist:
                    new_legs_plus=deepcopy(new_legs)
                    for alpha in range(len(I1)):
                      for j in range(QQ(n)/e[I[alpha]]):
                        new_legs_plus[(md[alpha]+j)%(QQ(n)/n1)]+=[self.legact[(NumtoG[j],I[alpha])]]
                    for alpha in range(len(I1),len(I)):
                      for j in range(QQ(n)/e[I[alpha]]):
                        new_legs_plus[(md[alpha]+j)%(QQ(n)/n2)+(QQ(n)/n1)]+=[self.legact[(NumtoG[j],I[alpha])]]   
                        
                    # all the data is now ready to generate the new graph
                    new_Ggraph=Gstgraph(G,stgraph(new_genera,new_legs_plus,new_edges),{},new_legact,new_character,hdata=self.hdata)
                    new_Ggraph.vertact_reconstruct()
                    degen+=[new_Ggraph]
          if len(dege.genera)==_sage_const_1 :  # case of self-loop
            I=deepcopy(dege.legs[0])
            I.remove(dege.edges[len(dege.edges)-_sage_const_1 ][0])  # remove the legs corresponding to the degenerated edge
            I.remove(dege.edges[len(dege.edges)-_sage_const_1 ][1])
                       
            
            n0_min=lcm([e[alpha] for alpha in I])
            
            #TODO: following for-loop has great optimization potential, but current form should be sufficient for now
            for n0_add in range(_sage_const_1 ,floor(QQ(n)/n0_min +_sage_const_1) ):
              n0=n0_add*n0_min  # n0 is the order of the stabilizer of any of the vertices
              if n0.divides(n):  
                for e_new in n0.divisors():
                  for g0 in [x for x in range(floor(QQ(n)/(_sage_const_2 *n0)+_sage_const_1) ) if gcd(x,QQ(n)/n0)==_sage_const_1 ]:
                    for nu1 in [j for j in range(e_new) if gcd(j,e_new)==_sage_const_1 ]:
                      if g0==_sage_const_0  and nu1>QQ(e_new)/_sage_const_2 :  # g0==0 means only one vertex and then there is a symmetry inverting edges
                        continue
                      nu2=e_new-nu1
                      k1=Integer(nu1).inverse_mod(e_new)
                      k2=Integer(nu2).inverse_mod(e_new)
                      
                      # now we list all ways to distribute the markings, avoiding duplicates by symmetries
                      I_temp=deepcopy(I)
                      
                      possi={}  #dictionary associating to a leg l in I the possible positions of l (from 0 to n/n1-1 if l in I1, ...)
                      
                      if len(I)>_sage_const_0 :
                        possi[I[0]]=[0] # use G-action to move marking I1[0] to zeroth vertex
                        I_temp.pop(_sage_const_0 )
                      for i in I_temp:
                        possi[i]=list(range(QQ(n)/n0))
                      
                      
                      # mark_dist is a list of the form [(v1,v2,...), ...] where leg I[0] goes to vertex number v1 in its orbit, ....
                      mark_dist=itertools.product(*[possi[j] for j in I]) 
     
                  
                      # now all choices are made, and we construct the degenerated graph, to add it to degen
                      # first: use Riemann-Hurwitz to compute the genera of the vertices above 0,1
                      gen0=floor((n0*(_sage_const_2 *dege.genera[0]-_sage_const_2 )+n0*(sum([_sage_const_1 -QQ(_sage_const_1 )/e[alpha] for alpha in I])+_sage_const_2 -QQ(_sage_const_2 )/e_new))/QQ(_sage_const_2 )+_sage_const_1  )
                      
                      # nonemptyness condition #TODO: is this the only thing you need to require?
                      if gen0<_sage_const_0 :
                        continue
                    
                      new_genera=[gen0 for j in range(QQ(n)/n0)]
                      new_legs=[[] for j in range(QQ(n)/n0)]
                      new_legact=deepcopy(self.legact)
                      new_edges=deepcopy(self.gamma.edges)
                      new_character=deepcopy(self.character)
                  
                      # now go through the orbit of the edge and adjust all necessary data
                      m0=self.gamma.maxleg+_sage_const_1 
                      m=self.gamma.maxleg+_sage_const_1 
                  
                      for j in range(QQ(n)/e_new):
                        new_legs[j % (QQ(n)/n0)]+=[m]
                        new_legs[(j+g0) % (QQ(n)/n0)]+=[m+_sage_const_1 ]
                        new_edges+=[(m,m+_sage_const_1 )]
                        new_legact[(sigma,m)]=m0+((m+_sage_const_2 -m0)%(_sage_const_2 *QQ(n)/e_new))
                        new_legact[(sigma,m+_sage_const_1 )]=new_legact[(sigma,m)]+_sage_const_1 
                        new_character[m]=(NumtoG[(QQ(n)/e_new)%n],e_new, k1)
                        new_character[m+_sage_const_1 ]=(NumtoG[(QQ(n)/e_new)%n],e_new, k2)
                    
                        m+=_sage_const_2
                  
                      # take care of remaining actions of g in G-{sigma} on legs belonging to orbit of new edge  
                      for jplus in range(_sage_const_2 ,n+_sage_const_1 ):
                        for m in range(m0,m0+_sage_const_2 *QQ(n)/e_new):
                          new_legact[(NumtoG[jplus%n],m)]=new_legact[(sigma,new_legact[(NumtoG[(jplus-_sage_const_1 )%n],m)])]
                                      
                      for md in mark_dist:
                        new_legs_plus=deepcopy(new_legs)
                        for alpha in range(len(I)):
                          for j in range(QQ(n)/e[I[alpha]]):
                            new_legs_plus[(md[alpha]+j)%(QQ(n)/n0)]+=[self.legact[(NumtoG[j],I[alpha])]]
                        
                        
                        # all the data is now ready to generate the new graph
                        new_Ggraph=Gstgraph(G,stgraph(new_genera,new_legs_plus,new_edges),{},new_legact,new_character,hdata=self.hdata)
                        new_Ggraph.vertact_reconstruct()
                        degen+=[new_Ggraph]
        return degen    
      else:
        print('Degenerations for non-cyclic groups not implemented!')
        return []
        
# returns the list of all G-isomorphisms of the Gstgraphs Gr1 and Gr2 
# isomorphisms must respect markings (=legs that don't appear in edges)
# they are given as [dictionary of images of vertices, dictionary of images of legs]
#TODO:IDEA: first take quotients, compute isomorphisms between them, then lift??
def equiGraphIsom(Gr1,Gr2):      
  if Gr1.G != Gr2.G:
    return []
  Iso = GraphIsom(Gr1.gamma,Gr2.gamma)  # list of all isomorphisms of underlying dual graphs
  GIso=[]
  
  #TODO: once Gequiv=False, can abort other loops
  #TODO: check character data!!
  for I in Iso:
    Gequiv=True
    for g in Gr1.G.gens():
      # check if isomorphism I is equivariant with respect to g: I o g = g o I
      # action on vertices:
      for v in I[0]:
        if I[0][Gr1.vertact[(g,v)]] != Gr2.vertact[(g,I[0][v])]:
          Gequiv=False
          break
      # action on legs:
      for l in I[1]:
        if I[1][Gr1.legact[(g,l)]] != Gr2.legact[(g,I[1][l])]:
          Gequiv=False   
          break       
      # character:
      for l in I[1]:
        if Gequiv==False:
          break
        for j in [t for t in range(Gr1.character[l][1]) if gcd(t,Gr1.character[l][1])==_sage_const_1 ]:
          if Gr1.character[l][0]**j == Gr2.character[I[1][l]][0] and not ((j*Gr1.character[l][2]-Gr2.character[I[1][l]][2])%Gr1.character[l][1])==_sage_const_0 :
            Gequiv=False
            break
    if Gequiv:
      GIso+=[I]      
  
  return GIso
    
# HurwitzData models the ramification data D of a Galois cover of curves in the following way:
#
# D.G = finite group
# D.l = list of elements of the form (h,e,k) corresponding to orbits of markings with 
#   * a generator h in G of the stabilizer of the element p of an orbit
#   * the order e of the stabilizer
#   * an integer 0<=k<e such that h acts on the tangent space of the curve at p by exp(2 pi i/e * k)
class HurwitzData:
  def __init__(self,G,l):
    self.G=G
    self.l=l
  def __eq__(self,other):
    if not isinstance(other,HurwitzData):
      return False
    return (self.G==other.G) and (self.l==other.l)
  def __hash__(self):
    return hash((self.G,tuple(self.l)))
  def __repr__(self):
    return repr((self.G,self.l))  
  def __deepcopy__(self,memo):
    return HurwitzData(self.G,deepcopy(self.l))  
  def nummarks(self):
    g=self.G.order()
    N=sum([QQ(g)/r[1] for r in self.l])
    return floor(N)

# HurData takes a group G and a list l of group elements (giving monodromy around the corresponding markings) and gives back the corresponding Hurwitz data 
# This ist just a more convenient way to enter HurwitzData
def HurData(G,l):
  return HurwitzData(G,[(h,h.order(),min(h.order(),_sage_const_1 )) for h in l])

# returns the trivial stable graph of genus gen with group action corresponding to the HurwitzData D    
def trivGgraph(gen,D):
  G=D.G
  
  #graph has only one vertex with trivial G-action
  vertact={}
  for g in D.G:
    vertact[(g,_sage_const_0 )]=_sage_const_0 
  
  n=_sage_const_0  #counts number of legs as we go through Hurwitz data  
  legact={}
  character={}

  for e in D.l:
    # h=e[0] generates the stabilizer of (one element of) the orbit corresponding to e
    H=G.subgroup([e[0]])
    # markings corresponding to entry e are labelled by cosets gH and G-action is given by left-action of G
    (L,dic)=rightcosetaction(G,H)
    for g in G:
      for j in range(len(L)):
        legact[(g,j+_sage_const_1 +n)] = dic[(g,j)]+_sage_const_1 +n  #shift comes from fact that the n legs 1,2,...,n have already been assigned

    for j in range(len(L)):
      # Stabilizer at point gH generated by ghg**{-1}, of same order e, acts still by exp(2 pi i/e * k)
      character[j+_sage_const_1 +n]=(L[j]*e[0]*L[j].inverse(), e[1],e[2])
    n+=len(L)
    
    
  gamma=stgraph([gen],[list(range(_sage_const_1 ,n+_sage_const_1 ))],[])  
  
  return Gstgraph(G,gamma,vertact,legact,character,hdata=D)


# gives a (duplicate-free) list of Gstgraphs for the Hurwitz space of genus g with HurwitzData H in codimension r
#TODO: Huge potential for optimization, at the moment consecutively degenerate and check for isomorphisms

@cached_function
def list_Hstrata(g,H,r):
  if r==_sage_const_0 :
    return [trivGgraph(g,H)]
  Lold=list_Hstrata(g,H,r-_sage_const_1 )
  Lnew=[]
  for Gr in Lold:
    for v in range(len(Gr.gamma.genera)):
      Lnew+=Gr.degenerations(v)
  # now Lnew contains a list of all possible degenerations of graphs G with codimension r-1
  # need to identify duplicates
  
  if Lnew==[]:
    return []
  
  Ldupfree=[Lnew[0]]
  count=_sage_const_1 
  # duplicate-free list of strata
  
  for i in range(_sage_const_1 ,len(Lnew)):
    newgraph=True
    for j in range(count):
      if equiGraphIsom(Lnew[i],Ldupfree[j]) != []:
        newgraph=False
        break    
    if newgraph:
      Ldupfree+=[Lnew[i]]
      count+=_sage_const_1 

  return Ldupfree      

# gives a list of the quotgraphs of the entries of list_Hstrata(g,H,r) and the corresponding dictionaries
# list elements are of the form [quotient graph,deggrfind(quotient graph),dicv,dicvinv,dicl]
# if localize=True, finds the quotient graphs in the corresponding degeneration_graph and records their index as well as an isomorphism to the standard-graph
# then the result has the form: [quotient graph,index in degeneration_graph,dicv,dicvinv,dicl,diclinv], where
#   * dicv is the quotient map sending vertices of Gr in list_Hstrata(g,H,r) to vertices IN THE STANDARD GRAPH inside degeneration_graph
#   * dicvinv gives a section of dicv
#   * dicl sends leg names in Gr to leg names IN THE STANDARD GRAPH
#   * diclinv gives a section of dicl

@cached_function
def list_quotgraphs(g,H,r,localize=True):
  Hgr=list_Hstrata(g,H,r)
  result=[]
  for gr in Hgr:
    dicv={}
    dicvinv={}
    dicl={}
    qgr=gr.quotient_graph(dicv,dicvinv,dicl)
    if localize:
      dgfind=deggrfind(qgr)
      defaultdicv=dgfind[2]
      defaultdicl=dgfind[3]
      defaultdicvinv={defaultdicv[v]:v for v in defaultdicv}
      defaultdiclinv={defaultdicl[l]:l for l in defaultdicl}
      
      result.append([qgr,dgfind[1],{v: defaultdicv[dicv[v]] for v in dicv},{w:dicvinv[defaultdicvinv[w]] for w in defaultdicvinv},{l:defaultdicl[dicl[l]] for l in dicl},defaultdiclinv])
    else:
      result.append([qgr,dicv,dicvinv,dicl])
  return result

# cyclicGstgraph is a convenient method to create a Gstgraph for a cyclic group action. It takes as input
#   * a stgraph Gr
#   * a number n giving the order of the cyclic group G
#   * a tuple perm of the form ((1,2),(3,),(4,5,6)) describing the action of a generator sigma of G on the legs; all legs need to appear to fix their order for interpreting cha
#   * a tuple cha=(2,3,1) giving for each of the cycles of legs l in perm the number k such that sigma**{n/|G_l|} acts on the tangent space at l by exp(2 pi i/|G_l| *k)
# and returns the corresponding Gstgraph
# optionally, the generator sigma can be given as input directly and G is computed as its parent
# Here we use that the G-action on a connected graph Gr is uniquely determined by the G-action on the legs
# TODO: user-friendliness: allow (3) instead of (3,)
def cyclicGstgraph(Gr,n,perm,cha,sigma=None):
  if sigma is None:
    G=PermutationGroup(tuple(range(_sage_const_1 ,n+_sage_const_1 )))
    sigma=G.gens()[0]
  else:
    G=sigma.parent()

  
  # first legaction and character
  perm_dic={}  # converts action of sigma into dictionary
  character={}
  
  for cycleno in range(len(perm)):
    e=floor(QQ(n)/len(perm[cycleno])) # order of stabilizer
    for j in range(len(perm[cycleno])):
      perm_dic[perm[cycleno][j]] = perm[cycleno][(j+_sage_const_1 )%len(perm[cycleno])]
      character[perm[cycleno][j]]=(sigma**(len(perm[cycleno])), e, cha[cycleno] )
     
  
  legact={(sigma,k):perm_dic[k] for k in perm_dic}
  
  mu=sigma
  for j in range(_sage_const_2 ,n+_sage_const_1 ):
    mu2=mu*sigma
    legact.update({(mu2,k):perm_dic[legact[(mu,k)]] for k in perm_dic})
    mu=mu2
  
  #TODO: insert appropriate hdata
  Gr_new=Gstgraph(G,Gr,{},legact,character)  # we don't bother to fill in vertact, since it is reconstructable anyway
  Gr_new.vertact_reconstruct()
  
  return Gr_new 

#returns a tuple (L,d) of
#  * a list L =[g_0, g_1, ...] of representatives g_i of the cosets g_i H of H in G
#  * a dictionary d associating to tuples (g,n) of g in G and integers n the integer m, such that g*(g_n H) = g_m H
#TODO: assumes first element of L is id_G
def rightcosetaction(G,H):
  C=G.cosets(H, side='right')
  L=[C[i][0] for i in range(len(C))]
  d={}
  
  for g in G:
    for i in range(len(C)):
      gtild=g*L[i]
      for j in range(len(C)):
        if gtild in C[j]:
          d[(g,i)]=j
  return (L,d)


#stores list of decstratums, together with methods for scalar multiplication from left and sum
class tautclass:   
  def __init__(self, terms):
    self.terms = terms  
    
  # returns the pullback of self under the forgetful map which forgot the markings in the list legs
  # rename: if True, checks if legs contains leg names already taken for edges
  def forgetful_pullback(self,legs,rename=True):
    r"""
    Returns the pullback of a given tautological class under the map pi : \bar M_{g,A cup B} --> \bar M_{g,A}.
    
    INPUT:
          
    legs : list
      List B of legs that are forgotten by the map pi.

      
    EXAMPLES::
    
      sage: from admcycles import *

      sage: psiclass(2,1,2).forgetful_pullback([3])
      Graph :      [1] [[1, 2, 3]] []
      Polynomial : 1*psi_2^1 
      <BLANKLINE>
      Graph :      [1, 0] [[1, 4], [5, 3, 2]] [(4, 5)]
      Polynomial : (-1)*
    """
    return sum([tautclass([])]+[c.forgetful_pullback(legs,rename) for c in self.terms])      

  # computes the pushforward under the map forgetting the given legs
  def forgetful_pushforward(self,legs):
    r"""
    Returns the pushforward of a given tautological class under the map pi : \bar M_{g,n} --> \bar M_{g,{1,...,n} \ A}.
    
    INPUT:
    
    legs : list
      List A of legs that are forgotten by the map pi.
      
    EXAMPLES::
    
      sage: from admcycles import *

      sage: s1=psiclass(3,1,3)^2;s1.forgetful_pushforward([2,3])
      Graph :      [1] [[1]] []
      Polynomial : 1*
    
    ::
    
      sage: t=tautgens(2,2,1)[1]+2*tautgens(2,2,1)[3]
      sage: t.forgetful_pushforward([1])
      Graph :      [2] [[2]] []
      Polynomial : 3*
      <BLANKLINE>
      Graph :      [2] [[2]] []
      Polynomial : 2*
    """
    return tautclass([t.forgetful_pushforward(legs) for t in self.terms]).consolidate()
    
  def rename_legs(self,dic,rename=False):
    for t in self.terms:
      t.rename_legs(dic,rename)
    return self  

  def __add__(self,other):        
    if other==_sage_const_0 :
      return deepcopy(self)
    new=deepcopy(self)
    new.terms+=deepcopy(other.terms)
    return new.consolidate()

  def __neg__(self):
    return (-_sage_const_1 )*self  
  
  def __sub__(self,other):
    return self + (-_sage_const_1 )*other  

  def __iadd__(self,other):
    if other==_sage_const_0 :
      return self
    if isinstance(other,tautclass):
      self.terms+=other.terms  
      return self
    if isinstance(other,decstratum):
      self.terms.append(other)
      return self  
    
  def __radd__(self,other):
    if other==_sage_const_0 :
      return deepcopy(self) #changed this adding deepcopy
    else:
      return self+other  
  
  def __mul__(self,other):
    return self.__rmul__(other)    
  
  def __rmul__(self,other): 
    if isinstance(other,tautclass):
      result=tautclass([])
      for t1 in self.terms:
        for t2 in other.terms:
          result+=t1*t2
      return result  
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational) or isinstance(other,int):
    else:
      new=deepcopy(self)
      for i in range(len(new.terms)):
        new.terms[i]=other*new.terms[i]
      return new


  def __pow__(self,exponent):
    if isinstance(exponent,Integer) or isinstance(exponent,Rational) or isinstance(exponent,int):
      return prod(exponent*[self])
  
  def coeff_subs(self,dic):
    r"""
    If coefficients of self are polynomials, it tries to substitute variable assignments given by dic.
    """
    safetycopy=deepcopy(self)
    try:
      for t in self.terms:
        coelist=t.poly.coeff
        for i in range(len(coelist)):
          coelist[i]=coelist[i].subs(dic)
      return self
    except:
      print('Substitution failed!')
      return safetycopy
      
      
  def __repr__(self):
    s=''
    for i in range(len(self.terms)):
      s+=repr(self.terms[i])+'\n\n'
    return s.rstrip('\n\n')
  
  def toTautvect(self,g=None,n=None,r=None):
    if g==None or n==None or r==None:
      l=self.gnr_list()
      if len(l)==_sage_const_1 :
        g=l[0][0]
        n=l[0][1]
        r=l[0][2]    
    return converttoTautvect(self,g,n,r)
  def toTautbasis(self,g=None,n=None,r=None,moduli='st'):
    r"""
    TESTS::
    
      sage: from admcycles import StableGraph
      sage: b=StableGraph([1],[[1,2,3]],[(2,3)]).to_tautclass()
      sage: b.toTautbasis()
      (10, -10, -14)
      sage: b.toTautbasis(moduli='ct')
      (0, 0)

    """
    if g==None or n==None or r==None:
      l=self.gnr_list()
      if len(l)==_sage_const_1 :
        g=l[0][0]
        n=l[0][1]
        r=l[0][2]      
    return Tautvecttobasis(converttoTautvect(self,g,n,r),g,n,r,moduli)
  
  def toprodtautclass(self,g,n):
    return prodtautclass(stgraph([g],[list(range(_sage_const_1 ,n+_sage_const_1 ))],[]), [[t] for t in deepcopy(self.terms)])
  
  def dimension_filter(self):
    for i in range(len(self.terms)):
      self.terms[i].dimension_filter()
    return self.consolidate()    
  
  #remove all terms of degree greater than dmax
  def degree_cap(self,dmax):
    for i in range(len(self.terms)):
      self.terms[i].degree_cap(dmax)
    return self.consolidate()  
  
  # returns degree d part of self
  def degree_part(self,d):
    result=tautclass([])
    for i in range(len(self.terms)):
      result+=self.terms[i].degree_part(d)
    return result.consolidate()
  
  def simplify(self,g=None,n=None,r=None):
    r"""
    Simplifies self by combining terms with same tautological generator, returns self.
    """
    L=self.gnr_list()
    if len(L)==_sage_const_0 :
      return self
    

    
    if r!=None:
      # Assume that self is not combination from different g,n
      g=L[0][0]
      n=L[0][1]   
      self.terms= Tautv_to_tautclass(self.toTautvect(g,n,r),g,n,r).terms
      return self
    else:
      result=tautclass([])
      for gnr in L:
        result+=Tautv_to_tautclass(self.toTautvect(*gnr),*gnr)
      self.terms=result.terms
      return self  

    
    #newself=Tautv_to_tautclass(self.toTautvect(g,n,r),g,n,r)
    #self.terms=newself.terms
    #return self
  
  # uses FZ relations to convert self in a sum of the basis tautclasses
  def FZsimplify(self,r=None):
    r"""
    Returns representation of self as a tautclass formed by a linear combination of the preferred tautological basis.
    If r is given, only take degree r part.
    """   
    L=self.gnr_list()
    if len(L)==_sage_const_0 :
      return deepcopy(self)
    

    
    if r!=None:
      # Assume that self is not combination from different g,n
      g=L[0][0]
      n=L[0][1]      
      return Tautvb_to_tautclass(self.toTautbasis(g,n,r),g,n,r)
    else:
      result=tautclass([])
      for gnr in L:
        result+=Tautvb_to_tautclass(self.toTautbasis(*gnr),*gnr)
      return result  
    
  def consolidate(self):  #TODO: Check for isomorphisms of stgraphs for terms, add corresponding kppolys
    revrange=list(range(len(self.terms)))
    revrange.reverse()
    for i in revrange:
      self.terms[i].consolidate()
      if len(self.terms[i].poly.monom)==_sage_const_0 :
        self.terms.pop(i)
    return self
  # computes integral against the fundamental class of the corresponding moduli space
  # will not complain if terms are mixed degree or if some of them do not have the right codimension  
  def evaluate(self):  
    return sum([t.evaluate() for t in self.terms])
  
  # returns a list [(g,n,r), ...] of all genera g, number n of markings and degrees r for the terms appearing in self
  def gnr_list(self):  
    L=[s for t in self.terms for s in t.gnr_list()]
    return list(set(L))
  
  # Decides if self is equivalent to zero (also for mixed-degree classes)
  def is_zero(self):  
    return (False not in [(self.toTautbasis(*gnr)).is_zero() for gnr in self.gnr_list()])
  

# polynomial in kappa and psi-classes on a common stgraph; represents this data by a list monomials of entries (kappa,psi) and a list coeff of their coefficients
# here (kappa,psi) is a monomial in kappa, psi classes, represented as
# * kappa = list of length len(self.gamma.genera) of lists of the form [3,0,2] meaning that this vertex carries kappa_1**3*kappa_3**2
# * psi   = dictionary, associating nonnegative integers to some legs, where psi[l]=3 means that there is a psi**3 at this leg
# for a kppoly p, the expression p[i] is of the form (kappa,psi,coeff)
class kppoly:
  def __init__(self,monom,coeff):
    self.monom=monom
    self.coeff=coeff
  def __iter__(self):  #TODO fix
    return iter([self[i] for i in range(len(self))])
  def __getitem__(self,i): 
    return self.monom[i]+(self.coeff[i],)
  def __len__(self):
    return len(self.monom)
  def __neg__(self):
    return (-_sage_const_1 )*self  
  def __add__(self,other):        #TODO: Add __radd__
    if other==_sage_const_0 :
      return deepcopy(self)
    new=deepcopy(self)
    ot=deepcopy(other)
    for (k,p,c) in ot:
      try:
        ind=new.monom.index((k,p))
        new.coeff[ind]+=c
        if new.coeff[ind]==_sage_const_0 :
          new.monom.pop(ind)
          new.coeff.pop(ind)
      except ValueError:
        if c!=_sage_const_0 :
          new.monom+=[(k,p)]
          new.coeff+=[c]  
    return new
  
  # returns the degree of the ith term of self (default: i=0). If self is empty, give back None
  def deg(self,i=_sage_const_0 ):
    if len(self.monom)==_sage_const_0 :
      return None
    else:
      (kappa,psi)=self.monom[i]
      return sum([sum((j+_sage_const_1 )*kvec[j] for j in range(len(kvec)) ) for kvec in kappa])+sum(psi.values())
  
      

  # computes the pullback of self under a graph morphism described by dicv, dicl
  # returns a kppoly on this graph
  def graphpullback(self,dicv,dicl):
    if len(self.monom)==_sage_const_0 :
      return kppoly([],[])
    
    numvert_self=len(self.monom[0][0]) 
    numvert=len(dicv)
           
    preim=[[] for i in range(numvert_self)]
    for v in dicv:
      preim[dicv[v]]+=[v] 
    
    resultpoly=kppoly([],[])
    for (kappa,psi,coeff) in self:
      # pullback of psi-classes
      psipolydict={dicl[l]: psi[l] for l in psi}
      psipoly=kppoly([([[] for i in range(numvert)],psipolydict)],[1])  
            
      # pullback of kappa-classes
      kappapoly=prod([prod([sum([kappacl(w,k+_sage_const_1 ,numvert) for w in preim[v] ])**kappa[v][k] for k in range(len(kappa[v]))])  for v in range(numvert_self)])
            
      resultpoly+=coeff*psipoly*kappapoly
    return resultpoly  


  def rename_legs(self,dic):
    for count in range(len(self.monom)):
      self.monom[count]=(self.monom[count][0],{dic.get(l,l): self.monom[count][1][l] for l in self.monom[count][1]})
    return self  
  
  # takes old kappa-data and embeds self in larger graph with numvert vertices on vertices start, start+1, ...
  def expand_vertices(self,start,numvert):  
    for count in range(len(self.monom)):
      self.monom[count] = ([[] for i in range(start)]+self.monom[count][0] + [[] for i in range(numvert-start-len(self.monom[count][0]))], self.monom[count][1])
    return self  
  
  def __radd__(self,other):
    if other==_sage_const_0 :
      return deepcopy(self)
  
  def __mul__(self,other):
    if isinstance(other,kppoly):
      return kppoly([([kappaadd(kappa1[i],kappa2[i]) for i in range(len(kappa1))],{l:psi1.get(l,_sage_const_0 )+psi2.get(l,_sage_const_0 ) for l in set(list(psi1)+list(psi2))}) for (kappa1,psi1) in self.monom for (kappa2,psi2) in other.monom],[a*b for a in self.coeff for b in other.coeff]).consolidate()
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational):
    else:
      return self.__rmul__(other)  
    
  def __rmul__(self,other): 
    if isinstance(other,kppoly):
      return self.__mul__(other)    
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational) or isinstance(other,int):
    else:
      new=deepcopy(self)
      for i in range(len(self)):
        new.coeff[i]*=other
      return new

  
  def __pow__(self,exponent):
    if isinstance(exponent,Integer) or isinstance(exponent,Rational) or isinstance(exponent,int):
      return prod(exponent*[self])
      
  def __repr__(self):
    s=''
    for (kappa,psi,coeff) in self:
       coestring=repr(coeff)
       if coestring.find('+')!=-_sage_const_1  or coestring.find('-')!=-_sage_const_1 : # coefficient contains sum or minus (sign)
         coestring='('+coestring+')'
       s+=coestring+'*'
       count=-_sage_const_1 
       for l in kappa:
         count+=_sage_const_1 
         if len(l)==_sage_const_0 :
           continue
         s+='('
         for j in range(len(l)):
           if l[j]==_sage_const_0 :
             continue
           s+='kappa_'+ repr(j+_sage_const_1 )+'^'+repr(l[j])+' '
         s+=')_' + repr(count)+' '
       for l in psi:
         if psi[l]==_sage_const_0 :
           continue
         s+='psi_'+repr(l)+'^'+repr(psi[l])+' '
       s+='+'   
    return s.rstrip('+') 
   
   # remove trailing zeroes in kappa and l with psi[l]=0 and things with coeff=0 and sum up again
  def consolidate(self):
    for (kappa,psi) in self.monom:
      for k in range(len(kappa)):
        kappa[k]=remove_trailing_zeroes(kappa[k])
      for l in list(psi):
        if psi[l] == _sage_const_0 :
          psi.pop(l)
    # now we must check for newly identified duplicates
    newself=kppoly([],[])+self
    self.monom=newself.monom
    self.coeff=newself.coeff
    return self      
           
# some functions for entering kappa and psi classes

# returns (kappa_index)_vertex - must give total number of vertices
def kappacl(vertex,index,numvert,g=None,n=None):
  if index==_sage_const_0 :
    return (_sage_const_2 *g-_sage_const_2 +n)*onekppoly(numvert)
  if index<_sage_const_0 :
    return kppoly([],[])  
  li=[[] for i in range(numvert)]
  li[vertex]=(index-_sage_const_1 )*[0]+[1]
  return kppoly([(li,{})],[1])

# returns (psi)_leg - must give total number of vertices
def psicl(leg,numvert):
  li=[[] for i in range(numvert)]
  return kppoly([(li,{leg:_sage_const_1 })],[1])  

def onekppoly(numvert):
  return kppoly([([[] for cnt in range(numvert)],{})],[1])  
   
#  def clean(self):
#    for k in self.coeff.keys():
#      if self.coeff[k]==0:
#        self.coeff.pop(k)
#    return self
  #TODO: Multiplication with other kppoly  

# tautological class given by boundary stratum, decorated by a polynomial in kappa-classes on the vertices and psi-classes on the legs (i.e. half-edges and markings)
# self.gamma = underlying stgraph for the boundary stratum
# kappa = list of length len(self.gamma.genera) of lists of the form [3,0,2] meaning that this vertex carries kappa_1^3*kappa_3^2
# psi   = dictionary, associating nonnegative integers to some legs, where psi[l]=3 means that there is a psi^3 at this leg
# Convention: kappa_a = pi_*(c_1(omega_pi(sum p_i))^{a+1} ), where pi is the universal curve over the moduli space, omega_pi the relative dualizing sheaf and p_i are the (images of the) sections of pi given by the marked points
class decstratum:
  def __init__(self,gamma,kappa=None,psi=None,poly=None):
    self.gamma=gamma
    if kappa==None:
      kappa=[[] for i in range(len(gamma.genera))]
    if psi==None:  
      psi={}
    if poly==None:  
      self.poly=kppoly([(kappa,psi)],[1])
    else:
      if isinstance(poly,kppoly):
        self.poly=poly
      #if isinstance(poly,sage.rings.integer.Integer) or isinstance(poly,sage.rings.rational.Rational):
      else:
        self.poly=poly*onekppoly(len(gamma.genera))
        
  #def deg(self):
    #return len(self.gamma.edges)+sum([sum([k[i]*(i+1) for i in range(len(k))]) for k in kappa])+sum(psi.values())
  
  def automorphism_number(self):
    r"""Returns number of automorphisms of underlying graph fixing decorations by kappa and psi-classes.
    Currently assumes that self has exaclty one nonzero term."""
    kappa,psi=self.poly.monom[0]
    g,n,r = self.gnr_list()[0]
    markings=range(1,n+1)
    num=DR.num_of_stratum(Pixtongraph(self.gamma,kappa,psi),g,r,markings)
    return DR.autom_count(num,g,r,markings,DR.MODULI_ST)
  
  def rename_legs(self,dic,rename=False):
    if rename:
      legl=self.gamma.leglist()
      shift=max(legl+list(dic.values())+[0])+_sage_const_1 
      dicenh={l:dic.get(l,l+shift) for l in legl}
    else:
      dicenh=dic  
    self.gamma.rename_legs(dicenh)
    self.poly.rename_legs(dicenh)
    return self
  
  def __repr__(self):
    return 'Graph :      ' + repr(self.gamma) +'\n'+ 'Polynomial : ' + repr(self.poly)

  # returns a list of lists of the form [kp1,kp2,...,kpr] where r is the number of vertices in self.gamma and kpj is a kppoly being the part of self.poly living on the jth vertex (we put coeff in the first vertex)
  def split(self):   
    result=[]
    numvert=len(self.gamma.genera)
    lvdict={l:v for v in range(numvert) for l in self.gamma.legs[v]}
    
    for (kappa,psi,coeff) in self.poly:
      psidiclist=[{} for v in range(numvert)]
      for l in psi:
        psidiclist[lvdict[l]][l]=psi[l]
      newentry=[kppoly([([kappa[v]],psidiclist[v])],[1]) for v in range(numvert)]
      newentry[0]*=coeff
      result.append(newentry)  
    return result  

  def __neg__(self):
    return (-_sage_const_1 )*self  
  
  def __mul__(self,other):
    return self.__rmul__(other)  

  def __rmul__(self,other):
    if isinstance(other,Hdecstratum):   
      return other.__mul__(self)
    
    if isinstance(other,decstratum):  
      if len(other.gamma.edges)>len(self.gamma.edges):
        return other.__rmul__(self)
      if self.gamma.edges==[] and other.gamma.edges==[]:
        # both are just vertices with some markings and some kappa-psi-classes
        # multiply those kappa-psi-classes and return the result
        return tautclass([decstratum(deepcopy(self.gamma),poly=self.poly*other.poly)])
      p1=self.convert_to_prodtautclass()
      p2=self.gamma.boundary_pullback(other)
      p=p1*p2
      return p.pushforward()
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational):
    else:
      new=deepcopy(self)
      new.poly*=other
      return new           

  def toTautvect(self,g=None,n=None,r=None):
    return converttoTautvect(self,g,n,r)
  def toTautbasis(self,g=None,n=None,r=None):
    return Tautvecttobasis(converttoTautvect(self,g,n,r),g,n,r)
  
  # remove all terms that must vanish for dimension reasons 
  def dimension_filter(self):
    for i in range(len(self.poly.monom)):
      (kappa,psi)=self.poly.monom[i]
      for v in range(len(self.gamma.genera)):
        # local check: we are not exceeding dimension at any of the vertices
        if sum([(k+_sage_const_1 )*kappa[v][k] for k in range(len(kappa[v]))])+sum([psi[l] for l in self.gamma.legs[v] if l in psi])>_sage_const_3 *self.gamma.genera[v]-_sage_const_3 +len(self.gamma.legs[v]):
          self.poly.coeff[i]=_sage_const_0 
          break
        # global check: the total codimension of the term of the decstratum is not higher than the total dimension of the ambient space
        #if self.poly.deg(i)+len(self.gamma.edges)>3*self.gamma.g()-3+len(self.gamma.list_markings()):
         # self.poly.coeff[i]=0
          #break          
    return self.consolidate()      
  
  # remove all terms of degree higher than dmax
  def degree_cap(self,dmax):
    for i in range(len(self.poly.monom)):
      if self.poly.deg(i)+len(self.gamma.edges)>dmax:
        self.poly.coeff[i]=_sage_const_0 
    return self.consolidate()        

  # returns degree d part of self
  def degree_part(self,d):
    result=deepcopy(self)
    for i in range(len(result.poly.monom)):
      if result.poly.deg(i)+len(result.gamma.edges) != d:
        result.poly.coeff[i]=_sage_const_0 
    return result.consolidate()            
  
  def consolidate(self):
    self.poly.consolidate()
    return self

  # computes integral against the fundamental class of the corresponding moduli space
  # will not complain if terms are mixed degree or if some of them do not have the right codimension  
  def evaluate(self):  
    answer=_sage_const_0 
    for (kappa,psi,coeff) in self.poly:
      temp=_sage_const_1 
      for v in range(len(self.gamma.genera)):
        psilist=[psi.get(l,_sage_const_0 ) for l in self.gamma.legs[v]]
        kappalist=[]
        for j in range(len(kappa[v])):
          kappalist+=[j+_sage_const_1  for k in range(kappa[v][j])]
        if sum(psilist+kappalist) != _sage_const_3 *self.gamma.genera[v]-_sage_const_3 +len(psilist):
          temp = _sage_const_0 
          break
        temp*=DR.socle_formula(self.gamma.genera[v],psilist,kappalist)
      answer+=coeff*temp  
    return answer  
  
  # computes the pushforward under the map forgetting the given markings
  # this returns a decstratum on the stgraph obtained by forgetting and stabilizing
  # currently works by forgetting one marking at a time
  def forgetful_pushforward(self,markings,dicv=False):
    result=deepcopy(self)
    result.dimension_filter()
    vertim=list(range(len(self.gamma.genera)))
    for m in markings:
      # take current result and forget m
      v = result.gamma.vertex(m)
      if result.gamma.genera[v]==_sage_const_0  and len(result.gamma.legs[v])==_sage_const_3 :  
        # this vertex will become unstable, but the previous dimension filter took care that no term in result.poly has kappa or psi on vertex v
        # thus we can simply forget this vertex and go on, but we must adjust the kappa entries in result.poly
        
        # If the vertex v carries another marking m' and a leg l, then while m' and l cannot have psi-data, the psi-data from the complementary leg of l must be transferred to m'
        # TODO: use more elegant (dicv,dicl)-return of .stabilize()
        vlegs=deepcopy(result.gamma.legs[v])
        vlegs.remove(m)
        vmarks=set(vlegs).intersection(set(result.gamma.list_markings()))
        
        if len(vmarks)!=_sage_const_0 :
          mprime=list(vmarks)[0]
          vlegs.remove(mprime)
          leg=vlegs[0]
          legprime=result.gamma.leginversion(leg)
          for (kappa,psi,coeff) in result.poly:
            if legprime in psi:
              temp=psi.pop(legprime)
              psi[mprime]=temp
        
        result.gamma.forget_markings([m])
        result.gamma.stabilize()
        vertim.pop(v)
        for (kappa,psi,coeff) in result.poly:
          kappa.pop(v)
      else:
        # no vertex becomes unstable, hence result.gamma is unchanged
        # we proceed to push forward on the space corresponding to marking v
        g=result.gamma.genera[v]
        n=len(result.gamma.legs[v])-_sage_const_1   # n of the target space
        numvert=len(result.gamma.genera)
        
        newpoly=kppoly([],[])
        for (kappa,psi,coeff) in result.poly:    
          trunckappa=deepcopy(kappa)
          trunckappa[v]=[]
          truncpsi=deepcopy(psi)
          for l in result.gamma.legs[v]:
            truncpsi.pop(l,_sage_const_0 )
          trunckppoly=kppoly([(trunckappa,truncpsi)],[coeff])  # kppoly-term supported away from vertex v
          
          kappav=kappa[v]
          psiv={l:psi.get(l,_sage_const_0 ) for l in result.gamma.legs[v] if l !=m}
          psivpoly=kppoly([([[] for i in range(numvert)],psiv)],[1])
          a_m = psi.get(m,_sage_const_0 )
          
          cposs=[]
          for b in kappav:
            cposs.append(list(range(b+_sage_const_1 )))
          # if kappav=[3,0,1] then cposs = [[0,1,2,3],[0],[0,1]]
          
          currpoly=kppoly([],[])
          
          for cvect in itertools.product(*cposs):
            currpoly+=prod([binomial(kappav[i],cvect[i]) for i in range(len(cvect))])*prod([kappacl(v,i+_sage_const_1 ,numvert)**cvect[i] for i in range(len(cvect))])*psivpoly*kappacl(v,a_m+sum([(kappav[i]-cvect[i])*(i+_sage_const_1 ) for i in range(len(cvect))])-_sage_const_1 ,numvert,g=g,n=n)
          if a_m==_sage_const_0 :
            kappapoly=prod([kappacl(v,i+_sage_const_1 ,numvert)**kappav[i] for i in range(len(kappav))])
            
            def psiminuspoly(l):
              psivminus=deepcopy(psiv)
              psivminus[l]-=_sage_const_1 
              return kppoly([([[] for i in range(numvert)],psivminus)],[1])
            
            currpoly+=sum([psiminuspoly(l) for l in psiv if psiv[l]>_sage_const_0 ])*kappapoly
          
          newpoly+=currpoly*trunckppoly
          
        result.poly=newpoly
        result.gamma.forget_markings([m])
        
      
      result.dimension_filter()
    
    if dicv:
      return (result,{v:vertim[v] for v in range(len(vertim))})
    else:  
      return result  
  
  
  # returns a tautclass giving the pullback under the forgetful map which forgot the markings in the list newmark
  def forgetful_pullback(self,newmark,rename=True):  
    if newmark==[]:
      return tautclass([self])
    if rename:  #TODO: at the moment rename is not really functional, since total overhaul would be necessary at the first calling
      # make sure that markings in newmark do not already appear as leg-labels in some edge
      mleg=max(self.gamma.maxleg+_sage_const_1 ,max(newmark)+_sage_const_1 )
      rndic={}
      rnself=deepcopy(self)
    
      for e in self.gamma.edges:
        if e[0] in newmark:
          rndic[e[0]]=mleg
          mleg+=_sage_const_1 
        if e[1] in newmark:
          rndic[e[1]]=mleg
          mleg+=_sage_const_1   
      rnself.gamma.rename_legs(rndic)  
      
      #now must fix psi-data
      for l in rndic:
        for (kappa,psi,coeff) in rnself.poly:  
          if l in psi:
            psi[rndic[l]]=psi.pop(l)
    else:
      rnself=self
    
    
    # TODO: change recursive definition to explicit, direct definition? 
    # mdist = itertools.product(*[list(range(len(rnself.gamma.genera))) for j in range(len(newmark))])
    
    # Strategy: first compute pullback under forgetting newmark[0], then by recursion pull this back under forgetting other elements of newmark
    a=newmark[0]
    nextnewmark=deepcopy(newmark)
    nextnewmark.pop(_sage_const_0 )
    partpullback=[]  # list of decstratums to construct tautological class obtained by forgetful-pulling-back a
    
    for v in range(len(self.gamma.genera)):
      # v gives the vertex where the marking a goes
      
      # first the purely kappa-psi-term
      # grv is the underlying stgraph
      grv=deepcopy(rnself.gamma)
      grv.legs[v]+=[a]
      grv.tidy_up()
      
      # polyv is the underlying kppoly
      polyv=kppoly([],[])
      for (kappa,psi,coeff) in rnself.poly:
        binomdist=[list(range(_sage_const_0 ,m+_sage_const_1 )) for m in kappa[v]]  # for kappa[v]=(3,0,2) gives [[0,1,2,3],[0],[0,1,2]]
      
        for bds in itertools.product(*binomdist):
          kappa_new=deepcopy(kappa)
          kappa_new[v]=list(bds)
          
          psi_new=deepcopy(psi)
          psi_new[a]=sum([(i+_sage_const_1 )*(kappa[v][i]-bds[i]) for i in range(len(bds))])
          polyv=polyv+kppoly([(kappa_new,psi_new)],[((-_sage_const_1 )**(sum([(kappa[v][i]-bds[i]) for i in range(len(bds))])))*coeff*prod([binomial(kappa[v][i],bds[i]) for i in range(len(bds))])])
      
      # now the terms with boundary divisors
      rnself.gamma.tidy_up()
      newleg=max(rnself.gamma.maxleg+_sage_const_1 ,a+_sage_const_1 )  #this is the leg landing on vertex v, connecting it to the rational component below
      grl={}  # dictionary: leg l -> graph with rational component attached where l was
      for l in rnself.gamma.legs[v]:
        # create a copy of rnself.gamma with leg l replaced by a rational component attached to v, containing a and l
        new_gr=deepcopy(rnself.gamma)
        new_gr.legs[v].remove(l)
        new_gr.legs[v]+=[newleg]
        new_gr.genera+=[0]
        new_gr.legs+=[[newleg+_sage_const_1 ,a,l]]
        new_gr.edges+=[(newleg,newleg+_sage_const_1 )]
        new_gr.tidy_up()
        
        grl[l]= new_gr
      # contains kappa, psi polynomials attached to the graphs above
      polyl={l:kppoly([],[]) for l in rnself.gamma.legs[v]}     
      
      for (kappa,psi,coeff) in rnself.poly:
        for j in set(psi).intersection(set(rnself.gamma.legs[v])):
          if psi[j]==_sage_const_0 :  # no real psi class here
            continue
          kappa_new=deepcopy(kappa)+[[]] # rational component, which is placed last in the graphs above, doesn't get kappa classes
          
          psi_new=deepcopy(psi)
          psi_new[newleg]=psi_new.pop(j)-_sage_const_1   # psi**b at leg l is replaced by -psi^(b-1) at the leg connecting v to the new rational component
          
          polyl[j]=polyl[j]+kppoly([(kappa_new,psi_new)],[-coeff])
      partpullback+=[decstratum(grv,poly=polyv)]+[decstratum(grl[l], poly=polyl[l]) for l in rnself.gamma.legs[v] if len(polyl[l])>_sage_const_0 ]    
    # now partpullback is list of decstratums; create tautclass from this and return pullback under nextnewmark
    T=tautclass(partpullback)
    return T.forgetful_pullback(nextnewmark)
  
  # converts the decstratum self to a prodtautclass on self.gamma
  def convert_to_prodtautclass(self):  
    terms = []
    for (kappa,psi,coeff) in self.poly:
      currterm=[]
      for v in range(len(self.gamma.genera)):
        psiv={(lnum+_sage_const_1 ):psi[self.gamma.legs[v][lnum]] for lnum in range(len(self.gamma.legs[v])) if self.gamma.legs[v][lnum] in psi}
        currterm.append(decstratum(stgraph([self.gamma.genera[v]],[list(range(_sage_const_1 ,len(self.gamma.legs[v])+_sage_const_1 ))] ,[]),kappa=[kappa[v]],psi=psiv))
      currterm[0].poly*=coeff  
      terms.append(currterm)
    return prodtautclass(self.gamma,terms)  

  # returns a list [(g,n,r), ...] of all genera g, number n of markings and degrees r for the terms appearing in self
  def gnr_list(self):  
    g=self.gamma.g()
    n=self.gamma.n()
    e=len(self.gamma.edges)
    
    L=[(g,n,e+self.poly.deg(i)) for i in range(len(self.poly.monom))]
    return list(set(L))
    
#stores list of Hdecstratums, together with methods for scalar multiplication from left and sum
class Htautclass:   
  def __init__(self, terms):
    self.terms = terms      

  def __neg__(self):
    return (-_sage_const_1 )*self  

  def __add__(self,other):        # TODO: add += operation
    if other==_sage_const_0 :
      return deepcopy(self)
    new=deepcopy(self)
    new.terms+=deepcopy(other.terms)
    return new.consolidate()
  def __radd__(self,other):
    if other==_sage_const_0 :
      return self
    else:
      return self+other  
  def __rmul__(self,other): 
    new=deepcopy(self)
    for i in range(len(new.terms)):
      new.terms[i]=other*new.terms[i]      
    return new
  def __mul__(self,other):
    if isinstance(other,tautclass):
      return sum([a*b for a in self.terms for b in other.terms])   
    
  def __repr__(self):
    s=''
    for i in range(len(self.terms)):
      s+=repr(self.terms[i])+'\n\n'
    return s.rstrip('\n\n')
  def consolidate(self):  #TODO: Check for isomorphisms of Gstgraphs for terms, add corresponding kppolys
    for i in range(len(self.terms)):
      self.terms[i].consolidate()
    return self
  
  # returns self as a prodHclass on the correct trivial graph
  # TODO: if self.terms==[], this does not produce a meaningful result
  def to_prodHclass(self):
    if self.terms==[]:
      raise ValueError('Htautclass does not know its graph, failed to convert to prodHclass')   
    else:
      gamma0=stgraph([self.terms[0].Gr.gamma.g()],[self.terms[0].Gr.gamma.list_markings()],[])  
      terms=[t.to_decHstratum() for t in self.terms]
      return prodHclass(gamma0,terms)
  
  # computes the pushforward under the map \bar H -> M_{g',b}, sending C to C/G
  # the result is a tautclass  
  def quotient_pushforward(self):  
    res=tautclass([])
    for c in self.terms:
      res+=c.quotient_pushforward()
    return res  
  
  # pull back tautclass other on \bar M_{g',b} under the quotient map delta and return multiplication with self
  # effectively: pushforward self (divide by deg(delta)), multiply with other, then pull back entire thing
  # TODO: verify that this is allowed
  def quotient_pullback(self, other):
    if self.terms==[]:
      return deepcopy(self)  #self=0, so pullback still zero
    g=self.terms[0].Gr.gamma.g()
    hdata=self.terms[0].Gr.hdata
    trivGg=trivGgraph(g,hdata)
    Gord=hdata.G.order()
    deltadeg=trivGg.delta_degree(_sage_const_0 )
    
    push=(QQ(_sage_const_1 )/deltadeg)*self.quotient_pushforward()
    pro=push*other
    pro.dimension_filter()
    
    # result = quotient pullback of pro to trivGg
    result=Htautclass([])
    edgenums=set([len(t.gamma.edges) for t in pro.terms])
    Hstrata={i:list_Hstrata(g,hdata,i) for i in edgenums}
    Hquots={i:list_quotgraphs(g,hdata,i,True) for i in edgenums}
    
    
    for t in pro.terms:
      # t is a decstratum on \bar M_{g',b} living on a graph t.gamma
      # list all Hstrata having quotient graph t.gamma, then pull back t.poly and scale by right multiplicity
      (r,ti,tdicv,tdicl)=deggrfind(t.gamma)
      # tdicv and tdicl send vertex/leg names in t.gamma to the names of the vertices/legs in the standard graph
      
      preims=[j for j in range(len(Hstrata[r])) if Hquots[r][j][1]==ti]
      
      for j in preims:
        # this corresponds to a Gstgraph, which needs to be decorated by pullbacks of t.poly and added to result
        newGr=deepcopy(Hstrata[r][j])
        numvert=len(newGr.gamma.genera)
        multiplicity=prod([newGr.lstabilizer(e0).order() for (e0,e1) in Hquots[r][j][0].edges]) * t.gamma.automorphism_number() / QQ(len(equiGraphIsom(newGr,newGr)))
        (quotientgraph,inde,dicv,dicvinv,dicl,diclinv) = Hquots[r][j]
        
        # dv is a dictionary associating to vertex numbers in t.gamma a preimage vertex in newGr
        dv={v: tdicv[v] for v in range(len(t.gamma.genera))}
        
        newpoly=kppoly([],[])
        for (kappa,psi,coeff) in t.poly:
          newcoeff=coeff
          newkappa=[[] for u in range(numvert)]
          for v in range(len(kappa)):
            newkappa[dicvinv[tdicv[v]]]=kappa[v]
            newcoeff*=(QQ(_sage_const_1 )/newGr.vstabilizer(dicvinv[tdicv[v]]).order())**(sum(kappa[v]))
          newpsi={diclinv[tdicl[l]]:psi[l] for l in psi}  
          newcoeff*=prod([(newGr.lstabilizer(diclinv[tdicl[l]]).order())**(psi[l]) for l in psi])
          
          newpoly+=kppoly([(newkappa,newpsi)],[newcoeff])
          
          
        newpoly*=multiplicity
        
        
        result.terms.append(Hdecstratum(newGr,poly=newpoly))
    return result    
    


# H-tautological class given by boundary stratum of Hurwitz space, i.e. a Gstgraph, decorated by a polynomial in kappa-classes on the vertices and psi-classes on the legs (i.e. half-edges and markings)
# self.Gr = underlying Gstgraph for the boundary stratum
# self.kappa = list of length len(self.gamma.genera) of lists of the form (3,0,2) meaning that this vertex carries kappa_1^3*kappa_3^2
# self.psi   = dictionary, associating nonnegative integers to some legs, where psi[l]=3 means that there is a psi^3 at this leg
# Convention: kappa_a = pi_*(c_1(omega_pi(sum p_i))^{a+1} ), where pi is the universal curve over the moduli space, omega_pi the relative dualizing sheaf and p_i are the (images of the) sections of pi given by the marked points
class Hdecstratum:
  def __init__(self,Gr,kappa=None,psi=None,poly=None):
    self.Gr=Gr
    if kappa==None:
      kappa=[[] for i in range(len(Gr.gamma.genera))]
    if psi==None:  
      psi={}
    if poly==None:  
      self.poly=kppoly([(kappa,psi)],[1])
    else:
      self.poly=poly
  #def deg(self):
    #return len(self.gamma.edges)+sum([sum([k[i]*(i+1) for i in range(len(k))]) for k in kappa])+sum(psi.values())

  def __neg__(self):
    return (-_sage_const_1 )*self  

  def __rmul__(self,other):
    if isinstance(other,decstratum):   
      return self.__mul__(other)
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational):
    else:
      new=deepcopy(self)
      new.poly*=other
      return new     

  
  def to_decHstratum(self):
    result=self.Gr.to_decHstratum()
    result.poly*=self.poly
    return result
  
  def __mul__(self,other):
    if isinstance(other,decstratum):
      # Step 1: find a list commdeg of generic (self,other)-Gstgraphs Gamma3
      # Elements of this list will have the form (Gamma3,currentdeg) with currentdeg a list of elements (vdict1,ldict1,vdict2,ldict2), where
      #   * Gamma3 is a Gstgraph with same group G as self.Gr
      #   * vdict1, vdict2 are the vertex-maps from vertices of Gamma3 to self.Gr.gamma and other.gamma
      #   * ldict1, ldict2 are the leg-maps from legs of self.Gr.gamma, other.gamma to Gamma3
      if self.Gr.gamma.edges==[]:  # TODO: implement intersection with non-trivial Gstgraph
        mindeg=ceil(QQ(len(other.gamma.edges))/self.Gr.G.order())  # minimal number of edge-orbits to hope for generic graph
        maxdeg=len(other.gamma.edges)
        numotheraut = other.gamma.automorphism_number()

        Ggrdegenerations=[list_Hstrata(self.Gr.gamma.g(),self.Gr.hdata, r) for r in range(maxdeg+_sage_const_1 )]
       
        commdeg=[]
        multiplicityvector=[]  # gives for every entry in commdeg the number of degenerations isomorphic to this entry via Aut_G(Gamma3)
        for deg in range(mindeg,maxdeg+_sage_const_1 ):
          for Gamma3 in Ggrdegenerations[deg]:
            currentdeg=[]
            currentmultiplicity=[]
            otstructures=Astructures(Gamma3.gamma,other.gamma)
            if otstructures==[]:
              continue
            AutGr=equiGraphIsom(Gamma3,Gamma3)
            
            # Now single out representatives of the AutGr-action on otstructures
            while otstructures!=[]:
              (dicvcurr,diclcurr)=otstructures[0]
              multiplicity=_sage_const_0 
              for (dicv,dicl) in AutGr:
                dicvnew={v:dicvcurr[dicv[v]] for v in dicv}
                diclnew={l:dicl[diclcurr[l]] for l in diclcurr}
                try:
                  otstructures.remove((dicvnew,diclnew))
                  multiplicity+=_sage_const_1 
                except:
                  pass  
              # now must test if we are dealing with a generic structure
              
              coveredlegs=set()
              for g in Gamma3.G:
                for l in diclcurr.values():
                  coveredlegs.add(Gamma3.legact[(g,l)])
              # in general case would need to include half-edges from self.Gr.gamma
              if set(Gamma3.gamma.halfedges()).issubset(coveredlegs):       
                currentdeg+=[({v:_sage_const_0  for v in range(len(Gamma3.gamma.genera))},{l:l for l in self.Gr.gamma.leglist()},dicvcurr,diclcurr)] 
                multiplicity*=QQ(_sage_const_1 )/len(AutGr) #1*numotheraut/len(AutGr)
                currentmultiplicity+=[multiplicity]
            commdeg+=[(Gamma3,currentdeg)]    
            multiplicityvector+=[currentmultiplicity] 
      
      #Step 1 finished        
      
      
      # Step2: go through commdeg, use vdicts to transfer kappa-classes and ldicts to transfer psi-classes
      # from self and other to Gamma3; also look for multiple edges in G-orbits on Gamma3 and put 
      # the contribution (-psi-psi') coming from excess intersection there
      # TODO: figure out multiplicities from orders of orbits, automorphisms, etc.
      # TODO: eliminate early any classes that must vanish for dimension reasons
      # sum everything up and return it
      result = Htautclass([])
      for count in range(len(commdeg)):
       if commdeg[count][1]==[]:
         continue
       Gamma3 = commdeg[count][0]
       gammaresultpoly=kppoly([],[])
       for count2 in range(len(commdeg[count][1])):
        (vdict1,ldict1,vdict2,ldict2) = commdeg[count][1][count2]
        # compute preimages of vertices in self, other under the chosen morphisms to assign kappa-classes
        preim1=[[] for i in range(len(self.Gr.gamma.genera))]
        for v in vdict1:
          preim1[vdict1[v]]+=[v] 
        preim2=[[] for i in range(len(other.gamma.genera))]
        for v in vdict2:
          preim2[vdict2[v]]+=[v]
        numvert=len(Gamma3.gamma.genera)  
        
        # excess intersection classes
        quotdicl={}
        quotgraph=Gamma3.quotient_graph(dicl=quotdicl)
        numpreim={l:_sage_const_0  for l in quotgraph.halfedges()}
        
        for l in self.Gr.gamma.halfedges():
          numpreim[quotdicl[ldict1[l]]]+=_sage_const_1 
        for l in other.gamma.halfedges():
          numpreim[quotdicl[ldict2[l]]]+=_sage_const_1 
        
        excesspoly=onekppoly(numvert)
        for (e0,e1) in quotgraph.edges:
          if numpreim[e0]>_sage_const_1 :
            excesspoly*=( (-_sage_const_1 )*(psicl(e0,numvert)+psicl(e1,numvert)) )**(numpreim[e0]-_sage_const_1 )
        
        
        resultpoly=kppoly([],[])
        for (kappa1,psi1,coeff1) in self.poly:
          for (kappa2,psi2,coeff2) in other.poly:
            # pullback of psi-classes
            psipolydict={ldic1t[l]: psi1[l] for l in psi1}
            for l in psi2:
              psipolydict[ldict2[l]]=psipolydict.get(ldict2[l],_sage_const_0 )+psi2[l]
            psipoly=kppoly([([[] for i in range(numvert)],psipolydict)],[1])  
            
            # pullback of kappa-classes
            kappapoly1=prod([prod([sum([kappacl(w,k+_sage_const_1 ,numvert) for w in preim1[v] ])**kappa1[v][k] for k in range(len(kappa1[v]))])  for v in range(len(self.Gr.gamma.genera))])
            kappapoly2=prod([prod([sum([kappacl(w,k+_sage_const_1 ,numvert) for w in preim2[v] ])**kappa2[v][k] for k in range(len(kappa2[v]))])  for v in range(len(other.gamma.genera))])
            resultpoly+=coeff1*coeff2*psipoly*kappapoly1*kappapoly2
          
        resultpoly*=multiplicityvector[count][count2]*excesspoly   #TODO: divide by |Aut_G(Gamma3)| ??? if so, do in definition of multiplicityvector
        gammaresultpoly+=resultpoly
          
       result.terms+=[Htautclass([Hdecstratum(Gamma3,poly=gammaresultpoly)])]
      return result
  
  def __repr__(self):
    return 'Graph :      ' + repr(self.Gr) +'\n'+ 'Polynomial : ' + repr(self.poly)

  def consolidate(self):
    self.poly.consolidate()
    return self

  # computes the pushforward under the map \bar H -> M_{g',b}, sending C to C/G
  # the result is a tautclass  
  def quotient_pushforward(self):  
    Gord=self.Gr.G.order()
    
    qdicv={}
    qdicvinv={}
    qdicl={}
    quotgr=self.Gr.quotient_graph(dicv=qdicv, dicvinv=qdicvinv, dicl=qdicl)
    
    preimlist=[[] for i in range(len(quotgr.genera))]
    for v in range(len(self.Gr.gamma.genera)):
      preimlist[qdicv[v]]+=[v]
    
    # first, for each vertex w in quotgr compute the degree of the delta-map  \bar H(preim(v)) -> \bar M_{g(v),n(v)}
    deltadeg={w: self.Gr.delta_degree(qdicvinv[w]) for w in qdicvinv}
    
    # result will be decstratum on the graph quotgr
    # go through all terms of self.poly and add their pushforwards
    # for each term, go through vertices of quotient graph and collect all classes above it, 
    # i.e. kappa-classes from vertex-preimages and psi-classes from leg-preimages
    
    resultpoly=kppoly([],[])
    for (kappa,psi,coeff) in self.poly:
      kappanew=[]
      coeffnew=coeff
      psinew={}
      for w in range(len(quotgr.genera)):
        kappatemp=[]
        for v in preimlist[w]:
          kappatemp=kappaadd(kappatemp,kappa[v])
        kappanew+=[kappatemp]
        coeffnew*=(QQ(Gord)/len(preimlist[w]))**sum(kappatemp)  # Gord/len(preimlist[w]) is the order of the stabilizer of any preimage v of w
      for l in psi:
        psinew[qdicl[l]]=psinew.get(qdicl[l],_sage_const_0 )+psi[l]
        coeffnew*=(QQ(_sage_const_1 )/self.Gr.character[l][1])**psi[l]
      coeffnew*=prod(deltadeg.values())
      resultpoly+=kppoly([(kappanew,psinew)],[coeffnew]) 
    return tautclass([decstratum(quotgr,poly=resultpoly)])
      
# returns a list l' which is obtained from l by removing trailing zeroes, i.e. (1,0,3,0,0) -> (1,0,3) and (0,0)->()    
def remove_trailing_zeroes(l):
  j=_sage_const_0 
  for j in range(len(l)):
    if l[len(l)-j-_sage_const_1 ]!=_sage_const_0 :
      break
  if j==len(l)-_sage_const_1  and l[0]==_sage_const_0 :
    return []
  return [l[i] for i in range(len(l)-j)]    

# returns sum of kappa-vectors for same vertex, so [0,2]+[1,2,3]=[1,4,3]  
def kappaadd(a,b):
  if len(a)<len(b):
    aprime=a+(len(b)-len(a))*[0]
  else:
    aprime=a
  if len(b)<len(a):
    bprime=b+(len(a)-len(b))*[0]
  else:
    bprime=b
  return [aprime[i]+bprime[i] for i in range(len(aprime))] 

# converts a Pixton-style Graph (Matrix with univariate-Polynomial entries) into a decstratum  
# assume that markings on Graph are called 1,2,3,...,n
def Graphtodecstratum(G):  
  # first care about vertices, i.e. genera and kappa-classes
  genera=[]
  kappa=[]
  for i in range(_sage_const_1 ,G.M.nrows()):
    genera.append(G.M[i,_sage_const_0 ][0])
    kappa.append([G.M[i,_sage_const_0 ][j] for j in range(_sage_const_1 ,G.M[i,_sage_const_0 ].degree()+_sage_const_1 )])
  # now care about markings as well as edges together with the corresponding psi-classes
  legs=[[] for i in genera]
  edges=[]
  psi={}
  legname=G.M.ncols()   # legs corresponding to edges are named legname, legname+1, ...; cannot collide with marking-names
  for j in range(_sage_const_1 ,G.M.ncols()):
    for i in range(_sage_const_1 ,G.M.nrows()):
      if G.M[i,j] != _sage_const_0 :
        break
    # now i is the index of the first nonzero entry in column j
    if G.M[_sage_const_0 ,j] != _sage_const_0 :  # this is a marking
      legs[i-_sage_const_1 ].append(ZZ(G.M[_sage_const_0 ,j]))
      if G.M[i,j].degree()>=_sage_const_1 :
        psi[G.M[_sage_const_0 ,j]]=G.M[i,j][1]
        
    if G.M[_sage_const_0 ,j] == _sage_const_0 :  # this is a leg, possibly self-node
      if G.M[i,j][0] == _sage_const_2 :  #self-node
        legs[i-_sage_const_1 ]+=[legname, legname+_sage_const_1 ]
        edges.append((legname,legname+_sage_const_1 ))
        if G.M[i,j].degree()>=_sage_const_1 :
          psi[legname]=G.M[i,j][1]
        if G.M[i,j].degree()>=_sage_const_2 :
          psi[legname+_sage_const_1 ]=G.M[i,j][2]  
        legname+=_sage_const_2 
      if G.M[i,j][0] == _sage_const_1 :  #edge to different vertex
        if G.M.nrows()<=i+_sage_const_1 :
          print('Attention')
          print(G.M)
        for k in range(i+_sage_const_1 ,G.M.nrows()):
          if G.M[k,j] != _sage_const_0 :
            break
        # now k is the index of the second nonzero entry in column j
        legs[i-_sage_const_1 ]+=[legname]
        legs[k-_sage_const_1 ]+=[legname+_sage_const_1 ]
        edges.append((legname,legname+_sage_const_1 ))
        if G.M[i,j].degree()>=_sage_const_1 :
          psi[legname]=G.M[i,j][1]
        if G.M[k,j].degree()>=_sage_const_1 :
          psi[legname+_sage_const_1 ]=G.M[k,j][1] 
        legname+=_sage_const_2                
  return decstratum(stgraph(genera,legs,edges),kappa=kappa,psi=psi)        

# returns the indices of a generating set of R^r \bar M_{g,n} in Pixton's all_strata(g,r,(1,..,n),MODULI_ST)  
# usually this is computed by using the FZ-relations
# however, if r is greater than half the dimension of \bar M_{g,n} and all cohomology is tautological, we rather compute a generating set using Poincare duality and the intersection pairing            

@cached_function
def generating_indices(g,n,r,FZ=False):          
  if FZ or r<=(_sage_const_3 *g-_sage_const_3 +n)/QQ(_sage_const_2 ) or not (g <=_sage_const_1  or (g==_sage_const_2  and n <= _sage_const_19 )):
    rel=matrix(DR.list_all_FZ(g,r,tuple(range(_sage_const_1 ,n+_sage_const_1 ))))
    relconv=matrix([DR.convert_vector_to_monomial_basis(rel.row(i),g,r,tuple(range(_sage_const_1 ,n+_sage_const_1 ))) for i in range(rel.nrows())])
    del(rel)
    reverseindices=list(range(relconv.ncols()))
    reverseindices.reverse()
    reordrelconv=relconv.matrix_from_columns(reverseindices)
    del(relconv)
    reordrelconv.echelonize() #(algorithm='classical')
    
    reordnongens=reordrelconv.pivots()
    nongens=[reordrelconv.ncols()-i-_sage_const_1  for i in reordnongens]
    gens = [i for i in range(reordrelconv.ncols()) if not i in nongens]    
    
    # compute result of genstobasis here, for efficiency reasons
    gtob={gens[j] : vector(QQ,len(gens),{j:_sage_const_1 }) for j in range(len(gens))}
    for i in range(len(reordnongens)):
      gtob[nongens[i]]=vector([-reordrelconv[i,reordrelconv.ncols()-j-_sage_const_1 ]  for j in gens])
    genstobasis.set_cache([gtob[i] for i in range(reordrelconv.ncols())],
                          *(g,n,r))
    return gens
  else:
    gencompdeg=generating_indices(g,n,_sage_const_3 *g-_sage_const_3 +n-r,True)
    maxrank=len(gencompdeg)
    currrank = _sage_const_0 
    M=matrix(maxrank,_sage_const_0 )
    gens=[]
    count=_sage_const_0 
    while currrank<maxrank:
      Mnew=block_matrix([[M,matrix(DR.pairing_submatrix(tuple(gencompdeg),(count,),g,_sage_const_3 *g-_sage_const_3 +n-r,tuple(range(_sage_const_1 ,n+_sage_const_1 ))))]],subdivide=False)
      if Mnew.rank()>currrank:
        gens.append(count)
        M=Mnew
        currrank=Mnew.rank()
      count+=_sage_const_1   
    return gens    

def Hintnumbers(g,dat,indices=None, redundancy=False):
  Hbar = Htautclass([Hdecstratum(trivGgraph(g,dat),poly=onekppoly(_sage_const_1 ))])
  dimens = Hbar.terms[0].Gr.dim()
  markins=tuple(range(_sage_const_1 ,_sage_const_1 +len(Hbar.terms[0].Gr.gamma.list_markings())))
  
  strata=DR.all_strata(g,dimens,markins)
  decst=[Graphtodecstratum(Grr) for Grr in strata]
  intnumbers=[]
  
  if indices==None or redundancy:
    effindices=list(range(len(strata)))
  else:
    effindices=indices
  
  for i in effindices:
    intnumbers+=[(Hbar*(tautclass([ Graphtodecstratum(strata[i]) ]))).quotient_pushforward().evaluate()]
  
  if redundancy==False:
    return intnumbers
    
  M=DR.FZ_matrix(g,dimens,markins)
  Mconv=matrix([DR.convert_vector_to_monomial_basis(M.row(i),g,dimens,markins) for i in range(M.nrows())])
  relcheck= Mconv*vector(intnumbers)
  if relcheck==_sage_const_2 *relcheck:  # lazy way to check relcheck==(0,0,...,0)
    print('Intersection numbers are consistent, number of checks: '+repr(len(relcheck)))
  else:
    print('Intersection numbers not consistent for '+repr((g,dat.G,dat.l)))
    print('relcheck = '+repr(relcheck))
  
  if indices==None:
    return intnumbers
  else:
    return [intnumbers[j] for j in indices]    


# identifies the (pushforward of the) fundamental class of \bar H_{g,dat} in terms of tautological classes
# here g is the genus and dat is the HurwitzData
# Optional arguments:
#   * method='pair' means we compute all intersection pairings of \bar H with a generating set of the complementary degree
#     method='pull' means we pull back to the boundary strata and recursively identify the result, then use linear algebra to restrict the class of \bar H to an affine subvectorspace (the corresponding vector space is the intersection of the kernels of the above pullback maps), then we use intersections with kappa,psi-classes to get additional information - if this is not sufficient, return instead information about this affine subvectorspace
#   * vecout=True means we return a coefficient-list with respect to Pixton's generating set instead of a tautclass
#     NOTE: if vecout=True and markings is not the full list of markings 1,..,n , it will return a Tautvector for the space with smaller number of markings, where result is renamed in an order-preserving way 
#    (Example: n=5, markings=[2,5,1] then result lives on \bar M_{g,{2,5,1}} and the resulting Tautvect lives on \bar M_{g,3}, where marking names were translated as 1=>1, 2=>2, 5=>3 from \bar M_{g,{2,5,1}} to \bar M_{g,3})
#   * redundancy=True (only valid in case method='pair') means we not only compute pairings with a generating set but with all possible generators of complementary dimension and use the remaining intersections to check consistency of the result
#   * markings is a list, subset of 1,2,...,n (default: [1,2,...,n]). return the class obtained by the fundamental class of the Hurwitz space by forgetting all points not in markings
def Hidentify(g,dat,method='pull',vecout=False,redundancy=False,markings=None):
  Hbar = trivGgraph(g,dat)
  r = Hbar.dim()
  n = len(Hbar.gamma.list_markings())  
  
  #global Hexam
  #Hexam=(g,dat,method,vecout,redundancy,markings)
  
  if markings==None:
    markings=list(range(_sage_const_1 ,n+_sage_const_1 ))

  N=len(markings)
  msorted=sorted(markings)
  markingdictionary={i+_sage_const_1 :msorted[i] for i in range(N)}
  invmarkingdictionary={markingdictionary[j]:j for j in markingdictionary}
  
  # Section to deal with the case that the group G is trivial quickly
  if dat.G.order()==_sage_const_1 :
    if len(markings)<n:
      return tautclass([])
    else:
      return tautclass([decstratum(stgraph([g],[list(range(_sage_const_1 ,n+_sage_const_1 ))],[]))])  
  
  
  if not cohom_is_taut(g,len(markings),_sage_const_2 *(_sage_const_3 *g-_sage_const_3 +len(markings)-r)):
    print('Careful, Hurwitz cycle '+repr((g,dat))+' might not be tautological!\n')
  
  # first: try to look up if we already computed this class (or a class with even more markings) before
  found=False
  try:
    Hdb=Hdatabase[(g,dat)]
    for marks in Hdb:
      if set(markings).issubset(set(marks)):
        forgottenmarks=set(marks)-set(markings)
        result=deepcopy(Hdb[marks])
        result=result.forgetful_pushforward(list(forgottenmarks))
        found=True
        #TODO: potentially include this result in Hdb
        
  except KeyError:
    pass
  
  
  # if not, proceed according to method given
  if method=='pair' and not found:
    if not (g <=_sage_const_1  or (g==_sage_const_2  and n <= _sage_const_19 )):
      print('Careful, potentially outside of Gorenstein range!\n')
    genscompl= generating_indices(g,n,r)      # indices of generators in rank with which \bar H will be paired
    gens = generating_indices(g,n,_sage_const_3 *g-_sage_const_3 +n-r)  # indices of generators in rank in which \bar H sits
    
    intnumbers = Hintnumbers(g,dat,indices=genscompl,redundancy=redundancy)
    Mpairing = matrix(DR.pairing_submatrix(tuple(genscompl),tuple(gens),g,r,tuple(range(_sage_const_1 ,n+_sage_const_1 ))))
    
    # in Mpairing, the rows correspond to generators in genscompl, the columns to generators in gens
    # we want to solve the equation Mpairing * x = intnumbers, which should have a unique solution
    # then \bar H = sum_i x_i * generator(gens[i]) in R^(3g-3+n-r) \bar M_{g,n}
    x = Mpairing.solve_right(vector(intnumbers))
    
    strata = DR.all_strata(g,_sage_const_3 *g-_sage_const_3 +n-r,  tuple(range(_sage_const_1 ,n+_sage_const_1 ))  )
    stratmod=[]
    for i in range(len(gens)):
      if x[i]==_sage_const_0 :
        continue
      currstrat=Graphtodecstratum(strata[gens[i]])
      currstrat.poly*=x[i]
      stratmod.append(currstrat)
        
    result= tautclass(stratmod)   
    if (g,dat) not in Hdatabase:
      Hdatabase[(g,dat)]={}
    Hdatabase[(g,dat)][tuple(range(_sage_const_1 ,n+_sage_const_1 ))]=result
    
    if len(markings)<n:
      result=Hidentify(g,dat,method,False,redundancy,markings)
  if method=='pull' and not found:   
    gens = generating_indices(g,N,_sage_const_3 *g-_sage_const_3 +N-r)  # indices of generators in rank in which forgetful_* \bar H sits
    ngens=len(gens)
    bdrydiv=list_strata(g,N,_sage_const_1 )
    
    # first compute matrix describing the pullbacks of the generators in gens to the boundary
    # NEW: omit pullback to irreducible boundary, since this leads to computing FZ-relations on spaces with many markings
    A=pullback_matrix(g,N,_sage_const_3 *g-_sage_const_3 +N-r,irrbdry=False)

    irrpullback = False
    if g >= 1 and (A.rank() < ngens or redundancy):
      irrpullback = True
      irrbd = stgraph([g-1], [list(range(1 ,N+3))], [(N+1, N+2)])
      A = block_matrix([[A], [pullback_matrix(g, N, 3*g - 3 + N - r, bdry=irrbd)]], subdivide=False)

    kpinters=False
    if A.rank() < ngens or redundancy:
      # pullback to boundary not injective, try to throw in intersection numbers with kappa-psi-polynomials of complementary degree as well
      kpinters=True
      (B,kppolynomials)=kpintersection_matrix(g,N,_sage_const_3 *g-_sage_const_3 +N-r)
      A=block_matrix([[A],[B]],subdivide=False)
    

      
    if A.rank()<ngens:
      print('Matrix rank in computation of '+repr((g,dat))+' not full!\n')
    
    
    # now we must compute the pullbacks of ( forgetful_* \bar H ) to the boundary, collect in vector b
    # if kpinters, we also must compute the intersection numbers with polynomials in kppolynomials and concatenate to b
    b=[]
    forgetmarks=list(set(range(_sage_const_1 ,n+_sage_const_1 ))-set(markings))
    bar_H=prodHclass(stgraph([g],[list(range(_sage_const_1 ,N+_sage_const_1 ))],[]),[decHstratum(stgraph([g],[list(range(_sage_const_1 ,N+_sage_const_1 ))],[]), {_sage_const_0 :(g,dat)}, [[_sage_const_0 ,markingdictionary]])])
    
    for bdry in bdrydiv:
      if len(bdry.genera)!=_sage_const_1 :
        b+=list(bar_H.gamma0_pullback(bdry).toprodtautclass().totensorTautbasis(_sage_const_3 *g-_sage_const_3 +N-r,vecout=True))

    if irrpullback:
      b+=list(bar_H.gamma0_pullback(irrbd).toprodtautclass().totensorTautbasis(_sage_const_3 *g-_sage_const_3 +N-r,vecout=True))        
    
    
    if kpinters:
      b+=[(bar_H*tautclass([kppo])).evaluate() for kppo in kppolynomials]

    
    # finally, the coefficients x of ( forgetful_* \bar H ) in basis gens are the solutions of A*x=b
    # the matrix A likely has many more rows than ngens, providing some redundancy
    # if its rank is smaller than ngens, we cannot obtain ( forgetful_* \bar H ) like this (at most restrict it to affine subvectorspace)
    # this CANNOT happen if both degree r and degree 3*g-3+N-r are completely tautological!
    try:
      x = A.solve_right(vector(b))
    except ValueError:
      global examA
      examA=A
      global examb
      examb=b
      global Hexam
      Hexam=(g,dat,method,vecout,redundancy,markings)   
      raise ValueError('In Hidentify, matrix equation has no solution')   
        
    result=Tautvb_to_tautclass(x,g,N,_sage_const_3 *g-_sage_const_3 +N-r)
    result.rename_legs(markingdictionary,rename=True)
  
  # return section
  if not found:
    if (g,dat) not in Hdatabase:
      Hdatabase[(g,dat)]={}
    Hdatabase[(g,dat)][tuple(markings)]=deepcopy(result)
  
  if vecout:
    result.rename_legs(invmarkingdictionary,rename=True)
    return result.toTautvect(g,len(markings),_sage_const_3 *g-_sage_const_3 +len(markings)-r)
  else:    
    return result    

# if bdry is given (as a stgraph with exactly one edge) it computes the matrix whose columns are the pullback of our preferred generating_indices(g,n,d) to the divisor bdry, identified in the (tensor product) Tautbasis
# if bdry=None, concatenate all matrices for all possible boundary divisors (in their order inside list_strata(g,n,1))
# if additionally irrbdry=False, omit the pullback to the irreducible boundary, since there computations get more complicated
def pullback_matrix(g,n,d,bdry=None,irrbdry=True):
  genindices = generating_indices(g,n,d)  # indices of generators corresponding to columns of A
  strata = DR.all_strata(g, d, tuple(range(_sage_const_1 ,n+_sage_const_1 )))
  gens=[Graphtodecstratum(strata[i]) for i in genindices]
  ngens=len(genindices)
  
  if bdry==None:
    A=matrix(_sage_const_0 ,ngens)
    bdrydiv=list_strata(g,n,_sage_const_1 )
    
    for bdry in bdrydiv:
      if irrbdry or len(bdry.genera)!=_sage_const_1 :
        A=block_matrix([[A],[pullback_matrix(g,n,d,bdry)]],subdivide=False)
    return A
  else:
    pullbacks=[bdry.boundary_pullback(cl).totensorTautbasis(d,True) for cl in gens]    
    return matrix(pullbacks).transpose()

# computes the matrix B whose columns are the intersection numbers of our preferred generating_indices(g,n,d) with the list kppolynomials of kappa-psi-polynomials that conveniently are exactly those generating_indices of opposite degree having underlying trivial graph
# returns the tuple (B,kppolynomials), where the latter are decstrata
def kpintersection_matrix(g,n,d):
  genindices = generating_indices(g,n,d)  # indices of generators corresponding to columns of A
  strata = DR.all_strata(g,d,tuple(range(_sage_const_1 ,n+_sage_const_1 )))
  opstrata = DR.all_strata(g,_sage_const_3 *g-_sage_const_3 +n-d,tuple(range(_sage_const_1 ,n+_sage_const_1 )))
  opgenindices = list(range(len(opstrata))) #generating_indices(g,n,3*g-3+n-d)  # indices of generators in opposite degree
  
  gens=[Graphtodecstratum(strata[i]) for i in genindices]
  ngens=len(genindices)
  kppolynomials=[Graphtodecstratum(opstrata[i]) for i in opgenindices]
  kppolynomials=[s for s in kppolynomials if s.gamma.edges==[]]
  
  B=[[(gen*s).evaluate() for gen in gens] for s in kppolynomials]
  return (matrix(B),kppolynomials)

# represents a tautological class on the product of several spaces \bar M_{g_i, n_i}, which correspond to the vertices of a stgraph gamma
# one way to obtain such a prodtautclass is to pull back a tautclass under the boundary map for gamma
# the product class is stored as a list terms, where each entry is of the form [ds(0),ds(1), ..., ds(m)], where ds(j) are decstratums 
# CAREFUL: marking-names on the ds(j) are 1,2,3, ... corresponding to legs 0,1,2, ... in gamma.legs[j] 
# if argument prodtaut is given, it is a list (of length = len(gamma.genera)) of tautclasses with correct leg names and this should produce the prodtautclass given as pushforward of the product of these classes
# that is, self.terms is the list of all possible choices of a decstratum from the various factors
class prodtautclass:
  def __init__(self, gamma, terms=None, protaut=None):
    self.gamma = gamma
    if terms!=None:
      self.terms = terms
    elif protaut!=None:
      declists=[t.terms for t in protaut]
      self.terms=[deepcopy(list(c)) for c in itertools.product(*declists)]
    else:
      self.terms = [[decstratum(stgraph([self.gamma.genera[i]],[list(range(_sage_const_1 ,len(self.gamma.legs[i])+_sage_const_1 ))],[])) for i in range(len(self.gamma.genera))]]
    
  # returns the pullback of self under the forgetful map which forgot the markings in the list newmark
  # rename: if True, checks if newmark contains leg names already taken for edges
  #def forgetful_pullback(self,newmark,rename=True):
   # return sum([c.forgetful_pullback(newmark,rename) for c in self.terms])      
  
  # returns the tautclass obtained by pushing forward under the gluing map associated to gamma
  def pushforward(self):
    result=tautclass([])
    for t in self.terms:
      # we have to combine the graphs from all terms such that there are no collisions of half-edge names
      #   * genera will be the concatenation of all t[i].gamma.genera
      #   * legs will be the concatenation of renamed versions of the t[i].gamma.legs
      #   * edges will be the union of the renamed edge-lists from the elements t[i] and the edge-list of self.gamma
      maxleg=max(self.gamma.leglist()+[0])+_sage_const_1 
      genera=[]
      legs=[]
      edges=deepcopy(self.gamma.edges)
      numvert=sum([len(s.gamma.genera) for s in t]) # total number of vertices in new graph
      poly = onekppoly(numvert)
      
      for i in range(len(t)):
        # s is a decstratum
        s=t[i]
        gr=s.gamma
        start=len(genera)
        genera+=deepcopy(gr.genera)
        
        # create the renaming-dictionary
        renamedic={j+_sage_const_1 :self.gamma.legs[i][j] for j in range(len(self.gamma.legs[i]))}
        for (e0,e1) in gr.edges:
          renamedic[e0]=maxleg
          renamedic[e1]=maxleg+_sage_const_1 
          maxleg+=_sage_const_2 
        
        legs+=[[renamedic[l] for l in ll] for ll in gr.legs]  
        edges+=[(renamedic[e0],renamedic[e1]) for (e0,e1) in gr.edges]
        
        grpoly=deepcopy(s.poly)
        grpoly.rename_legs(renamedic)
        grpoly.expand_vertices(start,numvert)
        poly*=grpoly
      result+=tautclass([decstratum(stgraph(genera,legs,edges),poly=poly)])      
    return result
  
  # given a stgraph gamma0 and (dicv,dicl) a morphism from self.gamma to gamma0 (i.e. self.gamma is a specialization of gamma0)
  # returns the prodtautclass on gamma0 obtained by the partial pushforward along corresponding gluing maps
  def partial_pushforward(self,gamma0,dicv,dicl):
    gamma=self.gamma
    preimv=[[] for v in gamma0.genera]
    for w in dicv:
      preimv[dicv[w]].append(w)
    usedlegs=dicl.values()  
    
    # now create list of preimage-graphs, where leg-names and orders are preserved so that decstratums can be used unchanged
    preimgr=[]
    for v in range(len(gamma0.genera)):
      preimgr.append(stgraph([gamma.genera[w] for w in preimv[v]],[gamma.legs[w] for w in preimv[v]],[e for e in gamma.edges if (gamma.vertex(e[0]) in preimv[v] and gamma.vertex(e[1]) in preimv[v]) and not (e[0] in usedlegs or e[1] in usedlegs)]))
    
    # now go through self.terms, split decstrata onto preimgr (creating temporary prodtautclasses)
    # push those forward obtaining tautclasses on the moduli spaces corresponding to the vertices of gamma0 (but wrong leg labels)
    # rename them according to the inverse of dicl, then multiply all factors together using distributivity
    result=prodtautclass(gamma0,[])
    rndics=[{dicl[gamma0.legs[v][j]]:j+_sage_const_1  for j in range(len(gamma0.legs[v]))} for v in range(len(gamma0.genera))]
    for t in self.terms:
      tempclasses=[prodtautclass(preimgr[v],[[t[i] for i in preimv[v]]]) for v in range(len(gamma0.genera))]
      temppush=[s.pushforward() for s in tempclasses]
      for v in range(len(gamma0.genera)):
        temppush[v].rename_legs(rndics[v],rename=True)
      for comb in itertools.product(*[tp.terms for tp in temppush]):
        result.terms.append(list(comb))
    return result    
  
  # converts self into a prodHclass on gamma0=self.gamma, all spaces being distinct with trivial Hurwitz datum (for the trivial group) and not having any identifications among themselves
  def toprodHclass(self):
    gamma0=deepcopy(self.gamma)
    terms=[]
    trivgp=PermutationGroup([()])
    trivgpel=trivgp[0]
    result=prodHclass(gamma0,[])
    
    for t in self.terms:
      # we have to combine the graphs from all terms such that there are no collisions of half-edge names
      #   * genera will be the concatenation of all t[i].gamma.genera
      #   * legs will be the concatenation of renamed versions of the t[i].gamma.legs
      #   * edges will be the union of the renamed edge-lists from the elements t[i] and the edge-list of self.gamma
      dicv0={}
      dicl0={l:l for l in self.gamma.leglist()}
      spaces={}
      vertdata=[]
      
      maxleg=max(self.gamma.leglist()+[0])+_sage_const_1 
      genera=[]
      legs=[]
      edges=deepcopy(self.gamma.edges)
      numvert=sum([len(s.gamma.genera) for s in t]) # total number of vertices in new graph
      poly = onekppoly(numvert)
      
      for i in range(len(t)):
        # s is a decstratum
        s=t[i]
        gr=s.gamma
        start=len(genera)
        genera+=deepcopy(gr.genera)
        dicv0.update({j:i for j in range(start,len(genera))})
        
        # create the renaming-dictionary
        renamedic={j+_sage_const_1 :self.gamma.legs[i][j] for j in range(len(self.gamma.legs[i]))}
        for (e0,e1) in gr.edges:
          renamedic[e0]=maxleg
          renamedic[e1]=maxleg+_sage_const_1 
          maxleg+=_sage_const_2 
        
        legs+=[[renamedic[l] for l in ll] for ll in gr.legs]  
        edges+=[(renamedic[e0],renamedic[e1]) for (e0,e1) in gr.edges]
        spaces.update({j:[genera[j],HurwitzData(trivgp,[(trivgpel,_sage_const_1 ,_sage_const_0 ) for counter in range(len(legs[j]))])] for j in range(start,len(genera))})
        vertdata+=[[j,{legs[j][lcount]:lcount+_sage_const_1  for lcount in range(len(legs[j]))}] for j in range(start,len(genera))]
        
        grpoly=deepcopy(s.poly)
        grpoly.rename_legs(renamedic)
        grpoly.expand_vertices(start,numvert)
        poly*=grpoly
      
      gamma=stgraph(genera,legs,edges)
      
      result.terms.append(decHstratum(gamma,spaces,vertdata,dicv0,dicl0,poly))
    return result            
  
  
  # takes a set of vertices of self.gamma and a prodtautclass prodcl on a graph with the same number of vertices as the length of this list - returns the multiplication of self with a pullback (under a suitable projection) of prodcl
  # more precisely: let vertices=[v_1, ..., v_r], then for j=1,..,r the vertex v_j in self.gamma has same genus and number of legs as vertex j in prodcl.gamma
  # multiply the pullback of these classes accordingly
  def factor_pullback(self,vertices,prodcl):
    other=prodtautclass(self.gamma)  # initialize with 1-class
    defaultterms=[other.terms[0][i] for i in range(len(self.gamma.genera))]  #collect 1-terms on various factors here
    other.terms=[]
    for t in prodcl.terms:
      newterm=deepcopy(defaultterms)
      for j in range(len(vertices)):
        newterm[vertices[j]]=t[j]
      other.terms.append(newterm)
    return self*other    
    
  def __neg__(self):
    return (-_sage_const_1 )*self  

  def __add__(self,other):      
    if other==_sage_const_0 :
      return deepcopy(self)    
    new=deepcopy(self)
    new.terms+=deepcopy(other.terms)
    return new.consolidate()
  def __radd__(self,other):
    if other==_sage_const_0 :
      return self
    else:
      return self+other  
  
  def __iadd__(self,other):
    if other==_sage_const_0 :
      return self
    if (not isinstance(other,prodtautclass)) or (not (other.gamma == self.gamma)):
      print('Error, summing two prodtautclasses on different graphs!')
      print(self.gamma)
      print(other.gamma)
      print((self.gamma.__eq__(other.gamma), (other.gamma == self.gamma)))
      raise ValueError('Prodtautclasses on different graphs')
      
    self.terms+=other.terms  
    return self
  
  def __mul__(self,other):
    return self.__rmul__(other)    
  
  def __imul__(self,other): 
    if isinstance(other,prodtautclass):
      self.terms=(self.__rmul__(other)).terms
      return self
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational) or isinstance(other,int):
    else:
      for t in self.terms:
        t[0]*=other 
      return self  
    
  def __rmul__(self,other): 
    if isinstance(other,prodtautclass):
      # multiply the decstratums on each vertex together separately
      if not (other.gamma == self.gamma):
        print('Error, trying to multiply two prodtautclasses on different graphs!')
        print(self)
        print(other)
        
      result = prodtautclass(self.gamma,[])
      for T1 in self.terms:
        for T2 in other.terms:
          # go through vertices, multiply decstratums -> obtain tautclasses
          # in the end: must output all possible combinations of those tautclasses    
          vertextautcl=[]
          for v in range(len(self.gamma.genera)):
            vertextautcl.append((T1[v]*T2[v]).terms)
          for choice in itertools.product(*vertextautcl):
            result+=prodtautclass(self.gamma,[list(choice)])
      return result      
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational) or isinstance(other,int):
    else:
      new=deepcopy(self)
      for t in new.terms:
        t[0]=other*t[0]
      return new


  def dimension_filter(self):
    for t in self.terms:
      for s in t:
        s.dimension_filter()
    return self.consolidate()
  
  def consolidate(self):
    revrange=list(range(len(self.terms)))
    revrange.reverse()
    for i in revrange:
      for s in self.terms[i]:
        if len(s.poly.monom)==_sage_const_0 :
          self.terms.pop(i)
          break
    return self            
            
  def __repr__(self):
    s='Outer graph : ' + repr(self.gamma) +'\n'
    for i in range(len(self.terms)):
      for j in range(len(self.terms[i])):
        s+='Vertex '+repr(j)+' :\n'+repr(self.terms[i][j])+'\n'
      s+='\n\n'  
    return s.rstrip('\n\n')
  
  # returns the cohomological degree 2r part of self, where we see self as a cohomology vector in 
  # H*(\bar M_{g1,n1} x \bar M_{g2,n2} x ... x \bar M_{gm,nm}) with m the number of vertices of self.gamma
  # currently only implemented for m=1 (returns vector) or m=2 (returns list of matrices of length r+1)
  # if vecout=True, in the case m=2 a vector is returned that is the concatenation of all row vectors of the matrices
  # TODO: make r optional argument?
  def totensorTautbasis(self,r,vecout=False):
    if len(self.gamma.genera)==_sage_const_1 :
      g=self.gamma.genera[0]
      n=len(self.gamma.legs[0])
      result = vector(QQ,len(generating_indices(g,n,r)))
      for t in self.terms:
        # t is a one-element list containing a decstratum
        result+=t[0].toTautbasis(g,n,r)
      return result  
    if len(self.gamma.genera)==_sage_const_2 :
      g1=self.gamma.genera[0]
      n1=len(self.gamma.legs[0])  
      g2=self.gamma.genera[1]
      n2=len(self.gamma.legs[1])   
      rmax1=_sage_const_3 *g1-_sage_const_3 +n1
      rmax2=_sage_const_3 *g2-_sage_const_3 +n2
      
      rmin=max(_sage_const_0 ,r-rmax2)  # the degree r1 in the first factor can only vary between rmin and rmax
      rmax=min(r,rmax1)
      
      result=[matrix(QQ,_sage_const_0 ,_sage_const_0 ) for i in range(rmin)]
      
      for r1 in range(rmin,rmax+_sage_const_1 ):
        M=matrix(QQ,len(generating_indices(g1,n1,r1)),len(generating_indices(g2,n2,r-r1)))
        for t in self.terms:
          # t is a list [d1,d2] of two decstratums
          vec1=t[0].toTautbasis(g1,n1,r1)
          vec2=t[1].toTautbasis(g2,n2,r-r1)
          M+=matrix(vec1).transpose()*matrix(vec2)
        result.append(M)  
      
      result+=[matrix(QQ,_sage_const_0 ,_sage_const_0 ) for i in range(rmax+_sage_const_1 ,r+_sage_const_1 )]
      
      if vecout:
        return vector([M[i,j] for M in result for i in range(M.nrows()) for j in range(M.ncols()) ])
      else:
        return result  
      
    if len(self.gamma.genera)>_sage_const_2 :
      print('totensorTautbasis not yet implemented on graphs with more than two vertices')
      return _sage_const_0 

# converts a decstratum or tautclass to a vector in Pixton's basis
# tries to reconstruct g,n,r from first nonzero term on the first decstratum
# if they are explicitly given, only extract the part of D that lies in right degree, ignore others
def converttoTautvect(D,g=None,n=None,r=None):
  #global copyD
  #copyD=(D,g,n,r)
  if isinstance(D,tautclass):
    if len(D.terms)==_sage_const_0 :
      if (g==None or n==None or r==None):
        print('Unable to identify g, n, r for empty tautclass')
        return _sage_const_0 
      else:
        return vector(QQ,DR.num_strata(g,r,tuple(range(_sage_const_1 ,n+_sage_const_1 ))))
    if g==None:
      g=D.terms[0].gamma.g()
    if n==None:
      n=len(D.terms[0].gamma.list_markings())
    if r==None:
      polydeg=D.terms[0].poly.deg()
      if polydeg!=None:
        r=len(D.terms[0].gamma.edges)+polydeg
    result=converttoTautvect(D.terms[0],g,n,r)
    for i in range(_sage_const_1 ,len(D.terms)):
      result+=converttoTautvect(D.terms[i],g,n,r)
    return result
  if isinstance(D,decstratum):
    D.dimension_filter()
    if g==None:
      g=D.gamma.g()
    if n==None:
      n=len(D.gamma.list_markings())    
    if len(D.poly.monom)==_sage_const_0 :
      if (r==None):
        print('Unable to identify r for empty decstratum')
        return _sage_const_0 
      else:
        return vector(QQ,DR.num_strata(g,r,tuple(range(_sage_const_1 ,n+_sage_const_1 ))))
    if r==None:
      polydeg=D.poly.deg()
      if polydeg!=None:
        r=len(D.gamma.edges)+polydeg    
    # just assume now that g,n,r are given
    length=DR.num_strata(g,r,tuple(range(_sage_const_1 ,n+_sage_const_1 )))
    markings=tuple(range(_sage_const_1 ,n+_sage_const_1 ))
    result = vector(QQ,length)
    graphdegree=len(D.gamma.edges)
    for (kappa,psi,coeff) in D.poly:
      if graphdegree + sum([sum((j+_sage_const_1 )*kvec[j] for j in range(len(kvec)) ) for kvec in kappa])+sum(psi.values()) == r:
        try:
          pare=coeff.parent()
        except:
          pare=QQ          
        result+=vector(pare,length,{DR.num_of_stratum(Pixtongraph(D.gamma,kappa,psi),g,r,markings):coeff})
    return result

# returns a Pixton-style graph given a stgraph G and data kappa and psi as in kppoly    
def Pixtongraph(G,kappa,psi):
  firstcol=[-_sage_const_1 ]
  for v in range(len(G.genera)):
    entry=G.genera[v]
    for k in range(len(kappa[v])):
      entry+=kappa[v][k]*(DR.X)**(k+_sage_const_1 )
    firstcol.append(entry)
  columns=[firstcol]
  
  for l in G.list_markings():
    vert=G.vertex(l)
    entry = _sage_const_1 
    if l in psi:
      entry+=psi[l]*DR.X
    columns.append([l]+[_sage_const_0  for i in range(vert)]+[entry]+[_sage_const_0  for i in range(len(G.genera)-vert-_sage_const_1 )] )  
  for (e0,e1) in G.edges:
    v0=G.vertex(e0)
    v1=G.vertex(e1)
    if v0==v1:
      entry=_sage_const_2 
      if (psi.get(e0,_sage_const_0 )!=_sage_const_0 ) and (psi.get(e1,_sage_const_0 )==_sage_const_0 ):
        entry+=psi[e0]*DR.X
      if (psi.get(e1,_sage_const_0 )!=_sage_const_0 ) and (psi.get(e0,_sage_const_0 )==_sage_const_0 ):
        entry+=psi[e1]*DR.X
      if (psi.get(e0,_sage_const_0 )!=_sage_const_0 ) and (psi.get(e1,_sage_const_0 )!=_sage_const_0 ):
        if psi[e0]>=psi[e1]:
          entry+=psi[e0]*DR.X  + psi[e1]*(DR.X)**_sage_const_2 
        else:
          entry+=psi[e1]*DR.X  + psi[e0]*(DR.X)**_sage_const_2 
      columns.append([0]+[_sage_const_0  for i in range(v0)]+[entry]+[_sage_const_0  for i in range(len(G.genera)-v0-_sage_const_1 )] )  
    else:
      col = [_sage_const_0  for i in range(len(G.genera)+_sage_const_1 )] 
      entry = _sage_const_1 
      if e0 in psi:
        entry+=psi[e0]*DR.X
      col[v0+_sage_const_1 ]=entry
      
      entry = _sage_const_1 
      if e1 in psi:
        entry+=psi[e1]*DR.X
      col[v1+_sage_const_1 ]=entry
      columns.append(col)
    
  M=matrix(columns).transpose()
  return DR.Graph(M)

# converts vector v in generating set all_strata(g,r,(1,..,n)) to preferred basis computed by generating_indices(g,n,r)
def Tautvecttobasis(v,g,n,r,moduli='st'):  
  if (_sage_const_2 *g-_sage_const_2 +n<=_sage_const_0 ) or (r<_sage_const_0 ) or (r>_sage_const_3 *g-_sage_const_3 +n):
    return vector([])
  vecs=genstobasis(g,n,r)
  res=vector(QQ,len(vecs[0]))
  for i in range(len(v)):
    if v[i]!=_sage_const_0 :
      res+=v[i]*vecs[i]
  if moduli == 'st':
    return res
  if moduli == 'ct':
    W=ct_space(g,n,r)
    reslen=len(res)
    veclist=[res[i] * W( vector(QQ,reslen,{i:1}) ) for i in range(reslen) if not res[i].is_zero()]  
    # this strange form is necessary if entries of v are not in QQ, but polynomials etc.
    return sum(veclist)

# gives a list whose ith entry is the representation of the ith generator in all_strata(g,r,(1,..,n)) in the preferred basis computed by generating_indices(g,n,r)

@cached_function
def genstobasis(g, n, r):
    generating_indices(g, n, r, True)
    return genstobasis(g, n, r)


# converts Tautvector to tautclass
def Tautv_to_tautclass(v,g,n,r):
  strata = DR.all_strata(g,r,  tuple(range(_sage_const_1 ,n+_sage_const_1 ))  )
  stratmod=[]
  for i in range(len(v)):
    if v[i]==_sage_const_0 :
      continue
    currstrat=Graphtodecstratum(strata[i])
    currstrat=v[i]*currstrat
    stratmod.append(currstrat)
        
  return tautclass(stratmod)   

# converts vector in generating_indices-basis to tautclass
def Tautvb_to_tautclass(v,g,n,r):
  genind=generating_indices(g,n,r )
  strata = DR.all_strata(g, r,  tuple(range(_sage_const_1 ,n+_sage_const_1 ))  )
  stratmod=[]
  for i in range(len(v)):
    if v[i]==_sage_const_0 :
      continue
    currstrat=Graphtodecstratum(strata[genind[i]])
    currstrat.poly*=v[i]
    stratmod.append(currstrat)
        
  return tautclass(stratmod)   


# represents a sum of gluing pushforwards of pushforwards of fundamental classes of Hurwitz spaces under products of forgetful morphisms
# this is all relative to a fixed graph gamma0
class prodHclass:
  def __init__(self, gamma0, terms):
    self.gamma0 = gamma0
    self.terms = terms    

  def __neg__(self):
    return (-_sage_const_1 )*self  

  def __add__(self,other):        
    if other==_sage_const_0 :
      return deepcopy(self)  
    if isinstance(other,prodHclass) and other.gamma0==self.gamma0:
      new=deepcopy(self)
      new.terms+=deepcopy(other.terms)
      return new.consolidate()
  def __radd__(self,other):
    if other==_sage_const_0 :
      return self
    else:
      return self+other  
  
  def __iadd__(self,other):
    if other==_sage_const_0 :
      return self
    if isinstance(other,prodHclass) and other.gamma0==self.gamma0:
      self.terms+=other.terms  #TODO: should we use a deepcopy here?
    else:
      print('Error, summing two prodHclasses on different graphs!')
      print(self.gamma0)
      print(other.gamma0)
      print((self.gamma0.__eq__(other.gamma0), (other.gamma0 == self.gamma0)))
    return self
  
  def __mul__(self,other): 
    if isinstance(other,tautclass) or isinstance(other,decstratum):
      return self.__rmul__(other)  
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational) or isinstance(other,int):
    else:
      new=deepcopy(self)
      for t in new.terms:
        t[0]=other*t[0]
      return new

      
  def __rmul__(self,other): 
    if isinstance(other,tautclass) or isinstance(other,decstratum):
      pbother = self.gamma0.boundary_pullback(other)  # this is a prodtautclass on self.gamma0 now
      pbother = pbother.toprodHclass()  # this is a prodHclass with gamma0 = self.gamma0 now, but we know that all spaces are \bar M_{g_i,n_i}, which we use below!
      result = prodHclass(deepcopy(self.gamma0),[])
      for t in pbother.terms:
        # t is a decHstratum and (t.dicv0,t.dicl0) is a morphism from t.gamma to self.gamma0
        # we pull back self along this morphism to get a prodHclass on t.gamma
        temppullback = self.gamma0_pullback(t.gamma,t.dicv0,t.dicl0)
        
        # now it remains to distribute the kappa and psi-classes from t.poly (living on t.gamma) to the terms of temppullback
        for s in temppullback.terms:
          # s is now a decHstratum and (s.dicv0,s.dicl0) describes a map s.gamma -> t.gamma
          s.poly*=t.poly.graphpullback(s.dicv0,s.dicl0)
          # rearrange s to be again a decHstratum with respect to gamma0
          s.dicv0={v : t.dicv0[s.dicv0[v]] for v in s.dicv0}
          s.dicl0={l : s.dicl0[t.dicl0[l]] for l in t.dicl0}
        result.terms+=temppullback.terms
      return result  
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational) or isinstance(other,int):
    else:
      new=deepcopy(self)
      for t in new.terms:
        t[0]=other*t[0]
      return new
  
  
  # evaluates self against the fundamental class of the ambient space (of self.gamma0), returns a rational number
  def evaluate(self):
    return sum([t.evaluate() for t in self.terms])
  
  
  
  # tries to convert self into a prodtautclass on the graph gamma0
  # Note: since not all Hurwitz spaces have tautological fundamental class and since not all diagonals have tautological Kunneth decompositions, this will not always work
  def toprodtautclass(self):
    result=prodtautclass(deepcopy(self.gamma0),[])
    for t in self.terms:
      # create a prodtautclass on t.gamma, then do partial pushforward under (t.dicv0,t.dicl0)
      tempres=decstratum(deepcopy(t.gamma),poly=deepcopy(t.poly))
      tempres=tempres.convert_to_prodtautclass()
      
      # now group vertices of t.gamma according to the spaces they access
      # create diagonals and insert the identification of the Hurwitz stack fundamental class
      # make sure that for this you use the version forgetting the most markings possible
      spacelist={a:[] for a in t.spaces}
      for v in range(len(t.gamma.genera)):
        spacelist[t.vertdata[v][0]].append(v)
      for a in spacelist:
        if spacelist[a]==[]:
          spacelist.pop(a)
      
      for a in spacelist:
        # find out which of the markings 1, .., N of the space containing the Hurwitz cycle are used
        usedmarks=set()
        for v in spacelist[a]:
          usedmarks.update(set(t.vertdata[v][1].values()))
        usedmarks=list(usedmarks)
        usedmarks.sort()  
        rndic={usedmarks[i]:i+_sage_const_1  for i in range(len(usedmarks))}
        
        Hclass=Hidentify(t.spaces[a][0],t.spaces[a][1],markings=usedmarks)
        Hclass.rename_legs(rndic,rename=True)
        
        legdics=[{l:rndic[t.vertdata[v][1][l]] for l in t.gamma.legs[v]} for v in spacelist[a]]
        diagclass=forgetful_diagonal(t.spaces[a][0],len(usedmarks),[t.gamma.legs[v] for v in spacelist[a]],legdics,T=Hclass)
        
        tempres=tempres.factor_pullback(spacelist[a],diagclass)

      
      tempres=tempres.partial_pushforward(self.gamma0,t.dicv0,t.dicl0)
      result+=tempres
    return result
      
  # given a different graph gamma1 carrying a gamma0-structure encoded by dicv, dicl, pull back self under this structure and return a prodHclass with underlying graph gamma1  
  def gamma0_pullback(self,gamma1,dicv=None,dicl=None):
    gamma0=self.gamma0
    
    if dicv==None:
      if len(gamma0.genera)==_sage_const_1 :
        dicv={v:_sage_const_0  for v in range(len(gamma1.genera))}
      else:
        print('Error: dicv not uniquely determined')
    if dicl==None:
      if len(gamma0.edges)==_sage_const_0 :
        dicl={l:l for l in gamma0.leglist()}
      else:
        print('Error: dicl not uniquely determined')
    
    # Step 1: factor the map gamma1 -> gamma0 in a series of 1-edge degenerations
    # TODO: choose a smart order to minimize computations later (i.e. start w/ separating edges with roughly equal genus on both sides
    
    imdicl=dicl.values()
    extraedges=[e for e in gamma1.edges if e[0] not in imdicl]
    delta_e = len(gamma1.edges) - len(gamma0.edges)
    if delta_e != len(extraedges):
      print('Warning: edge numbers')
      global exampullb
      exampullb=(deepcopy(self),deepcopy(gamma1),deepcopy(dicv),deepcopy(dicl))
      raise ValueError('Edge numbers')
    edgeorder=list(range(delta_e))
    contredges=[extraedges[i] for i in edgeorder]
    
    contrgraph=[gamma1]
    actvert=[]
    edgegraphs=[]
    vnumbers=[]
    contrdicts=[]
    vimages=[dicv[v] for v in range(len(gamma1.genera))]
    count=_sage_const_0 
    for e in contredges:
      (gammatild,av,edgegraph,vnum,diccv)=contrgraph[count].contract_edge(e,adddata=True)
      contrgraph.append(gammatild)
      actvert.append(av)
      edgegraphs.append(edgegraph)
      vnumbers.append(vnum)
      contrdicts.append(diccv)
      if len(vnum)==_sage_const_2 :
        vimages.pop(vnum[1])
      count+=_sage_const_1 
    contrgraph.reverse()
    actvert.reverse()
    edgegraphs.reverse()
    vnumbers.reverse()  
    contrdicts.reverse()
    

    # Step 2: pull back the decHstratum t one edge-degeneration at a time 
    # Note that this will convert the decHstratum into a prodHclass, so we need to take care of all the different terms in each step
    
    # First we need to adapt (a copy of) self so that we take into account that gamma0 is isomorphic to the contracted version of gamma1
    # The gamma0-structure on all terms of self must be modified to be a contrgraph[0]-structure
    result=deepcopy(self)
    result.gamma0=contrgraph[0]
    dicvisom={dicv[vimages[v]]:v for v in range(len(gamma0.genera))} # gives isomorphism V(gamma0) -> V(contrgraph[0])
    diclisom={dicl[l]:l for l in dicl} # gives isomorphism L(contrgraph[0]) -> L(gamma0)
    for t in result.terms:
      t.dicv0={v:dicvisom[t.dicv0[v]] for v in t.dicv0}
      t.dicl0={l:t.dicl0[diclisom[l]] for l in diclisom} 
    # dicv, dicl should have served their purpose and should no longer appear below
    
    for edgenumber in range(delta_e):
      newresult=prodHclass(contrgraph[edgenumber+_sage_const_1 ],[])
      gam0=contrgraph[edgenumber]  # current gamma0, we now pull back under contrgraph[edgenumber+1] -> gam0
      av=actvert[edgenumber] # vertex in gam0 where action happens
      diccv=contrdicts[edgenumber] # vertex dictionary for contrgraph[edgenumber+1] -> gam0 
      diccvinv={diccv[v]:v for v in diccv}  # section of diccv: bijective if loop is added, otherwise assigns one of the preimages to the active vertex
      vextractdic={v:vnumbers[edgenumber][v] for v in range(len(vnumbers[edgenumber]))}
      
      
      for t in result.terms:
        gamma=t.gamma
        
        # Step 2.1: extract the preimage of the active vertex inside t.gamma
        actvertices=[v for v in range(len(gamma.genera)) if t.dicv0[v]==av]
        #global exsubvar
        #exsubvar=(t,gamma,actvertices,gam0, av)
        #avloops=[e for e in gam0.edges if (e[0] in gam0.legs[av] and e[1] in gam0.legs[av])]
        #outlegs=set(gam0.legs[av])-set([e[0] for e in avloops] + [e[1] for e in avloops])
        (gammaprime,dicvextract,diclextract) =gamma.extract_subgraph(actvertices,outgoing_legs=[t.dicl0[l] for l in gam0.legs[av]],rename=False)
        
        dicvextractinv={dicvextract[v]:v for v in dicvextract}
        # dicvextract maps vertex numbers in gamma to  vertex-numbers in gammaprime
        # diclextract not needed since rename=False
        
        # Step 2.2: find the common degenerations of this preimage and the one-edge graph relevant for this step
        # We need to rename edgegraphs[edgenumber] to match the leg-names in gammaprime
        egraph=deepcopy(edgegraphs[edgenumber])
        eshift=max(list(t.dicl0.values())+[0])+_sage_const_1 
        egraph.rename_legs(t.dicl0,shift=eshift)
        
        #(gammaprime,dicvextract,diclextract) =gamma.extract_subgraph(actvertices,outgoing_legs=[l for l in egraph.list_markings()],rename=False)
        
        #dicvextractinv={dicvextract[v]:v for v in dicvextract}
        # dicvextract maps vertex numbers in gamma to  vertex-numbers in gammaprime
        # diclextract not needed since rename=False
        
        commdeg=common_degenerations(gammaprime,egraph,modiso=True,rename=True)
        
        
        (e0,e1)=egraph.edges[0]
        for (gammadeg,dv1,dl1,dv2,dl2) in commdeg:
          if len(gammadeg.edges)==len(gammaprime.edges):
            # Step 2.3a: if gammadeg isomorphic to gammaprime, we have excess intersection, introducing -psi - psi'
            term=deepcopy(t)
            numvert=len(gamma.genera)
            dl1inverse={dl1[l]:l for l in dl1}
            term.poly*=-(psicl(dl1inverse[dl2[e0]],numvert)+psicl(dl1inverse[dl2[e1]],numvert))
            # adapt term.dicv0 and term.dicl0
            
            # term.dicv0 must be lifted along the contraction map using diccvinv outside of the active area gammaprime; there we use dv2
            dv1inverse={dv1[v]:v for v in dv1}  #TODO: is this what we want?
            term.dicv0={v:diccvinv[term.dicv0[v]] for v in term.dicv0}
            term.dicv0.update({v:vextractdic[dv2[dv1inverse[dicvextract[v]]]] for v in actvertices})
            
            # term.dicl0 should now assign to the two half-edges that are new the corresponding edge in term.gamma
            term.dicl0[e0-eshift]= dl1inverse[dl2[e0]]
            term.dicl0[e1-eshift]= dl1inverse[dl2[e1]]
            
            newresult.terms.append(term)
          else:  
            # Step 2.3b: else there is a real degeneration going on
            # This means we need to find the vertex of gamma where this new edge would appear,
            # then check if the Hurwitz space glued to this spot admits a compatible degeneration.
            # Note that here we must take note that we possibly forgot some markings of this Hurwitz space.
            
            
            vactiveprime=dv1[gammadeg.vertex(dl2[e0])]  # vertex in gammaprime where degeneration occurs
            vactive=dicvextractinv[vactiveprime] # vertex in gamma where degeneration occurs
            
            
            #TODO: it is likely much faster to go through elements Gr of Hbdry, go through edges e of Gr, contract everything except e and check if 
            #compatible with the boundary partition
            (a,spacedicl)=t.vertdata[vactive]
            (gsp,Hsp)=t.spaces[a]
            numHmarks=len(trivGgraph(gsp,Hsp).gamma.legs[0])
            
            #Hbdry=list_Hstrata(gsp,Hsp,1)  # these are the Gstgraphs which might get glued in at vertex vactive (+ other vertices accessing space a)
            #if Hbdry==[]:
            #  continue  # we would require a degeneration, but none can occur
            #numHmarks=len(Hbdry[0].gamma.list_markings())
            #presentmarks=spacedicl.values()
            #forgetmarks=[i for i in range(1,numHmarks) if i not in presentmarks]
            
            # now create list divlist of divisors D living in the space of Hbdry such that we can start enumerating D-structures on elements of Hbdry
            # first we must extract the original boundary graph, which is a subgraph of gammadeg on the preimages of vactiveprime
            vactiveprimepreim=[gammadeg.vertex(dl2[e0]),gammadeg.vertex(dl2[e1])]
            if vactiveprimepreim[0]==vactiveprimepreim[1]:
              vactiveprimepreim.pop(_sage_const_1 )
            # old, possibly faulty: (egr,dvex,dlex) =gammadeg.extract_subgraph(vactiveprimepreim,outgoing_legs=gammaprime.legs[vactiveprime],rename=False)  
            (egr,dvex,dlex) =gammadeg.extract_subgraph(vactiveprimepreim,outgoing_legs=[dl1[le] for le in gammaprime.legs[vactiveprime]],rename=False)  
            
            # rename egr to fit in the space of Hbdry
            rndic={dl1[l]: spacedicl[l] for l in gammaprime.legs[vactiveprime]}
            egr.rename_legs(rndic,shift=numHmarks+_sage_const_1 )
            
            
            degenlist = Hbdrystructures(gsp,Hsp,egr)
            
            for (Gr,mult,degendicv,degendicl) in degenlist:
              term=deepcopy(t)
              speciale_im=term.replace_space_by_Gstgraph(a,Gr,specialv=vactive,speciale=(degendicl[egr.edges[0][0]],degendicl[egr.edges[0][1]]))
              term.poly*=mult
              # term is still a decHstratum with correct gamma, spaces, vertdata and poly, BUT still referencing to ga0
              # now repair dicv0, dicl0

              # term.dicl0 should now assign to the two half-edges that are new the corresponding edge in term.gamma
              dl1inverse={dl1[l]:l for l in dl1}
              eindex=egr.edges[0].index(dl2[e0]+numHmarks+_sage_const_1 )
              term.dicl0[e0-eshift]= speciale_im[eindex]
              term.dicl0[e1-eshift]= speciale_im[_sage_const_1 -eindex]
              
              # term.dicv0 is now reconstructed from dicl0
              # TODO: add more bookkeeping to do this directly???
              term.dicv0=dicv_reconstruct(term.gamma,contrgraph[edgenumber+_sage_const_1 ],term.dicl0)
            
              newresult.terms.append(term)
      
      result=newresult
      
      
    return result  

#  def dimension_filter(self):
#    for t in self.terms:
 #      for s in t:
#        s.dimension_filter()
#    return self.consolidate()
  
  def consolidate(self):
#    revrange=range(len(self.terms))
#    revrange.reverse()
#    for i in revrange:
#      for s in self.terms[i]:
#        if len(s.poly.monom)==0:
#          self.terms.pop(i)
#          break
    return self            
            
  def __repr__(self):
    s='Outer graph : ' + repr(self.gamma0) +'\n'
    for t in self.terms:
      s+=repr(t) + '\n\n'
#    for i in range(len(self.terms)):
#      for j in range(len(self.terms[i])):
#        s+='Vertex '+repr(j)+' :\n'+repr(self.terms[i][j])+'\n'
#      s+='\n\n'  
    return s.rstrip('\n\n')
  
# takes a genus g, a HurwitzData H and a stgraph bdry with exactly one edge, whose markings are a subset of the markings 1,2,..., N of trivGgraph(g,H)
# returns a list with entries (Gr,mult,dicv,dicl) giving all boundary Gstgraphs derived from (g,H) which are specializations of (the forgetful pullback of ) Gr, where
#   * Gr is a Gstgraph
#   * mult is a rational number giving an appropriate multiplicity for the intersection
#   * dicv is a surjective dictionary of the vertices of Gr.gamma to the vertices of bdry
#   * dicl is an injection from the legs of bdry to the legs of Gr.gamma   
def Hbdrystructures(g,H,bdry):
  preHbdry, N = preHbdrystructures(g, H)
  
  if len(bdry.genera)==_sage_const_1 :
    try:
      tempresult=preHbdry[(g)]
    except:
      return []
    (e0,e1)=bdry.edges[0]
    result=[]
    for (Gr,mult,dicv,dicl) in tempresult:
      result.append([Gr,mult,dicv,{e0:dicl[N+_sage_const_1 ], e1:dicl[N+_sage_const_2 ]}])
    return result
      
  
  if len(bdry.genera)==_sage_const_2 :
    presentmarks=bdry.list_markings()
    forgetmarks=[i for i in range(_sage_const_1 ,N+_sage_const_1 ) if i not in presentmarks]
    possi=[[_sage_const_0 ,_sage_const_1 ] for j in forgetmarks]
    
    
    (e0,e1)=bdry.edges[0]
    lgs=deepcopy(bdry.legs)
    ve0=bdry.vertex(e0)
    lgs[ve0].remove(e0)     #leglists stripped of the legs forming the edge of bdry
    lgs[_sage_const_1 -ve0].remove(e1)
    
    result=[]
    
    for distri in itertools.product(*possi):
      # distri = (0,0,1,0,1,1) means that forgetmarks number 0,1,3 go to erg.legs[0] and 2,4,5 go to erg.legs[1]
      lgscpy=deepcopy(lgs)
      lgscpy[0]+=[forgetmarks[j] for j in range(len(forgetmarks)) if distri[j]==_sage_const_0 ]
      lgscpy[1]+=[forgetmarks[j] for j in range(len(forgetmarks)) if distri[j]==_sage_const_1 ]
      
      if bdry.genera[0]>bdry.genera[1] or (bdry.genera[0]==bdry.genera[1] and _sage_const_1  in lgscpy[1]):
        vert=_sage_const_1 
      else:
        vert=_sage_const_0 
      ed=(ve0+vert)%_sage_const_2 
      
          
      try:
        tempresult=preHbdry[(bdry.genera[vert],tuple(sorted(lgscpy[vert])))]
        for (Gr,mult,dicv,dicl) in tempresult:
          result.append((Gr,mult,{j:(dicv[j]+vert)%_sage_const_2  for j in dicv},{e0:dicl[N+_sage_const_1 +ed], e1:dicl[N+_sage_const_2 -ed]}))
      except KeyError:
        pass
    return result 

# returns (result,N), where N is the number of markings in Gstgraphs with (g,H) and result is a dictionary sending some tuples (g',(m_1, ..., m_l)), which correspond to boundary divisors, to the list of all entries of the form [Gr,mult,dicv,dicl] like in the definition of Hbdrystructures. Here dicv and dicl assume that the boundary divisor bdry is of the form stgraph([g',g-g'],[[m_1, ..., m_l,N+1],[complementary legs, N+2],[(N+1,N+2)]]
# Convention: we choose the key above such that g'<=g-g'. If there is equality, either there are no markings OR we ask that m_1=1. Note that m_1, ... are assumed to be ordered
# For the unique boundary divisor parametrizing irreducible curves (having a self-node), we reserve the key (g)

@cached_function
def preHbdrystructures(g, H):
  Hbdry=list_Hstrata(g,H,_sage_const_1 )
  if len(Hbdry)==_sage_const_0 :
    return ({},len(trivGgraph(g,H).gamma.list_markings()))
  N=len(Hbdry[0].gamma.list_markings())  
  result={}
  for Gr in Hbdry:
    AutGr=equiGraphIsom(Gr,Gr)
    
    edgs=deepcopy(Gr.gamma.edges)
    
    
    
    while edgs!=[]:
      econtr=edgs[0]  # this edge will remain after contraction
      
      # now go through AutGr and eliminate all other edges which are in orbit of econtr, record multiplicity
      multiplicity=_sage_const_0 
      for (dicv,dicl) in AutGr:
        try:
          edgs.remove((dicl[econtr[0]],dicl[econtr[1]]))
          multiplicity+=_sage_const_1 
        except:
          pass
      
      
      # now contract all except econtr and add the necessary data to the dictionary result
      contrGr=deepcopy(Gr.gamma)
      diccv={j:j for j in range(len(contrGr.genera))}
      for e in Gr.gamma.edges:
        if e!=econtr:
          (newgraph, v0, d1, d2,diccv_new)=contrGr.contract_edge(e,True)
          contrGr=newgraph
          diccv={j:diccv_new[diccv[j]] for j in diccv}
      
      # OLD: multiplicity*=len(GraphIsom(contrGr,contrGr))
      # NOTE: multiplicity must be multiplied by the number of automorphisms of the boundary stratum, 2 in this case
      # this compensates for the fact that these automorphisms give rise to different bdry-structures on Gr
      
      if len(contrGr.genera)==_sage_const_1 :
        # it remains a self-loop
        if g not in result:
          result[(g)]=[]
        result[(g)].append([Gr,QQ(multiplicity)/len(AutGr),{j:_sage_const_0  for j in range(len(Gr.gamma.genera))},{N+_sage_const_1 :econtr[0],N+_sage_const_2 :econtr[1]}])
        result[(g)].append([Gr,QQ(multiplicity)/len(AutGr),{j:_sage_const_0  for j in range(len(Gr.gamma.genera))},{N+_sage_const_2 :econtr[0],N+_sage_const_1 :econtr[1]}])
        
      else:
        # we obtain a separating boundary; now we must distinguish cases to ensure that g' <= g-g' and for equality m_1=1
        if contrGr.genera[0]>contrGr.genera[1] or (contrGr.genera[0] == contrGr.genera[1] and _sage_const_1  in contrGr.legs[1]):
          switched=_sage_const_1 
        else:
          switched=_sage_const_0 
        
        eswitched=(contrGr.vertex(econtr[0])+switched)%_sage_const_2   # eswitched=0 means econtr[0] is in the vertex with g',[m_1,..]; eswitched=1 means it is at the other vertex
        
        gprime=contrGr.genera[switched]
        markns=deepcopy(contrGr.legs[switched])
        markns.remove(econtr[eswitched])
        markns.sort()
        markns=tuple(markns)
        
        
        try:
          result[(gprime,markns)].append([Gr,QQ(multiplicity)/len(AutGr),{v:(diccv[v]+switched)%_sage_const_2  for v in diccv},{N+_sage_const_1 :econtr[eswitched], N+_sage_const_2 :econtr[_sage_const_1 -eswitched]}])
        except KeyError:
          result[(gprime,markns)]=[[Gr,QQ(multiplicity)/len(AutGr),{v:(diccv[v]+switched)%_sage_const_2  for v in diccv},{N+_sage_const_1 :econtr[eswitched], N+_sage_const_2 :econtr[_sage_const_1 -eswitched]}]]
        
        if contrGr.genera[0] == contrGr.genera[1] and N==_sage_const_0 :
          # in this case the resulting boundary divisor has an automorphism, so we need to record also the switched version of the above bdry-structure
          result[(gprime,markns)].append([Gr,QQ(multiplicity)/len(AutGr),{v:(diccv[v]+_sage_const_1 -switched)%_sage_const_2  for v in diccv},{N+_sage_const_2 :econtr[eswitched], N+_sage_const_1 :econtr[_sage_const_1 -eswitched]}])  
  
  return (result,N)
        

        
        
          
    
    

# summands in prodHclass
#  * gamma is a stgraph on which this summand lives
#  * spaces is a dictionary, assigning entries of the form [g,Hdata] of a genus and HurwitzData Hdata to integer labels a - since these change a lot and are replaced frequently by multiple new labels, this data structure hopefully allows for flexibility
#  * vertdata gives a list of entries of the form [a, dicl] for each vertex v of gamma, where a is a label (sent to (g,Hdata) by spaces) and dicl is an injective dictionary mapping leg-names of v to the corresponding (standard) numbers of the Hurwitz space of (g,Hdata)
#  * poly is a kppoly on gamma
#  * dicv0 is a surjective dictionary mapping vertices of gamma to vertices of the including prodHclass
#  * dicl0 is an injective dictionary mapping legs of gamma0 to legs of gamma
class decHstratum:
  def __init__(self,gamma,spaces,vertdata,dicv0=None,dicl0=None,poly=None):
    self.gamma=gamma
    self.spaces=spaces
    self.vertdata=vertdata
    if dicv0==None:
      self.dicv0={v:_sage_const_0  for v in range(len(gamma.genera))}
    else:
      self.dicv0=dicv0
    
    if dicl0==None:  
      self.dicl0={l:l for l in gamma.list_markings()}
    else:
      self.dicl0=dicl0
      
    if poly==None:  
      self.poly=onekppoly(len(gamma.genera))
    else:
      self.poly=poly
  
  def __repr__(self):
    return repr((self.gamma,self.spaces,self.vertdata,self.dicv0,self.dicl0,self.poly))
  
  def __neg__(self):
    return (-_sage_const_1 )*self  

  def __rmul__(self,other):
    #if isinstance(other,sage.rings.integer.Integer) or isinstance(other,sage.rings.rational.Rational) or isinstance(other,int):
      new=deepcopy(self)
      new.poly*=other
      return new   
  
  # self represents a morphism H_1 x ... x H_r -i-> M_1 x ... x M_r -pf-> M_1'x ... x M_g', where the first map i is the inclusion of Hurwitz stacks and the second map pf is a product of forgetful maps of some of the M_i. The spaces M_j' are those belonging to the vertices of self.gamma
  # prodforgetpullback takes a dictionary spacelist mapping space labels a_1, ..., a_r to the lists of vertices j using these spaces (i.e. the M_j'-component of pf depends on the M_a_i argument if j in spacelist[a_i])
  # it returns the pullback of self.poly under pf, which is a prodtautclass on a stgraph being the disjoint union of M_1, ..., M_r (in the order of spacelist.keys())
  # this function is meant as an auxilliary function for self.evaluate()
  def prodforgetpullback(self,spacelist):
   alist=list(spacelist)
   decs=decstratum(self.gamma,poly=self.poly)
   splitdecs=decs.split()
   
   # find number of markings of spaces M_i
   N={a: self.spaces[a][1].nummarks() for a in spacelist}
   forgetlegs=[list(set(range(_sage_const_1 ,N[self.vertdata[v][0]]+_sage_const_1 ))-set(self.vertdata[v][1].values())) for v in range(len(self.gamma.genera))]
   resultgraph=stgraph([self.spaces[a][0] for a in spacelist],[list(range(_sage_const_1 ,N[a]+_sage_const_1 )) for a in N],[])
   
   # rename splitted kppolys to match the standard names of markings on the M_i and wrap them in decstrata
   trivgraphs=[stgraph([self.gamma.genera[i]],[list(self.vertdata[i][1].values())],[]) for i in range(len(self.gamma.genera))]
   splitdecs=[[s[i].rename_legs(self.vertdata[i][1]) for i in range(len(s))] for s in splitdecs]
   splitdecs=[[decstratum(trivgraphs[i],poly=s[i]) for i in range(len(s))] for s in splitdecs]
   
   result=prodtautclass(resultgraph,[])
   for s in splitdecs:
     term=prodtautclass(resultgraph)
     for j in range(len(alist)):
       t=prod([s[i].forgetful_pullback(forgetlegs[i]) for i in spacelist[alist[j]]])
       t.dimension_filter()
       t=t.toprodtautclass(self.spaces[alist[j]][0],N[alist[j]])
       term=term.factor_pullback([j],t)
     result+=term
   return result    
       
  
  # evaluates self against the fundamental class of the ambient space (of self.gamma), returns a rational number
  def evaluate(self):
    spacelist={a:[] for a in self.spaces}
    for v in range(len(self.gamma.genera)):
      spacelist[self.vertdata[v][0]].append(v)
    for a in spacelist:
      if spacelist[a]==[]:
        spacelist.pop(a)
    alist=list(spacelist)
    
    pfp=self.prodforgetpullback(spacelist)
    Gr=[trivGgraph(*self.spaces[a]) for a in spacelist]
    prodGr=[prodHclass(gr.gamma,[gr.to_decHstratum()]) for gr in Gr]
    result=_sage_const_0 
    for t in pfp.terms:
      tempresult=_sage_const_1 
      for i in range(len(alist)):
        if t[i].gamma.edges==[]:  # decstratum t[i] is a pure kppoly
          tempresult*=(Hdecstratum(Gr[i],poly=t[i].poly)).quotient_pushforward().evaluate()
        else:
          tempresult*=(prodGr[i]*t[i]).evaluate()
      result+=tempresult
    return result  
  
  # replaces the fundamental class of the Hurwitz space with label a with the (fundamental class of the stratum corresponding to) Gstgraph Gr
  # in particular, self.gamma is changed by replacing all vertices with vertdata a with the graph Gr (more precisely: with the graph obtained by forgetting the corresponding markings in Gr and then stabilizing
  # if the vertex specialv in self and the edge speciale in Gr are given, also return the edge corresponding to the version of speciale that was glued to the vertex specialv (which by assumption has space labelled by a)
  # IMPORTANT: here we assume that speciale is not contracted in the forgetful-stabilization process!
  def replace_space_by_Gstgraph(self,a,Gr,specialv=None,speciale=None):      
    #global examinrep
    #examinrep=(deepcopy(self),a,deepcopy(Gr),specialv,speciale)
    
    avertices=[v for v in range(len(self.gamma.genera)) if self.vertdata[v][0]==a]
    avertices.reverse()
    
    
    gluein=Gr.to_decHstratum()
    
    
    maxspacelabel=max(self.spaces)
    self.spaces.pop(a)
    self.spaces.update({l+maxspacelabel+_sage_const_1 :gluein.spaces[l] for l in gluein.spaces})
    
    for v in avertices:
      # First we must create the graph to be glued in at v. For this we take the graph from gluein and forget unnecessary markings, stabilize and then rename the remaining markings as dictated by self.vertdata[v][1]. During all steps we must record which vertices/legs go where
      
      gluegraph=deepcopy(gluein.gamma)
      dicl_v=self.vertdata[v][1]
      
      usedlegs=dicl_v.values()
      unusedlegs=[l for l in gluegraph.list_markings() if l not in usedlegs]
      
      gluegraph.forget_markings(unusedlegs)
      
      
      (forgetdicv,forgetdicl,forgetdich)=gluegraph.stabilize()
      
      forgetdicl.update({l:l for l in gluegraph.leglist() if l not in forgetdicl})
      
      
      # now we must rename the legs in gluegraph so they fit with the leg-names in self.gamma, using the inverse of dicl_v
      dicl_v_inverse={dicl_v[l]:l for l in dicl_v}
      shift=max(list(dicl_v)+[0])+_sage_const_1 
      gluegraph.rename_legs(dicl_v_inverse,shift)
      
      
      divGr={}
      divs={}
      dil={}
      numvert_old=len(self.gamma.genera)
      num_newvert=len(gluegraph.genera)
      dic_voutgoing={l:l for l in self.gamma.legs[v]}
      self.gamma.glue_vertex(v,gluegraph,divGr,divs,dil)
      dil.update(dic_voutgoing)
      dil_inverse={dil[l]:l for l in dil}
      
      
      if specialv==v:
        speciale_im=(dil[forgetdich.get(speciale[0],speciale[0])+shift],dil[forgetdich.get(speciale[1],speciale[1])+shift])
      
      
      # now repair vertdata: note that new vertex list is obtained by deleting v and appending vertex list of gluegraph
      # also note that in the gluing-procedure ALL leg-labels at vertices different from v have NOT changed, so those vertdatas do not have to be adapted
      self.vertdata.pop(v)
      for w in range(num_newvert):
        # forgetdicv[w] is the vertex number that w corresponded to before stabilizing, inside gluein
        (pre_b,pre_diclb)=gluein.vertdata[forgetdicv[w]]
        
        
        b=pre_b+maxspacelabel+_sage_const_1 
        # pre_diclb is injective dictionary from legs of vertex forgetdicv[w] in gluein.gamma to the standard-leg-numbers in self.spaces[b]
        # thus we need to reverse the shift/rename and the glue_vertex-rename and compose with diclb
        diclb={l:pre_diclb[forgetdicl[dicl_v.get(dil_inverse[l],dil_inverse[l]-shift)]]  for l in self.gamma.legs[w+numvert_old-_sage_const_1 ]}
        
        self.vertdata.append([b,diclb])
      
      
      # now repair dicv0, the surjective map from vertices of self.gamma to the gamma0 of the containing prodHclass
      # vertex v went to some vertex w, now all vertices that have replaced v must go to w
      # unfortunately, all vertices v+1, v+2, ... have shifted down by 1, so this must be taken care of
      w=self.dicv0.pop(v)
      for vnumb in range(v,numvert_old-_sage_const_1 ):
        self.dicv0[vnumb]=self.dicv0[vnumb+_sage_const_1 ]
      for vnumb in range(numvert_old-_sage_const_1 ,numvert_old-_sage_const_1 +num_newvert):
        self.dicv0[vnumb]=w    
      
      # now repair dicl0, the injective map from leg-names of gamma0 to leg-names of self.gamma
      # ACTUALLY: since gluing does not change any of the old leg-names, dicl0 is already up to date!
      
      
      # now repair self.poly, term by term, collecting the results in newpoly, which replaces self.poly at the end
      newpoly=kppoly([],[])
      for (kappa,psi,coeff) in self.poly:  
        trunckappa=deepcopy(kappa)
        kappav=trunckappa.pop(v)
        trunckappa+=[[] for i in range(num_newvert)]
        trunckppoly=kppoly([(trunckappa,psi)],[coeff])
        trunckppoly*=prod([(sum([kappacl(numvert_old-_sage_const_1 +k,j+_sage_const_1 ,numvert_old+num_newvert-_sage_const_1 ) for k in range(num_newvert)]))**kappav[j] for j in range(len(kappav))])
        newpoly+=trunckppoly
        
      self.poly=newpoly
    
    spacesused={a:False for a in self.spaces}
    for (a,di) in self.vertdata:
      spacesused[a]=True
    unusedspaces=[a for a in spacesused if spacesused[a]==False]  
    
    degree=_sage_const_1 
    for a in unusedspaces:
      trivGraph=trivGgraph(*self.spaces.pop(a))
      if trivGraph.dim()==_sage_const_0 :
        degree*=trivGraph.delta_degree(_sage_const_0 )
      else:
        degree=_sage_const_0 
        break  
    
    self.poly*=degree    
    
    if specialv!=None:
      return speciale_im

# takes genus g, number n of markings and lists leglists, legdics of length r (and possibly a tautclass T on \bar M_{g,n})
# for i=0,..,r-1 the dictionary legdics[i] is an injection of the list leglists[i] in {1,..,n}
# computes the class DELTA of the small diagonal in (\bar M_{g,n})^r, intersects with T on the first factor and then pushes down under a forgetful map
# this map exactly forgets in the ith factor all markings not in the image of legdics[i]
# afterwards it renames the markings on the ith factor such that marking legdics[i][j] is called j
# it returns a prodtautclass on a graph that is the disjoint union of genus g vertices with leglists given by leglists (assumed to be disjoint)
def forgetful_diagonal(g,n,leglists,legdics,T=None):
  #global inpu 
  #inpu = (g,n,leglists,legdics,T)
  r=len(leglists)
  if T==None:
    T=tautclass([decstratum(stgraph([g],[list(range(_sage_const_1 ,n+_sage_const_1 ))],[]))])
  
  gamma=stgraph([g for i in range(r)],[list(range(_sage_const_1 ,n+_sage_const_1 )) for i in range(r)],[])
  result=prodtautclass(gamma,[[decstratum(stgraph([g],[list(range(_sage_const_1 ,n+_sage_const_1 ))],[])) for i in range(r)]])
  
  # We want to obtain small diagonal by intersecting Delta_12, Delta_13, ..., Delta_1r
  # since we will forget markings in the factors 2,..,r, only components of Delta_1i are relevant which have sufficient cohomological degree in the second factor (all others vanish in the pushforward having positive-dimensional fibres)
  forgetlegs=[[j for j in range(_sage_const_1 ,n+_sage_const_1 ) if j not in legdics[i].values()] for i in range(r)]
  fl=[len(forg) for forg in forgetlegs]
  rndics=[{legdics[i][leglists[i][j]] :j+_sage_const_1  for j in range(len(leglists[i]))} for i in range(r)]
  
  
  if r >_sage_const_1 :
    #TODO: check that everything is tautological more carefully, only checking those degrees that are really crucial
    for rdeg in range(_sage_const_0 ,_sage_const_2 *(_sage_const_3 *g-_sage_const_3 +n)+_sage_const_1 ):
      if not cohom_is_taut(g,n,rdeg):
        print("In computation of diagonal : H^%s(bar M_%s,%n) not necessarily tautological" % (rdeg,g,n))
      
    # now compute diagonal 
    Dgamma=stgraph([g,g],[list(range(_sage_const_1 ,n+_sage_const_1 )),list(range(_sage_const_1 ,n+_sage_const_1 ))],[])
    Delta=prodtautclass(Dgamma,[])
    for deg in range(_sage_const_0 ,(_sage_const_3 *g-_sage_const_3 +n)+_sage_const_1 ):
      gi1=generating_indices(g,n,deg)
      gi2=generating_indices(g,n,_sage_const_3 *g-_sage_const_3 +n-deg)
      strata1 = DR.all_strata(g,deg,tuple(range(_sage_const_1 ,n+_sage_const_1 )))
      gens1=[Graphtodecstratum(strata1[j]) for j in gi1]
      strata2 = DR.all_strata(g,_sage_const_3 *g-_sage_const_3 +n-deg,tuple(range(_sage_const_1 ,n+_sage_const_1 )))
      gens2=[Graphtodecstratum(strata2[j]) for j in gi2]    
    
      # compute inverse of intersection matrix
      invintmat=inverseintmat(g,n,tuple(gi1),tuple(gi2),deg)
      for a in range(len(gi1)):
        for b in range(len(gi2)):
          if invintmat[a,b] != _sage_const_0 :
            Delta.terms.append([invintmat[a,b]*gens1[a],gens2[b]])
    
    for i in range(_sage_const_1 ,r):
      result=result.factor_pullback([_sage_const_0 ,i],Delta)
  result=result.factor_pullback([0],T.toprodtautclass(g,n))
  
  # now we take care of forgetful pushforwards and renaming
  for t in result.terms:
    for i in range(r):
      t[i]=t[i].forgetful_pushforward(forgetlegs[i])
      t[i].rename_legs(rndics[i])  #note: there can be no half-edge names in the range 1,..,n so simply renaming legs is possible
  
  result.gamma=stgraph([g for i in range(r)],deepcopy(leglists),[])
  
  return result.consolidate() 
      

@cached_function
def inverseintmat(g,n,gi1,gi2,deg):
  if deg <= QQ(_sage_const_3 *g-_sage_const_3 +n)/_sage_const_2 :
    intmat=matrix(DR.pairing_submatrix(gi1,gi2,g,deg,tuple(range(_sage_const_1 ,n+_sage_const_1 ))))
  else:
    intmat=matrix(DR.pairing_submatrix(gi2,gi1,g,_sage_const_3 *g-_sage_const_3 +n-deg,tuple(range(_sage_const_1 ,n+_sage_const_1 )))).transpose()  
  return intmat.transpose().inverse()      
  
def inverseintmat2(g,n,gi1,gi2,deg):
  tg1=tautgens(g,n,deg)
  tg2=tautgens(g,n,_sage_const_3 *g-_sage_const_3 +n-deg)
  intmat=matrix([[(tg1[i]*tg2[j]).evaluate() for i in gi1] for j in gi2]) 
  return intmat.transpose().inverse()     

"""  # remove all terms that must vanish for dimension reasons 
  def dimension_filter(self):
    for i in range(len(self.poly.monom)):
      (kappa,psi)=self.poly.monom[i]
      for v in range(len(self.gamma.genera)):
        # local check: we are not exceeding dimension at any of the vertices
        if sum([(k+1)*kappa[v][k] for k in range(len(kappa[v]))])+sum([psi[l] for l in self.gamma.legs[v] if l in psi])>3*self.gamma.genera[v]-3+len(self.gamma.legs[v]):
          self.poly.coeff[i]=0
          break
        # global check: the total codimension of the term of the decstratum is not higher than the total dimension of the ambient space
        #if self.poly.deg(i)+len(self.gamma.edges)>3*self.gamma.g()-3+len(self.gamma.list_markings()):
         # self.poly.coeff[i]=0
          #break          
    return self.consolidate()      
  
  def consolidate(self):
    self.poly.consolidate()
    return self """

"""  # computes integral against the fundamental class of the corresponding moduli space
  # will not complain if terms are mixed degree or if some of them do not have the right codimension  
  def evaluate(self):  
    answer=0
    for (kappa,psi,coeff) in self.poly:
      temp=1
      for v in range(len(self.gamma.genera)):
        psilist=[psi.get(l,0) for l in self.gamma.legs[v]]
        kappalist=[]
        for j in range(len(kappa[v])):
          kappalist+=[j+1 for k in range(kappa[v][j])]
        if sum(psilist+kappalist) != 3*self.gamma.genera[v]-3+len(psilist):
          temp = 0
          break
        temp*=DR.socle_formula(self.gamma.genera[v],psilist,kappalist)
      answer+=coeff*temp  
    return answer  """
"""  def rename_legs(self,dic):
    self.gamma.rename_legs(dic)
    self.poly.rename_legs(dic)
    return self  
  def __repr__(self):
    return 'Graph :      ' + repr(self.gamma) +'\n'+ 'Polynomial : ' + repr(self.poly) """
  
  
# old code snippet for boundary pullback of decHstrata
"""            
            if len(erg.genera)==1:
              # loop graph, add all missing markings to it
              egr.legs[0]+=forgetmarks
              divlist=[egr]
            if len(erg.genera)==2:
              possi=[[0,1] for j in forgetmarks]
              divlist=[]
              for distri in itertools.product(*possi):
                # distri = (0,0,1,0,1,1) means that forgetmarks number 0,1,3 go to erg.legs[0] and 2,4,5 go to erg.legs[1]
                ergcpy=deepcopy(erg)
                ergcpy.legs[0]+=[forgetmarks[j] for j in range(len(forgetmarks)) if distri[j]==0]
                ergcpy.legs[1]+=[forgetmarks[j] for j in range(len(forgetmarks)) if distri[j]==1]
                divlist.append(ergcpy)
"""            

# Knowing that there exists a morphism Gamma -> A, we want to reconstruct the corresponding dicv (from vertices of Gamma to vertices of A) from the known dicl                      
#TODO: we could give dicv as additional argument if we already know part of the final dicv
def dicv_reconstruct(Gamma,A,dicl):
  if len(A.genera)==_sage_const_1 :
    return {ver:_sage_const_0  for ver in range(len(Gamma.genera))}
  else:  
    dicv={Gamma.vertex(dicl[h]) : A.vertex(h) for h in dicl}
    remaining_vertices=set(range(len(Gamma.genera)))-set(dicv)
    remaining_edges=set([e for e in Gamma.edges if e[0] not in dicl.values()])
    current_vertices=set(dicv)

    while remaining_vertices!=set():
      newcurrent_vertices=set()
      for e in deepcopy(remaining_edges):
        if Gamma.vertex(e[0]) in current_vertices:
          vnew=Gamma.vertex(e[1])
          remaining_edges.remove(e)
          # if vnew is in current vertices, we don't have to do anything (already know it)
          # otherwise it must be a new vertex (cannot reach old vertex past the front of current vertices)
          if vnew not in current_vertices:  
            dicv[vnew]=dicv[Gamma.vertex(e[0])]
            remaining_vertices.discard(vnew)
            newcurrent_vertices.add(vnew)
          continue
        if Gamma.vertex(e[1]) in current_vertices:
          vnew=Gamma.vertex(e[0])
          remaining_edges.remove(e)
          # if vnew is in current vertices, we don't have to do anything (already know it)
          # otherwise it must be a new vertex (cannot reach old vertex past the front of current vertices)
          if vnew not in current_vertices:  
            dicv[vnew]=dicv[Gamma.vertex(e[1])]
            remaining_vertices.discard(vnew)
            newcurrent_vertices.add(vnew)  
      current_vertices=newcurrent_vertices
    return dicv

# approximation to the question if H^{r}(\overline M_{g,n},QQ) is generated by tautological classes
# if True is returned, the answer is yes, if False is returned, the answer is no; if None is returned, we make no claim
# we give a reference for each of the claims, though we do not claim that this is the historically first such reference
def cohom_is_taut(g,n,r):    
  if g==_sage_const_0 :
    return True  # [Keel - Intersection theory of moduli space of stable N-pointed curves of genus zero]
  if g==_sage_const_1  and (r%_sage_const_2 ) == _sage_const_0 :
    return True  # [Petersen - The structure of the tautological ring in genus one]
  if g==_sage_const_1  and n<_sage_const_10 :
    return True  # [Graber, Pandharipande - Constructions of nontautological classes on moduli spaces of curves] TODO: also for n=10 probably, typo in GP ?
  if g==_sage_const_1  and n>=_sage_const_11  and r==_sage_const_11 :
    return False # [Graber, Pandharipande]
  if g==_sage_const_2  and (r%_sage_const_2 )==_sage_const_0  and n<_sage_const_20 :
    return True  # [Petersen - Tautological rings of spaces of pointed genus two curves of compact type]
  if g==_sage_const_2  and n<=_sage_const_3 :
    return True  # [Getzler - Topological recursion relations in genus 2 (above Prop. 16+e_11=-1,e_2=0)] + [Yang - Calculating intersection numbers on moduli spaces of curves]  
  if g==_sage_const_2  and n==_sage_const_4 :
    return True  # [Bini,Gaiffi,Polito - A formula for the Euler characteristic of \bar M_{2,4}] + [Yang] + [Petersen - Tautological ...] : all even cohomology is tautological and dimensions from Yang sum up to Euler characteristic
    # WARNING: [BGP] contains error, later found in [Bini,Harer - Euler characteristics of moduli spaces of curves], does not affect the numbers above
  if g==_sage_const_3  and n==_sage_const_0 :
    return True  # [Getzler - Topological recursion relations in genus 2 (Proof of Prop. 16)] + [Yang]
  if g==_sage_const_3  and n==_sage_const_1 :
    return True  # [Getzler,Looijenga - The hodge polynomial of \bar M_3,1] + [Yang]
  if g==_sage_const_3  and n==_sage_const_2 :
    return True  # [Bergström - Cohomology of moduli spaces of curves of genus three via point counts]
  if g==_sage_const_4  and n==_sage_const_0 :
    return True  # [Bergström, Tommasi - The rational cohomology of \bar M_4] + [Yang]
  
  #TODO: Getzler computes Serre characteristic in genus 1 ('96)
  #TODO: [Bini,Harer - Euler characteristics of moduli spaces of curves] : recursive computation of chi(\bar M_{g,n})
  # This suggests that g=3,n=2 should also work (Yang's numbers add up to Euler char.)
  
  
  if r==_sage_const_0  or r==_sage_const_2 :
    return True  # r=0: fundamental class is tautological, r=1: [Arbarello, Cornalba - The Picard groups of the moduli spaces of curves]  
  if r==_sage_const_1  or r==_sage_const_3  or r==_sage_const_5 :
    return True  # [Arbarello, Cornalba - Calculating cohomology groups of moduli spaces of curves via algebraic geometry]
  if _sage_const_2 *(_sage_const_3 *g-_sage_const_3 +n)- r in [_sage_const_0 ,_sage_const_1 ,_sage_const_2 ,_sage_const_3 ,_sage_const_5 ]:
    return True  
    # dim=(3*g-3+n), then by Hard Lefschetz, there is isomorphism H^(dim-k) -> H^(dim+k) by multiplication with ample divisor
    # this divisor is tautological, so if all of H^(dim-k) is tautological, also H^(dim+k) is tautological
  
  return None  

# approximation to the question if the Faber-Zagier relations generate all tautological relations in A^d(\bar M_{g,n})
# if True is returned, the answer is yes, if False is returned, it means that no proof has been registered yet
# we give a reference for each of the claims, though we do not claim that this is the historically first such reference
def FZ_conjecture_holds(g,n,d):    
  if g==_sage_const_0 :
    return True  # [Keel - Intersection theory of moduli space of stable N-pointed curves of genus zero]
  if g==_sage_const_1 :
    return True  # [Petersen - The structure of the tautological ring in genus one] %TODO: verify FZ => Getzler's rel. + WDVV

############
#
# Lookup and saving functions for Hdatabase
#
############

# To ensure future compatibility: only append functions to this list! Do not change order of existing functions.
PICKLED_FUNCTIONS = [generating_indices, genstobasis]


def save_FZrels():
    """
    Saving previously computed Faber-Zagier relations to file new_geninddb.pkl.
    TESTS::
        sage: from admcycles import *
        sage: generating_indices(0,3,0)
        [0]
        sage: admcycles.genstobasis(0,3,0)
        [(1)]
        sage: cache1=deepcopy(dict(generating_indices.cache))
        sage: cache2=deepcopy(dict(admcycles.genstobasis.cache))
        sage: save_FZrels()
        sage: generating_indices.clear_cache()
        sage: admcycles.genstobasis.clear_cache()
        sage: load_FZrels()
        sage: cache1==dict(generating_indices.cache)
        True
        sage: cache2==dict(admcycles.genstobasis.cache)
        True
    """
    with open('new_geninddb.pkl', 'wb') as file:
        dumped = {fun[0]: dict(fun[1].cache)
                   for fun in enumerate(PICKLED_FUNCTIONS)}
        pickle.dump(dumped, file)


def load_FZrels():
    """
    Loading values
    """
    try:
        with open('new_geninddb.pkl', 'rb') as file:
            dumped = pickle.load(file)
            for k, cache in dumped.items():
                PICKLED_FUNCTIONS[k].cache.update(cache)
    except IOError:
          raise IOError('Could not find file new_geninddb.pkl\nIf you previously saved FZ relations in geninddb.pkl, try old_load_FZrels() followed by save_FZrels() to go to new format.\nType old_load_FZrels? for more info.')          

def old_load_FZrels():
    """
    Loading values from old format in 'geninddb.pkl'.
    If you previously saved FZ relations to this file, you should first call old_load_FZrels(), followed by save_FZrels() to save them to the new location 'new_geninddb.pkl'. From now on, you can load the relations from this new file using load_FZrels().
    Once you are certain that the transfer worked, you can delete the file 'geninddb.pkl'.
    """    
    pkl_file=open('geninddb.pkl','rb')
    dumpdic=pickle.load(pkl_file) 
    # Dictionary of the form
    # {('generating_indices', (0, 3, 0)): [0],
    # ('genstobasis', (2, 1, 0)): [(1)], ... }
    for k, cache in dumpdic.items():
        if k[0]=='generating_indices':
            generating_indices.set_cache(cache, *(k[1]))
        if k[0]=='genstobasis':
            genstobasis.set_cache(cache, *(k[1]))
    pkl_file.close()
    

# looks up if the Hurwitz cycle for (g,dat) has already been computed. If yes, returns a fresh tautclass representing this
# it takes care of the necessary reordering and possible pushforwards by forgetting markings
# if this cycle has not been computed before, it raises a KeyError
def Hdb_lookup(g,dat,markings):
  # first get a sorted version of dat, remembering the reordering
  li=dat.l
  sort_li=sorted(enumerate(li),key=lambda x:x[1])
  ind_reord=[i[0] for i in sort_li]  # [2,0,1] means that li looking like [a,b,c] now is reordered as li_reord=[c,a,b]
  li_reord=[i[1] for i in sort_li]
  dat_reord=HurwitzData(dat.G,li_reord)
  
  # now create a dictionary legpermute sending the marking-names in the space you want to the corresponding names in the standard-ordered space
  mn_list=[]
  num_marks=_sage_const_0 
  Gord=dat.G.order()
  for count in range(len(li)):
    new_marks=QQ(Gord)/li[count][1]
    mn_list.append(list(range(num_marks+_sage_const_1 ,num_marks+new_marks+_sage_const_1 )))
  
  mn_reord=[]  
  for i in ind_reord:
    mn_reord.append(mn_list[i])
  
  legpermute={mn_reord[j]:j+_sage_const_1  for j in range(len(mn_reord))}  
  #markings_reord=
  
  Hdb=Hdatabase[(g,dat_reord)]
  for marks in Hdb:
    if set(markings).issubset(set(marks)):
      forgottenmarks=set(marks)-set(markings)
      result=deepcopy(Hdb[marks])
      result=result.forgetful_pushforward(list(forgottenmarks))
      found=True
      #TODO: potentially include this result in Hdb
  



############
#
# Library of interesting cycle classes
#
############

def fundclass(g,n):
  r"""
  Return the fundamental class of \Mbar_g,n.
  """
  if not all(isinstance(i, (int, Integer)) and i >= 0 for i in (g,n)):
    raise ValueError("g,n must be non-negative integers")  
  if 2*g-2+n <= 0:
    raise ValueError("g,n must satisfy 2g-2+n>0")
  return trivgraph(g,n).to_tautclass()

# returns a list of generators of R^r(\bar M_{g,n}) as tautclasses in the order of Pixton's program
# if decst=True, returns generators as decstrata, else as tautclasses
def tautgens(g,n,r,decst=False):
  r"""
  Returns a lists of all tautological classes of degree r on \bar M_{g,n}.
  
  INPUT:
  
  g : integer
    Genus g of curves in \bar M_{g,n}.
  n : integer
    Number of markings n of curves in \bar M_{g,n}.
  r : integer
    The degree r of of the classes.
  decst : boolean
    If set to True returns generators as decorated strata, else as tautological classes.
    
  EXAMPLES::
  
    sage: from admcycles import *

    sage: tautgens(2,0,2)[1]
    Graph :      [2] [[]] []
    Polynomial : 1*(kappa_1^2 )_0
    
  ::
  
    sage: L=tautgens(2,0,2);2*L[3]+L[4]
    Graph :      [1, 1] [[2], [3]] [(2, 3)]
    Polynomial : 2*psi_2^1
    <BLANKLINE>
    Graph :      [1] [[2, 3]] [(2, 3)]
    Polynomial : 1*(kappa_1^1 )_0
  """
  L = DR.all_strata(g,r,tuple(range(_sage_const_1 ,n+_sage_const_1 )))
  if decst:
    return [Graphtodecstratum(l) for l in L]
  else:
    return [tautclass([Graphtodecstratum(l)]) for l in L]

# prints a list of generators of R^r(\bar M_{g,n}) as tautclasses in the order of Pixton's program
def list_tautgens(g,n,r):
  r"""
  Lists all tautological classes of degree r on \bar M_{g,n}.
  
  INPUT:
  
  g : integer
    Genus g of curves in \bar M_{g,n}.
  n : integer
    Number of markings n of curves in \bar M_{g,n}.
  r : integer
    The degree r of of the classes.
    
  EXAMPLES::
  
    sage: from admcycles import *

    sage: list_tautgens(2,0,2)
    [0] : Graph :      [2] [[]] []
    Polynomial : 1*(kappa_2^1 )_0 
    [1] : Graph :      [2] [[]] []
    Polynomial : 1*(kappa_1^2 )_0 
    [2] : Graph :      [1, 1] [[2], [3]] [(2, 3)]
    Polynomial : 1*(kappa_1^1 )_0 
    [3] : Graph :      [1, 1] [[2], [3]] [(2, 3)]
    Polynomial : 1*psi_2^1 
    [4] : Graph :      [1] [[2, 3]] [(2, 3)]
    Polynomial : 1*(kappa_1^1 )_0 
    [5] : Graph :      [1] [[2, 3]] [(2, 3)]
    Polynomial : 1*psi_2^1 
    [6] : Graph :      [0, 1] [[3, 4, 5], [6]] [(3, 4), (5, 6)]
    Polynomial : 1*
    [7] : Graph :      [0] [[3, 4, 5, 6]] [(3, 4), (5, 6)]
    Polynomial : 1*
  """
  L=tautgens(g,n,r)
  for i in range(len(L)):
    print('['+repr(i)+'] : '+repr(L[i]))

# returns kappa_d on \bar M_{gloc,nloc}
def kappaclass(a,g=None,n=None):
  r"""
  Returns the (Arbarello-Cornalba) kappa-class kappa_a on \bar M_{g,n} defined by 
  
    kappa_a= pi_*(psi_{n+1}^{a+1})
  
  where pi is the morphism \bar M_{g,n+1} --> \bar M_{g,n}.
  
  INPUT:
  
  a : integer
    The degree a of the kappa class.
  g : integer
    Genus g of curves in \bar M_{g,n}.
  n : integer
    Number of markings n of curves in \bar M_{g,n}.  
      
  EXAMPLES::
  
    sage: from admcycles import *

    sage: kappaclass(2,3,1)
    Graph :      [3] [[1]] []
    Polynomial : 1*(kappa_2^1 )_0 
    
  When working with fixed g and n for the moduli space \bar M_{g,n} it is possible specify the desired value of the global variables g and n to avoid giving them as an argument each time::
  
    sage: g=1;n=2;kappaclass(1) #doctest: +SKIP
    Graph :      [1] [[1, 2]] []
    Polynomial : 1*(kappa_1^1 )_0 
  """
  if g==None:
    g=globals()['g']
  if n==None:
    n=globals()['n']
  return tautclass([decstratum(trivgraph(g,n), poly=kappacl(_sage_const_0 ,a,_sage_const_1 ,g,n))])

# returns psi_i on \bar M_{gloc,nloc}
def psiclass(i,g=None,n=None):
  r"""
  Returns the class psi_i on \bar M_{g,n}.
  
  INPUT:
  
  i : integer
    The leg i associated to the psi class.
  g : integer
    Genus g of curves in \bar M_{g,n}.
  n : integer
    Number of markings n of curves in \bar M_{g,n}.  
      
  EXAMPLES::
  
    sage: from admcycles import *

    sage: psiclass(2,2,3)
    Graph :      [2] [[1, 2, 3]] []
    Polynomial : 1*psi_2^1
    
  When working with fixed g and n for the moduli space \bar M_{g,n} it is possible specify the desired value of the global variables g and n to avoid giving them as an argument each time::
  
    sage: g=3;n=2;psiclass(1) #doctest: +SKIP
    Graph :      [3] [[1, 2]] []
    Polynomial : 1*psi_1^1
  """
  if g==None:
    g=globals()['g']
  if n==None:
    n=globals()['n']
  return tautclass([decstratum(trivgraph(g,n), poly=psicl(i,_sage_const_1 ))])  


# returns the pushforward of the fundamental class under the boundary gluing map to \bar M_{gloc,nloc} associated to the partition (g1,A|g-g1, {1,...,n} \ A) of (g,n)
def sepbdiv(g1,A,g=None,n=None):
  r"""
  Returns the pushforward of the fundamental class under the boundary gluing map \bar M_{g1,A} X \bar M_{g-g1,{1,...,n} \ A}  -->  \bar M_{g,n}.
  
  INPUT:
  
  g1 : integer
    The genus g1 of the first vertex.
  A: list
    The list A of markings on the first vertex.
  g : integer
    The total genus g of the graph.
  n : integer
    The total number of markings n of the graph.  
      
  EXAMPLES::
  
    sage: from admcycles import *

    sage: sepbdiv(1,(1,3,4),2,5)
    Graph :      [1, 1] [[1, 3, 4, 6], [2, 5, 7]] [(6, 7)]
    Polynomial : 1*
    
  When working with fixed g and n for the moduli space \bar M_{g,n} it is possible specify the desired value of the global variables g and n to avoid giving them as an argument each time::
  
    sage: g=3;n=3;sepbdiv(1,(2,)) #doctest: +SKIP
    Graph :      [1, 2] [[2, 4], [1, 3, 5]] [(4, 5)]
    Polynomial : 1*
  """
  if g==None:
    g=globals()['g']
  if n==None:
    n=globals()['n']
  return tautclass([decstratum(stgraph([g1,g-g1],[list(A)+[n+_sage_const_1 ], list(set(range(_sage_const_1 ,n+_sage_const_1 )) - set(A))+[n+_sage_const_2 ]],[(n+_sage_const_1 ,n+_sage_const_2 )]))])    

# returns the pushforward of the fundamental class under the irreducible boundary gluing map \bar M_{g-1,n+2} -> \bar M_{g,n}
def irrbdiv(g=None, n=None):
  r"""
  Returns the pushforward of the fundamental class under the irreducible boundary gluing map \bar M_{g-1,n+2} -> \bar M_{g,n}.
  
  INPUT:
  
  g : integer
    The total genus g of the graph.
  n : integer
    The total number of markings n of the graph.  
      
  EXAMPLES::
  
    sage: from admcycles import *

    sage: irrbdiv(2,5)
    Graph :      [1] [[1, 2, 3, 4, 5, 6, 7]] [(6, 7)]
    Polynomial : 1*
    
  When working with fixed g and n for the moduli space \bar M_{g,n} it is possible specify the desired value of the global variables g and n to avoid giving them as an argument each time::
  
    sage: g=3; n=0; irrbdiv() #doctest: +SKIP
    Graph :      [2] [[1, 2]] [(1, 2)]
    Polynomial : 1*
  """
  if g==None:
    g=globals()['g']
  if n==None:
    n=globals()['n']
  return tautclass([decstratum(stgraph([g-_sage_const_1 ], [list(range(_sage_const_1 ,n+_sage_const_3 ))], [(n+_sage_const_1 ,n+_sage_const_2 )]))])  






  

# tries to return the class lambda_d on \bar M_{g,n}. We hope that this is a variant of the DR-cycle
# def lambdaish(d,g,n):
#   dvector=vector([_sage_const_0  for i in range(n)])
#   return (-_sage_const_2 )**(-g) * DR_cycle(g,dvector,d)

# Returns the chern character ch_d(EE) of the Hodge bundle EE on \bar M_{g,n} as a mixed degree tautological class (up to maxim. degree dmax)
# implements the formula from [Mumford - Towards an enumerative geometry ...]

@cached_function
def hodge_chern_char(g, n, d):
  bdries=list_strata(g,n,_sage_const_1 )
  irrbdry=bdries.pop(_sage_const_0 )
  autos = [bd.automorphism_number() for bd in bdries]
  result  = tautgens(g,n,_sage_const_0 )[0] #=1
  
  if d==_sage_const_0 :
    return deepcopy(tautgens(g,n,_sage_const_0 )[0])
  elif (d%_sage_const_2  == _sage_const_0 ) or (d<_sage_const_0 ):
    return tautclass([])
  else:  
    psipsisum_onevert=sum([((-_sage_const_1 )**i)*(psicl(n+_sage_const_1 ,_sage_const_1 )**i)*(psicl(n+_sage_const_2 ,_sage_const_1 )**(d-_sage_const_1 -i)) for i in range(d)])
    psipsisum_twovert=sum([((-_sage_const_1 )**i)*(psicl(n+_sage_const_1 ,_sage_const_2 )**i)*(psicl(n+_sage_const_2 ,_sage_const_2 )**(d-_sage_const_1 -i)) for i in range(d)])
    
    contrib=kappaclass(d,g,n)-sum([psiclass(i,g,n)**d for i in range(_sage_const_1 ,n+_sage_const_1 )])
    

    # old: contrib=kappaclass(d,g,n)-sum([psiclass(i,g,n) for i in range(1,n+1)])
    contrib+=(QQ(_sage_const_1 )/_sage_const_2 )*tautclass([decstratum(irrbdry,poly=psipsisum_onevert)])
    contrib+=sum([(QQ(_sage_const_1 )/autos[ind])*tautclass([decstratum(bdries[ind], poly=psipsisum_twovert)])for ind in range(len(bdries))])    

    contrib.dimension_filter()
    
    return (bernoulli(d+_sage_const_1 )/factorial(d+_sage_const_1 ) ) * contrib

# converts the function chclass (sending m to ch_m) to the corresponding chern polynomial, up to degree dmax
def chern_char_to_poly(chclass,dmax,g,n):
  result=deepcopy(tautgens(g,n,_sage_const_0 )[0])
  
  argum=sum([factorial(m-_sage_const_1 )*chclass(m) for m in range(_sage_const_1 ,dmax+_sage_const_1 )])
  expo=deepcopy(argum)
  result=result+argum
  
  for m in range(_sage_const_2 , dmax+_sage_const_1 ):
    expo*=argum
    expo.degree_cap(dmax)
    result+=(QQ(_sage_const_1 )/factorial(m))*expo
  
  return result

# returns lambda-class lambda_d on \bar M_{g,n}
#  r"""Returns lambda-class lambda_d on \\bar M_{g,n}"""
def lambdaclass(d,g=None,n=None):  
  r"""
  Returns the tautological class lambda_d on \bar M_{g,n} defined as the d-th Chern class
  
    lambda_d = c_d(E)
    
  of the Hodge bundle E. The result is represented as a sum of stable graphs with kappa and psi classes.
  
  INPUT:
  
  d : integer
    The degree d.
  g : integer
    Genus g of curves in \bar M_{g,n}.
  n : integer
    Number of markings n of curves in \bar M_{g,n}.  
      
  EXAMPLES::
  
    sage: from admcycles import *

    sage: lambdaclass(1,2,1)
    Graph :      [2] [[1]] []
    Polynomial : 1/12*(kappa_1^1 )_0 
    <BLANKLINE>
    Graph :      [2] [[1]] []
    Polynomial : (-1/12)*psi_1^1 
    <BLANKLINE>
    Graph :      [1, 1] [[3], [1, 4]] [(3, 4)]
    Polynomial : 1/12*
    <BLANKLINE>
    Graph :      [1] [[3, 4, 1]] [(3, 4)]
    Polynomial : 1/24*
    
  When working with fixed g and n for the moduli space \bar M_{g,n} it is possible specify the desired value of the global variables g and n to avoid giving them as an argument each time::
  
    sage: g=1;n=1;lambdaclass(1) #doctest: +SKIP
    Graph :      [1] [[1]] []
    Polynomial : 1/12*(kappa_1^1 )_0 
    
    Graph :      [1] [[1]] []
    Polynomial : (-1/12)*psi_1^1 
    
    Graph :      [0] [[3, 4, 1]] [(3, 4)]
    Polynomial : 1/24*
  """ 
  if g==None:
    g=globals()['g']
  if n==None:
    n=globals()['n']

  if d>g:
    return tautclass([])
    
  def chcl(m):
    return hodge_chern_char(g,n,m)
  
  cherpoly=chern_char_to_poly(chcl,d,g,n)
  
  result=cherpoly.degree_part(d)
  result.simplify(g,n,d)
  return result

def barH(g,dat,markings=None):
  """Returns \\bar H on genus g with Hurwitz datum dat as a prodHclass on the trivial graph, remembering only the marked points given in markings"""
  Hbar = trivGgraph(g,dat)
  n = len(Hbar.gamma.list_markings())  
  
  #global Hexam
  #Hexam=(g,dat,method,vecout,redundancy,markings)
  
  if markings==None:
    markings=list(range(_sage_const_1 ,n+_sage_const_1 ))

  N=len(markings)
  msorted=sorted(markings)
  markingdictionary={i+_sage_const_1 :msorted[i] for i in range(N)}  
  return prodHclass(stgraph([g],[list(range(_sage_const_1 ,N+_sage_const_1 ))],[]),[decHstratum(stgraph([g],[list(range(_sage_const_1 ,N+_sage_const_1 ))],[]), {_sage_const_0 :(g,dat)}, [[_sage_const_0 ,markingdictionary]])])


def Hyperell(g,n=_sage_const_0 ,m=_sage_const_0 ):
  """Returns the cycle class of the hyperelliptic locus of genus g curves with n marked fixed points and m pairs of conjugate points in \\barM_{g,n+2m}.
  
  TESTS::
    sage: from admcycles import *  
    sage: H=Hyperell(3) # long time
    sage: H.toTautbasis() # long time
    (3/4, -9/4, -1/8)
  """
  if n>_sage_const_2 *g+_sage_const_2 :
    print('A hyperelliptic curve of genus '+repr(g)+' can only have '+repr(_sage_const_2 *g+_sage_const_2 )+' fixed points!')
    return _sage_const_0 
  if _sage_const_2 *g-_sage_const_2 +n+_sage_const_2 *m<=_sage_const_0 :
    print('The moduli space \\barM_{'+repr(g)+','+repr(n+_sage_const_2 *m)+'} does not exist!')
    return _sage_const_0 
  
  G=PermutationGroup([(_sage_const_1 ,_sage_const_2 )])
  H=HurData(G,[G[1] for i in range(_sage_const_2 *g+_sage_const_2 )]+[G[0] for i in range(m)])
  marks=list(range(_sage_const_1 ,n+_sage_const_1 ))+list(range(_sage_const_2 *g+_sage_const_2 +_sage_const_1 ,_sage_const_2 *g+_sage_const_2 +_sage_const_1 +_sage_const_2 *m))
  factor=QQ(_sage_const_1 )/factorial(_sage_const_2 *g+_sage_const_2 -n)
  result= factor*Hidentify(g,H,markings=marks)
  
  # currently, the markings on result are named 1,2,..,n, 2*g+3, ..., 2*g+2+2*m
  # shift the last set of markings down by 2*g+3-(n+1)
  rndict={i:i for i in range(_sage_const_1 ,n+_sage_const_1 )}
  rndict.update({j:j-(_sage_const_2 *g+_sage_const_2 -n) for j in range(_sage_const_2 *g+_sage_const_2 +_sage_const_1 ,_sage_const_2 *g+_sage_const_2 +_sage_const_1 +_sage_const_2 *m)})
  result.rename_legs(rndict,True)
  
  return result

def Biell(g,n=_sage_const_0 ,m=_sage_const_0 ):
  r"""
  Returns the cycle class of the bielliptic locus of genus ``g`` curves with ``n`` marked fixed points and ``m`` pairs of conjugate points in `\bar M_{g,n+2m}`.
  
  TESTS::
      sage: from admcycles import *  
      sage: B=Biell(2) # long time
      sage: B.toTautbasis() # long time
      (15/2, -9/4)
  """
  if g==_sage_const_0 :
    print('There are no bielliptic curves of genus 0!')
    return _sage_const_0     
  if n>_sage_const_2 *g-_sage_const_2 :
    print('A bielliptic curve of genus '+repr(g)+' can only have '+repr(_sage_const_2 *g-_sage_const_2 )+' fixed points!')
    return _sage_const_0 
  if _sage_const_2 *g-_sage_const_2 +n+_sage_const_2 *m<=_sage_const_0 :
    print('The moduli space \\barM_{'+repr(g)+','+repr(n+_sage_const_2 *m)+'} does not exist!')
    return _sage_const_0 
  
  G=PermutationGroup([(_sage_const_1 ,_sage_const_2 )])
  H=HurData(G,[G[1] for i in range(_sage_const_2 *g-_sage_const_2 )]+[G[0] for i in range(m)])
  marks=list(range(_sage_const_1 ,n+_sage_const_1 ))+list(range(_sage_const_2 *g-_sage_const_2 +_sage_const_1 ,_sage_const_2 *g-_sage_const_2 +_sage_const_1 +_sage_const_2 *m))
  factor=_sage_const_1 /factorial(_sage_const_2 *g-_sage_const_2 -n)
  if g==_sage_const_2  and n==_sage_const_0  and m==_sage_const_0 :
    factor/=_sage_const_2 
  result= factor*Hidentify(g,H,markings=marks)
  
  # currently, the markings on result are named 1,2,..,n, 2*g-1, ..., 2*g-2+2*m
  # shift the last set of markings down by 2*g-1-(n+1)
  rndict={i:i for i in range(_sage_const_1 ,n+_sage_const_1 )}
  rndict.update({j:j-(_sage_const_2 *g-_sage_const_2 -n) for j in range(_sage_const_2 *g-_sage_const_2 +_sage_const_1 ,_sage_const_2 *g-_sage_const_2 +_sage_const_1 +_sage_const_2 *m)})
  result.rename_legs(rndict,True)
  
  return result
############
#
# Transfer maps
#
############

def Hpullpush(g,dat,alpha):
  """Pulls the class alpha to the space \\bar H_{g,dat} via map i forgetting the action, then pushes forward under delta."""
  Hb = Htautclass([Hdecstratum(trivGgraph(g,dat),poly=onekppoly(_sage_const_1 ))])
  Hb = Hb * alpha
  return Hb.quotient_pushforward()

def FZreconstruct(g,n,r):
  genind=generating_indices(g,n,r)
  gentob=genstobasis(g,n,r)
  numgens=len(gentob)
  M=[]
  
  for i in range(numgens):
    v=insertvec(gentob[i],numgens,genind)
    v[i]-=_sage_const_1 
    M.append(v)
  
  return matrix(M)  
    
    
def insertvec(w,length,positions):
  v=vector(QQ,length)
  for j in range(len(positions)):
    v[positions[j]]=w[j]
  return v        

############
#
# Test routines
#
############


def pullpushtest(g,dat,r):
  r"""Test if for Hurwitz space specified by (g,dat), pulling back codimension r relations under the source map and pushing forward under the target map gives relations.
  """
  Gr=trivGgraph(g,dat)
  n=Gr.gamma.n()
  
  Grquot=Gr.quotient_graph()
  gquot=Grquot.g()
  nquot=Grquot.n()
  
  M=FZreconstruct(g,n,r)
  
  N=matrix([Hpullpush(g,dat,alpha).toTautbasis(gquot,nquot,r) for alpha in tautgens(g,n,r)])
  
  return (N.transpose()*M.transpose()).is_zero()
  
  for v in M.rows():
    if not v.is_zero():
      alpha=Tautv_to_tautclass(v,g,n,r)
      pb=Hpullpush(g,dat,alpha)
      print(pb.is_zero())


# compares intersection numbers of Pixton generators computed by Pixton's program and by own program
# computes all numbers between generators for \bar M_{g,n} in degrees r, 3g-3+n-r, respectively
def checkintnum(g,n,r):
  markings=tuple(range(_sage_const_1 ,n+_sage_const_1 ))
  Mpixton=DR.pairing_matrix(g,r,markings)
  
  strata1=[Graphtodecstratum(Grr) for Grr in DR.all_strata(g,r,markings)]
  strata2=[Graphtodecstratum(Grr) for Grr in DR.all_strata(g,_sage_const_3 *g-_sage_const_3 +n-r,markings)]
  Mself=[[(s1*s2).evaluate() for s2 in strata2] for s1 in strata1]
  
  return Mpixton==Mself
  

# pulls back all generators of degree r to the boundary divisors and identifies them, checks if results are compatible with FZ-relations between generators
def pullandidentify(g,n,r):
  markings=tuple(range(_sage_const_1 ,n+_sage_const_1 ))
  M=DR.FZ_matrix(g,r,markings)
  Mconv=matrix([DR.convert_vector_to_monomial_basis(M.row(i),g,r,markings) for i in range(M.nrows())])  
  
  L=list_strata(g,n,_sage_const_1 )
  strata = DR.all_strata(g, r, markings)
  decst=[Graphtodecstratum(Grr) for Grr in strata] 
  
  for l in L:
    pullbacks=[((l.boundary_pullback(st)).dimension_filter()).totensorTautbasis(r,True) for st in decst]
    for i in range(Mconv.nrows()):
      vec=_sage_const_0 *pullbacks[0]
      for j in range(Mconv.ncols()):
        if Mconv[i,j]!=_sage_const_0 :
          vec+=Mconv[i,j]*pullbacks[j]
      if not vec.is_zero():
        return False
  return True
        

# computes all intersection numbers of generators of R^(r1)(\bar M_{g,n1}) with pushforwards of generators of R^(r2)(\bar M_{g,n2}), where n1<n2
# compares with result when pulling back and intersecting
# condition: r1 + r2- (n2-n1) = 3*g-3+n1
def pushpullcompat(g,n1,n2,r1):
  #global cu
  #global cd
  
  r2=_sage_const_3 *g-_sage_const_3 +n2-r1
  
  strata_down=[tautclass([Graphtodecstratum(Grr)]) for Grr in DR.all_strata(g,r1,tuple(range(_sage_const_1 ,n1+_sage_const_1 )))]
  strata_up=[tautclass([Graphtodecstratum(Grr)]) for Grr in DR.all_strata(g,r2,tuple(range(_sage_const_1 ,n2+_sage_const_1 )))]
  
  fmarkings=list(range(n1+_sage_const_1 ,n2+_sage_const_1 ))
  
  for class_down in strata_down:
    for class_up in strata_up:
      intersection_down = (class_down*class_up.forgetful_pushforward(fmarkings)).evaluate()
      intersection_up = (class_down.forgetful_pullback(fmarkings) * class_up).evaluate()
      
      if not intersection_down == intersection_up:
        return False
  return True


# test delta-pullback composed with delta-pushforward is multiplication with delta-degree for classes in R^r(\bar M_{g',b}) on space of quotient curves
def deltapullpush(g,H,r):
  trivGg=trivGgraph(g,H)
  trivGclass=Htautclass([Hdecstratum(trivGg)])
  ddeg=trivGg.delta_degree(_sage_const_0 )
  quotgr=trivGg.quotient_graph()
  gprime=quotgr.genera[0]
  bprime=len(quotgr.legs[0])
  
  gens=tautgens(gprime,bprime,r)
  
  for cl in gens:
    clpp=trivGclass.quotient_pullback(cl).quotient_pushforward()
    if not (clpp.toTautvect(gprime,bprime,r)==ddeg*cl.toTautvect(gprime,bprime,r)):
      return False
    
    #print 'The class \n'+repr(cl)+'\npulls back to\n'+repr(trivGclass.quotient_pullback(cl))+'\nunder delta*.\n'
  return True


## Lambda-classes must satisfy this:
def lambdaintnumcheck(g):
  intnum=((lambdaclass(g,g,_sage_const_0 )*lambdaclass(g-_sage_const_1 ,g,_sage_const_0 )).simplify()*lambdaclass(g-_sage_const_2 ,g,_sage_const_0 )).evaluate()
  result=-_sage_const_1 /_sage_const_2 *(_sage_const_1 /factorial(_sage_const_2 *(g-_sage_const_1 )))*bernoulli(_sage_const_2 *(g-_sage_const_1 ))/(_sage_const_2 *(g-_sage_const_1 ))*bernoulli(_sage_const_2 *g)/(_sage_const_2 *g)
  return intnum==result

@cached_function
def ct_space(g,n,r):
  r"""
  Returns a vector space W over QQ which is the quotient W = V / U, where
  V = space of vectors representing classes in R^r(\Mbar_{g,n}) in a basis
  U = subspace of vectors representing classes supported outside the compact-type locus M^{ct}_{g,n}
  Thus for v in V, the vector W(v) is the representation of the class represented by v
  in a basis of R^r(M^{ct}_{g,n}).
  """
  Msm=[]
  for t in tautgens(g,n,r):
    if len(t.terms[0].gamma.edges)-len(t.terms[0].gamma.genera)+1!=0:
      # t is supported on a graph outside the compact type locus (not a tree)
      Msm.append(t.toTautbasis()) 
  MsmM=matrix(QQ,Msm)
  U=MsmM.row_space()
  W=U.ambient_vector_space()/U
  return W       
        
############
#
# Further doctests
#
############
r"""
EXAMPLES::

    sage: from admcycles import *
    sage: from admcycles.admcycles import pullpushtest, deltapullpush, checkintnum, pullandidentify, pushpullcompat, lambdaintnumcheck
    sage: G=PermutationGroup([(1,2)])
    sage: H=HurData(G,[G[1],G[1]])
    sage: pullpushtest(2,H,1)
    True
    sage: pullpushtest(2,H,2) # long time
    True
    sage: deltapullpush(2,H,1)
    True
    sage: deltapullpush(2,H,2) # long time
    True
    sage: G=PermutationGroup([(1,2,3)])
    sage: H=HurData(G,[G[0]])
    sage: c=Hidentify(1,H)
    sage: c.toTautbasis()
    (5, -3, 2, 2, 2)
    sage: checkintnum(2,0,1)
    True
    sage: checkintnum(2,1,2)
    True
    sage: pullandidentify(2,1,2)
    True
    sage: pullandidentify(3,0,2)
    True
    sage: pushpullcompat(2,0,1,2) # long time
    True
    sage: lambdaintnumcheck(2)
    True
    sage: lambdaintnumcheck(3) # long time
    True

"""      

