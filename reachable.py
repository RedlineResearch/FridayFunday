############################################
# Copyright (c) 2012 Ganesh Gopalakrishnan ganesh@cs.utah.edu
#
# Check if the given graph has a Hamiltonian cycle.
#
# Author: Ganesh Gopalakrishnan ganesh@cs.utah.edu
############################################
from z3 import *

def gencon(gr, a, b):
    """
    Input a graph as an adjacency list, e.g. {0:[1,2], 1:[2], 2:[1,0]}.
    Produces solver to check if the given graph has
    a Hamiltonian cycle. Query the solver using s.check() and if sat,
    then s.model() spells out the cycle. Two example graphs from
    http://en.wikipedia.org/wiki/Hamiltonian_path are tested.

    =======================================================

    Explanation:

    Generate a list of Int vars. Constrain the first Int var ("Node 0") to be 0.
    Pick a node i, and attempt to number all nodes reachable from i to have a
    number one higher (mod L) than assigned to node i (use an Or constraint).

    =======================================================
    """
    #L = len(gr)
    #cv = [Int('cv%s'%i) for i in range(L)]
    s = Solver()
    #s.add(source==0)
    #for i in range(L):
    aToB = Bool('atob')
    bToA = Bool('btoa')
    #s.add(Or([a==j for j in gr[b]]))
    s.add(bToA == Or([a==j for j in gr[b]]))
    s.add(aToB == Or([b==j for j in gr[a]]))
    s.add(Or([aToB,bToA]))
    return s


def isReachable(gr, v, w):
  reach = Function('reach', IntSort(), IntSort(), BoolSort())
  a = Int('a')
  b = Int('b')
  c = Int('c')

  s = Solver()
  transitive_reach = ForAll([a,b,c], Implies(And(reach(a,b) == True , reach(b,c) == True),
                                                 reach(a,c) == True))
  reflexive_reach = ForAll([a], reach(a,a) == True)

  #s.add(transitive_reach)
  #s.add(reflexive_reach)

  f = And(transitive_reach, reflexive_reach)
  for (node, neighbors) in gr.iteritems():
    for neighbor in neighbors:
      f=And(f, reach(node, neighbor) == True)

  # s.add(reach(v, w) == False)

  return prove(Implies(f, reach(v, w)))
  #return s.check() == unsat



def examples():
    #print(sdodec.model())
    # =======================================================
    # See http://en.wikipedia.org/wiki/Hamiltonian_path for the Herschel graph
    # being the smallest possible polyhdral graph that does not have a Hamiltonian
    # cycle.
    #
    grherschel = { 0: [1, 9, 10, 7],
                   1: [0, 8, 2],
                   2: [1, 9, 3],
                   3: [2, 8, 4],
                   4: [3, 9, 10, 5],
                   5: [4, 8, 6],
                   6: [5, 10, 7],
                   7: [6, 8, 0],
                   8: [1, 3, 5, 7],
                   9: [2, 0, 4],
                   10: [6, 4, 0],
                   11: [12],
                   12: [11]}
    #pp.pprint(grherschel)
    #sherschel=gencon(grherschel)
    #print(sherschel.check())
    # =======================================================

    print "0 reaches 6? " + str(isReachable(grherschel, 0,6))
    # print "100343 reaches 343214234? " + str(isReachable(grherschel, 100343, 343214234))
    # print "0 reaches 12? " + str(isReachable(grherschel, 0, 12))

if __name__ == "__main__":
    examples()
