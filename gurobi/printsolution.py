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
                       electr_timefactor, gas_timefactor, CO2_timefactor, P, ELECTRICITY_SUBS, HEATPUMP_SUBS):
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
        "electr_timefactor", "gas_timefactor", "CO2_timefactor","zipcode", "ELECTRICITY_SUBS", "HEATPUMP_SUBS"]
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        f.close()
        
    f = open(os.path.join(dirname, "solutions\solution.csv"), 'a', newline="")    
    writer = csv.writer(f, delimiter=";")
    
    for m, i, d, t in P:
        if t >= 0:
            try:
                curr = model.getVarByName(
                    f'hp_type_{str(m)}_at_house_type_{str(i)}_by_distributor_{str(distributors[d]["name"])}_in_year_{str(t)}').X
            except:
                continue
        
            if curr != 0:
                try: 
                    prev = model.getVarByName(
                        f'hp_type_{str(m)}_at_house_type_{str(i)}_by_distributor_{str(distributors[d]["name"])}_in_year_{str(t-1)}').X
                except:
                   prev=0 
                newbuilds = curr-prev
                qty = curr
                percent = qty / I[i]["quantity"]
                row = [I[i]["district"], I[i]["year of construction"], I[i]["type of building"], I[i]["modernization status"], M[m]['brand_name'], t,newbuilds,qty, I[i]["quantity"], percent, str(I[i]["max_heat_demand_W/m^2"]), distributors[d]['name'], datetime.now(
                          ).strftime("%Y_%m_%d-%I_%M_%S_%p"),
                      NUMBER_OF_YEARS, MIN_PERCENTAGE,
                      CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
                      CO2_EMISSION_PRICE, max_sales[NUMBER_OF_YEARS -
                                              1], AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
                      electr_timefactor[NUMBER_OF_YEARS-1], gas_timefactor[NUMBER_OF_YEARS-1], CO2_timefactor[NUMBER_OF_YEARS-1], I[i]["zipcode"]], ELECTRICITY_SUBS, HEATPUMP_SUBS
                writer.writerow([str(r) for r in row])
    f.close()
    return

