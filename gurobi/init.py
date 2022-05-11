#!/usr/bin/env python3
from gurobipy import *


def solve():
    buildings = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10"]
    benefits = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    heatpumps = ["H1", "H2", "H3", "H4", "H5"]
    costs = [1, 2, 3, 4, 5]
    P = {}

    model = Model("Heatpumps")
    # for x in heatpumps:
    #     costs[x] = installation_cost[x] + cost_of_electric[x]

    for y in buildings:
        for x in heatpumps:
            P[(x, y)] = model.addVar(vtype=GRB.BINARY, name=f'P({x},{y})')
    for y in buildings:
        model.addConstr(quicksum(P[(x, y)] for x in heatpumps) <= 1)

    
    model.addConstr(quicksum(P[(x, buildings[i])]*benefits[i]
                        for x in heatpumps for i in range(len(buildings))) >= 2000)

    model.setObjective(quicksum(P[(heatpumps[i], y)] * costs[i]
                       for i in range(len(heatpumps)) for y in buildings), GRB.MINIMIZE)
    model.update()
    model.optimize()
    model.write("model.lp")
    # print(model.getObjective())
    for v in model.getVars():
        if v.x == 1:
            print(v.varName)

solve()
