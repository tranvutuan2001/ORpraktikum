# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 17:23:47 2022

@author: ciesl
"""

from gurobipy import *
import os
import csv

dirname = os.path.dirname(__file__)


def write_solution_csv(model, D, M, I, T):
    status = model.Status
    if status != GRB.OPTIMAL:
        print("Current model is infeasible")
        return

    f = open(os.path.join(dirname, "solutions\solution.csv"), 'w', newline="")
    writer = csv.writer(f, delimiter=";")
    writer.writerow(
        ["district", "year construct", "type", "modern", "HPModel", "Year", "QTY", "totalhouses", "percent of totalhouses", "heatcapacity"])
    for i in I:
        for m in M:
            for t in range(T):
                if model.getVarByName(f'hp_type_{str(m)}_at_house_type_{str(i)}_in_month_{str(t)}').X != 0:
                    p = model.getVarByName(f'hp_type_{str(m)}_at_house_type_{str(i)}_in_month_{str(t)}').X
                    percent = p / I[i]["quantity"]
                    row = [I[i]["district"], I[i]["year of construction"], I[i]["type of building"], I[i]["modernization status"], m, t,
                           int(p), I[i]["quantity"], percent, I[i]["max_heat_demand_Patrick"]]
                    writer.writerow(row)
    f.close()
    return


"""legacy code  
def write_solution(model, D, M, I):
    status = model.Status
    if status != GRB.OPTIMAL:
        print("Current model is infeasible")
        with open('optimization_result.txt', 'w') as f:
            f.write("infeasible")
        return
    
    with open(os.path.join(dirname,"solutions\optimization_result.txt", 'w')) as f:
        f.write('Work force configuration:\n')
        for index in D:
            f.write(f'{index}: {D[index]}\n')
            
    

        f.write('\n')
        f.write('Heat pump models configuration:\n')
        for index in M:
            f.write(f'{index}: {M[index]}\n')

        f.write('\n')
        f.write('House type configuration:\n')
        for index in I:
            f.write(f'{index}: {I[index]}\n')

        f.write('\n')
        f.write('Optimal variable set:\n')
        res = json.loads(model.getJSONSolution())['Vars']
        for var in res:
            f.write(f'{var}\n')    
        return
 """