
from gurobipy import *


def solve():
    # some dummy variables so that we can test
    buildings = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10"]
    heatpumps = ["H1", "H2", "H3", "H4", "H5"]

    # {"B1:100, "B2":200,...,"B10":1000}
    benefits = {buildings[i]: i*100 for i in range(len(buildings))}
    # {"H1":1, "H2":2,...,"H5":5}
    costs = {heatpumps[i]: i+1 for i in range(len(heatpumps))}
    P = {}

    model = Model("Heatpumps")
    # for x in heatpumps:
    #     costs[x] = installation_cost[x] + cost_of_electric[x]

    # Variables
    for b in buildings:
        for h in heatpumps:
            P[(h, b)] = model.addVar(vtype=GRB.BINARY, name=f'P({h},{b})')
    for b in buildings:
        model.addConstr(quicksum(P[(h, b)] for h in heatpumps) <= 1)

    # Constraints
    model.addConstr(quicksum(P[(h, b)]*benefits[b]
                             for h in heatpumps for b in buildings) >= 2000)

    # Objective
    model.setObjective(quicksum(P[(h, b)] * costs[h]
                       for h in heatpumps for b in buildings), GRB.MINIMIZE)
    model.update()
    model.optimize()
    model.write("model.lp")
    print(model.getObjective())
    for v in model.getVars():
        if v.x == 1:
            print(v.varName)

solve()
