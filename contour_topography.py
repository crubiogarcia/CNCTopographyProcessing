"""
    Inputs:
        S: List of Surfaces ordered
        step: distance between surfaces
    Output:
        T: The topography surfaces"""

__author__ = "crubiogarcia"
__version__ = "2023.12.06"

import rhinoscriptsyntax as rs
import ghpythonlib.treehelpers as th
from itertools import combinations
from collections import defaultdict


#Convert to nested list
all = th.tree_to_list(S, None)

#get highest level contours
init = all.pop(0)

max_a = 0


for i in range(len(init)):
    area = rs.Area(init[i])
    if area > max_a:
        max_a = area
        elem = i

#initialize the list of the wanted curves
surfaces = []
aux = [init[i] for i in range(len(init)) if i != elem]

#append highest curves
surfaces.append(aux)
auxi =  surfaces

def get_curves(prev):
    
    global all
    
    #Create array
    possible = []
    possible = all.pop(0)
    
    if len(all)<1:
        return
    if isinstance(prev[0], list):
        previous = prev[0][0]
    else:
        previous = prev[0]
    cs = rs.DuplicateEdgeCurves(previous)
    if len(cs) > 1:
        cs = rs.JoinCurves(cs)
    
    for i in range(len(cs)):
        max = 0
        ln = rs.CurveLength(cs[i])
        if ln > max:
            max = ln
            cc=cs[i]

    p = rs.CurveAreaCentroid(cc)[0]
    cv= rs.OffsetCurve(cc,p,0.0001)

    pt = rs.CurveEndPoint(cv)
    scaled = rs.VectorScale([0,0,-1], STEP+1)
    line = rs.AddLine(pt, pt + scaled)

    for j in range(len(possible)):
        if rs.CurveBrepIntersect(line,possible[j]):
            want=j

    wanted = [want]
    unwanted = []
    
    adjacency_graph = build_surface_adjacency_graph(possible)
    splitlist(adjacency_graph, possible, want, wanted, unwanted, visited=None)
    
    srfs = [possible[i] for i in wanted]
    surfaces.append(srfs)
    
    get_curves(srfs)

def are_surfaces_adjacent(surface_id1, surface_id2):
    ls = [surface_id1, surface_id2]
    return len(rs.BooleanUnion(ls, False)) == 1

def build_surface_adjacency_graph(surface_ids):
    adjacency_graph = {}

    for surface_id1, surface_id2 in combinations(surface_ids, 2):
        if are_surfaces_adjacent(surface_id1, surface_id2):
            adjacency_graph[(surface_id1, surface_id2)] = True
            adjacency_graph[(surface_id2, surface_id1)] = True
        else:
            adjacency_graph[(surface_id1, surface_id2)] = False
            adjacency_graph[(surface_id2, surface_id1)] = False

    return adjacency_graph

def splitlist(graph, items, idx, yes, no, visited=None):
    if visited is None:
        visited = set()
    
    visited.add(idx)
    
    if idx in yes:
        for i in range(len(items)):
            if i != idx and graph[(items[idx], items[i])] == True and i not in no:
                no.append(i)
                splitlist(graph, items, i, yes, no, visited)
    
    elif idx in no:
        for j in range(len(items)):
            if j != idx and graph[(items[idx], items[j])] == True and j not in yes:
                yes.append(j)
                splitlist(graph, items, j, yes, no, visited)
    
    return


a = get_curves(auxi)

T = []
for i in surfaces:
    for j in i:
        T.append(j)



