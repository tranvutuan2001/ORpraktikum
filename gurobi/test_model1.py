
from cgi import print_form
from gurobipy import *

eoncost = 0.437   # euro per kwh


def solve():
    # some dummy variables so that we can test
    buildings = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10"]
    heatpumps = ["H1", "H2", "H3", "H4", "H5"]


    # {"B1:100, "B2":200,...,"B10":1000}
    benefits = {buildings[i]: i*100 for i in range(len(buildings))}
    # {"H1":1, "H2":2,...,"H5":5}
    costs = {heatpumps[i]: i+1 for i in range(len(heatpumps))}
    area = {buildings[i]: i*40 for i in range(len(buildings))}
    demand = {buildings[i]: i for i in range(len(buildings))}
    # P = {}

    model = Model("Heatpumps")
    # for x in heatpumps:
    #     costs[x] = installation_cost[x] + cost_of_electric[x]

    # Variables   
    P = model.addVars(heatpumps, buildings, name = "P" )
   
    
     # Constraints
    model.addConstrs(P.sum(h, '*') <=1 for h in heatpumps )
    model.addConstr(quicksum(P[(h, b)]*benefits[b]
                             for h in heatpumps for b in buildings) >= 3000)

    # Objective
    obj = quicksum(P[(h, b)] * (costs[h] + area[b]*demand[b]*eoncost )
                       for h in heatpumps for b in buildings)
    model.setObjective(obj, GRB.MINIMIZE)
    model.update()
    model.optimize()
    model.write("model.lp")
    print(model.getObjective())
    for v in model.getVars():
        if v.x == 1:
            print(v.varName)

            
            
            
solve()



