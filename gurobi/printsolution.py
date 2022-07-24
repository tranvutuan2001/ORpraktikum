# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 17:23:47 2022
@author: ciesl
"""
from gurobipy import GRB
from datetime import datetime
import os
import csv
dirname = os.path.dirname(__file__)


def write_solution_csv(model, D, M, I, T, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
                       CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
                       CO2_EMISSION_PRICE, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
                       electr_timefactor, gas_timefactor, CO2_timefactor, P, ELECTRICITY_SUBS, HEATPUMP_SUBS, name):
    model.printStats()
    status = model.Status
    if status != GRB.OPTIMAL:
        print("Current model is infeasible")
        return
   
    
    if not os.path.exists(os.path.join(dirname, "solutions\solution.csv")):
        print("new file is created with headers")
        
        f = open(os.path.join(dirname, "solutions\solution.csv"), 'a', newline="")
        header=["name","district", "year construct", "type of building", "heat capacity", "HPModel", "Year","qty newly built HP", "cumul.QTY", "totalhouses", "percent of totalhouses", "average heat demand",
         "distributor","zipcode"]
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        f.close()

        f = open(os.path.join(dirname, "solutions\datasets.csv"), 'a', newline="")
        header=["name", "NUMBER_OF_YEARS", "MIN_PERCENTAGE", "CO2_EMISSION_GAS", "CO2_EMISSION_EON", "BOILER_EFFICIENCY", "CO2_EMISSION_PRICE", "max_sales", "AVERAGE_BOILER_COST_PER_UNIT", "ELECTRICITY_COST_PER_UNIT",
        "electr_timefactor", "gas_timefactor", "CO2_timefactor", "ELECTRICITY_SUBS", "HEATPUMP_SUBS"]
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        f.close()
        
    f = open(os.path.join(dirname, "solutions\solution.csv"), 'a', newline="")    
    writer = csv.writer(f, delimiter=";")
    c = 0
    
    for m, i, d, t in P:
        new_installs= abs(model.getVarByName(f'hp_type_{str(m)}_at_house_type_{str(i)}_by_distributor_{str(distributors[d]["name"])}_in_year_{str(t)}').X)
        cumulated_amount= abs(sum(model.getVarByName(f'hp_type_{str(m)}_at_house_type_{str(i)}_by_distributor_{str(distributors[d]["name"])}_in_year_{str(t)}').X for t in range(t+1)))
        if new_installs ==0 and cumulated_amount==0:
            continue
        else:
            percent_new = round(new_installs / I[i]["quantity"],2)
            percent_cumul= round(cumulated_amount / I[i]["quantity"],2)
            row = [name, I[i]["district"], I[i]["year of construction"], I[i]["type of building"], I[i]["Heatcapacity"], M[m]['brand_name'], t,newbuilds,qty, I[i]["quantity"], percent, I[i]["average heat demand"], distributors[d]['name'], I[i]["zipcode"]
            writer.writerow([r for r in row])
        
        if c==0:
            f2 = open(os.path.join(dirname, "solutions\datasets.csv"), 'a', newline="")    
            writer2 = csv.writer(f2, delimiter=";")
            row = [name,
            NUMBER_OF_YEARS, MIN_PERCENTAGE,
            CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
            CO2_EMISSION_PRICE, max_sales[NUMBER_OF_YEARS -
            1], AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
            electr_timefactor[NUMBER_OF_YEARS-1], gas_timefactor[NUMBER_OF_YEARS-1], CO2_timefactor[NUMBER_OF_YEARS-1], ELECTRICITY_SUBS, HEATPUMP_SUBS]
            writer2.writerow(row)
            f2.close()
            c=1

    f.close()

    

    return

