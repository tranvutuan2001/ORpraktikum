# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 17:23:47 2022
@author: ciesl
"""
from gurobipy import *
from datetime import datetime
import os
import csv
dirname = os.path.dirname(__file__)


def write_solution_csv(model, D, M, I, T, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
                       CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
                       CO2_EMISSION_PRICE, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
                       electr_timefactor, gas_timefactor, CO2_timefactor, P):
    model.printStats()
    status = model.Status
    if status != GRB.OPTIMAL:
        print("Current model is infeasible")
        return
    # f = open(os.path.join(dirname, "solutions\solution_"+ datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") +".csv"), 'w', newline="")
    # writer = csv.writer(f, delimiter=";")
    # writer.writerow(
    #     ["district", "year construct", "type", "modern", "HPModel", "Year", "QTY", "totalhouses", "percent of totalhouses", "heatcapacity",
    #      "distributor"])
    # for i in I:
    #     for m in M:
    #         for t in range(T):
    #             for d in distributors:
    #                 var = model.getVarByName(
    #                     f'hp_type_{str(m)}_at_house_type_{str(i)}_in_year_{str(t)}_by_distributor_{str(distributors[d]["name"])}').X
    #                 if var != 0:
    #                     p = var
    #                     percent = p / I[i]["quantity"]
    #                     row = [I[i]["district"], I[i]["year of construction"], I[i]["type of building"], I[i]["modernization status"], M[m]['brand_name'], t,
    #                            int(p), I[i]["quantity"], percent, I[i]["max_heat_demand_Patrick"], distributors[d]['name']]
    #                     writer.writerow(row)
    # f.close()
    f = open(os.path.join(dirname, "solutions\solution.csv"), 'a', newline="")
    writer = csv.writer(f, delimiter=";")
    '''writer.writerow(
        ["district", "year construct", "type", "modern", "HPModel", "Year", "QTY", "totalhouses", "percent of totalhouses", "heatcapacity",
         "distributor","data_timestamp"
         "NUMBER_OF_YEARS", "MIN_PERCENTAGE",
        "CO2_EMISSION_GAS", "CO2_EMISSION_EON", "BOILER_EFFICIENCY", 
        "CO2_EMISSION_PRICE", "max_sales", "AVERAGE_BOILER_COST_PER_UNIT", "ELECTRICITY_COST_PER_UNIT",
        "electr_timefactor", "gas_timefactor", "CO2_timefactor"])'''

    for p in P:
        try:
            var = model.getVarByName(
                f'hp_type_{str(p[0])}_at_house_type_{str(p[1])}_by_distributor_{str(distributors[p[2]]["name"])}_in_year_{str(p[3])}').X
        except:
            continue
    if var != 0:
        p1 = var
        i = p[1]
        m = p[0]
        d = p[2]
        t = p[3]

        percent = p1 / I[i]["quantity"]
        row = [I[i]["district"], I[i]["year of construction"], I[i]["type of building"], I[i]["modernization status"], M[m]['brand_name'], t,
               int(p1), I[i]["quantity"], percent, I[i]["max_heat_demand_W/m^2"], distributors[d]['name'], datetime.now(
        ).strftime("%Y_%m_%d-%I_%M_%S_%p"),
            NUMBER_OF_YEARS, MIN_PERCENTAGE,
            CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
            CO2_EMISSION_PRICE, max_sales[NUMBER_OF_YEARS -
                                          1], AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
            electr_timefactor[NUMBER_OF_YEARS-1], gas_timefactor[NUMBER_OF_YEARS-1], CO2_timefactor[NUMBER_OF_YEARS-1]], I[i]["zipcode"]
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
