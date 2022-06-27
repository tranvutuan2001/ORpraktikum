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
   
    
    if not os.path.exists(os.path.join(dirname, "solutions\solution.csv")):
        print("new file is created with headers")
        
        f = open(os.path.join(dirname, "solutions\solution.csv"), 'a', newline="")
        header=["district", "year construct", "type of building", "modern", "HPModel", "Year","qty newly built HP", "cumul.QTY", "totalhouses", "percent of totalhouses", "heatcapacity",
         "distributor","data_timestamp",
         "NUMBER_OF_YEARS", "MIN_PERCENTAGE",
        "CO2_EMISSION_GAS", "CO2_EMISSION_EON", "BOILER_EFFICIENCY", 
        "CO2_EMISSION_PRICE", "max_sales", "AVERAGE_BOILER_COST_PER_UNIT", "ELECTRICITY_COST_PER_UNIT",
        "electr_timefactor", "gas_timefactor", "CO2_timefactor","zipcode"]
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        f.close()
        
    f = open(os.path.join(dirname, "solutions\solution.csv"), 'a', newline="")    
    writer = csv.writer(f, delimiter=";")
    
    
    for p in P:
        if p[3]>=0:
            try:
                var = model.getVarByName(
                    f'hp_type_{str(p[0])}_at_house_type_{str(p[1])}_by_distributor_{str(distributors[p[2]]["name"])}_in_year_{str(p[3])}').X
            except:
                continue
        
            if var != 0:
                try: 
                    var2=model.getVarByName(f'hp_type_{str(p[0])}_at_house_type_{str(p[1])}_by_distributor_{str(distributors[p[2]]["name"])}_in_year_{str(p[3]-1)}').X
                except:
                   continue 
                newbuilds= var-var2
                qty=var
                i = p[1]
                m = p[0]
                d = p[2]
                t = p[3]
                percent = qty / I[i]["quantity"]
                row = [I[i]["district"], I[i]["year of construction"], I[i]["type of building"], I[i]["modernization status"], M[m]['brand_name'], t,newbuilds,qty, I[i]["quantity"], percent, str(I[i]["max_heat_demand_W/m^2"]), distributors[d]['name'], datetime.now(
                          ).strftime("%Y_%m_%d-%I_%M_%S_%p"),
                      NUMBER_OF_YEARS, MIN_PERCENTAGE,
                      CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
                      CO2_EMISSION_PRICE, max_sales[NUMBER_OF_YEARS -
                                              1], AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
                      electr_timefactor[NUMBER_OF_YEARS-1], gas_timefactor[NUMBER_OF_YEARS-1], CO2_timefactor[NUMBER_OF_YEARS-1], I[i]["zipcode"]]
                writer.writerow([str(r) for r in row])
    f.close()
    return

