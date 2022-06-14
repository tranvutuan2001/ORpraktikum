# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# Template for our final model

from gurobipy import *
from gurobipy import GRB
import numpy as np
import os

from dataprp import data_preprocess, prepare_params
from printsolution import write_solution_csv
import timeit, csv

dirname = os.path.dirname(__file__)

NUMBER_OF_MONTHS = 9  # number of months
MIN_PERCENTAGE = 0.8  # minimum required share of houses that receive HP
# from https://www.volker-quaschning.de/datserv/CO2-spez/index_e.php
CO2_EMISSION_GAS = 433 # gramm/ kwh
# from https://www.eon.de/de/gk/strom/oekostrom.html#:~:text=Im%20Jahr%201990%20lag%20der,der%20CO%202%2DEmissionen%20leisten.
CO2_EMISSION_EON = 366 # gramm/kwh in 2020
# from https://www.umweltbundesamt.de/daten/umwelt-wirtschaft/gesellschaftliche-kosten-von-umweltbelastungen#klimakosten-von-treibhausgas-emissionen
CO2_EMISSION_PRICE_1 =  201E-6  # euro/gramm,  suggestion by German Environment Agency
CO2_EMISSION_PRICE_2 =  698E-6  # euro/gram,   then balanced with the welfare losses caused by climate change for current and future generations
BOILER_EFFICIENCY = 0.7

def solve():
    """Solves the heat pump problem.

    T (int): number of months startting from January
    M (dict) : dictionary of heat pumps, each containing the keys:
        'brand_name' (str) : brand name of the heat pump
        'cop' (float) : COP of the heat pump
        'produced heat' (float) : heat produced by the heat pump
        'price'(float) : price of heat pump including installation and accessories
    I (dict) : dictionary of buildings each containing the keys:
        "building_type" (str) : building type
        "modernization_status" (str) : status of the building (i.e. whether it is modernized or not)
        "max_heat_demand" (int)  : maximum heat demand of the building (in kWh/m^2)
        "district" (str) : district of the building
        "quantity" (int) : number of buildings of the same type in the district
    D (dict) dictionary of working capacity of every district
        D = {district: workforce}
        (district: String, workforce: int)
    __________________________________________________________________________________________________________

    """

    # Preparation of Data and Parameters
    T = NUMBER_OF_MONTHS
    D, M, I, fitness = data_preprocess()
    max_sales, heatdemand, boilercosts, hpcosts, hpinvestment,  electr_timefactor, \
        gas_timefactor, electr_locationfactor, gas_locationfactor, CO2_timefactor, hpCO2 = prepare_params(T, I, M, D)

    # Create a new model
    print("Preparing the model\n")
    model = Model("Heatpumps")
    # Add Variables
    print("Adding variables")
    start = timeit.default_timer()
    print(len(M) * len(I) * T, "variables will be added")
    # Quantity of installed heat pumps with given conditions
    x = {}
    for m in M:
        for i in I:
            for t in range(T):
                # name = f"x: install hp_{str(m)} in house_{str(i)} in district_{str(s)} in month_{str(t)}"
                x[m, i, t] = model.addVar(
                    vtype=GRB.INTEGER,
                    name=f'hp_type_{str(m)}_at_house_type_{str(i)}_in_month_{str(t)}'
                )
    stop = timeit.default_timer()
    print('Time in seconds to add the variables: ', stop - start, "\n")

    print("Adding the constraints")
    start = timeit.default_timer()
    # Constraint 1: Consider Installability : never assign HP if they do not fit to the house type
    for i in I:
        for m in M:
            for t in range(T):
                if fitness[i, m] == 0:
                    model.addConstr(x[m, i, t] == 0)

    # Constraint 2:  Install heat pumps in AT LEAST the specified percentage of all houses

    model.addConstr(
        quicksum(x[m, i, t] for m in M for i in I for t in range(T)) >= MIN_PERCENTAGE * quicksum(I[i]['quantity'] for i in I)
    )
    # Constraint 3: Only install as many heatpumps in a house category as the total quantity of houses of that type
    for i in I:
        model.addConstr(
            quicksum(x[m, i, t] for m in M for t in range(T)) <= I[i]['quantity']
        )

    # Constraint 4: Only install up to the current expected sales volume
    for t in range(T):
        model.addConstr(quicksum(x[m, i, t] for i in I for m in M) <= max_sales[t])

    # Constraints 5: Respect the operation radius for each distributor
    # TODO: add the constraint 5 as explained above

    # Constraint 6: Respect maximum worker capacity
    # TODO: implement the constraint "yearly workforce <= qty of heat pumps installed by the distributor"

    stop = timeit.default_timer()
    print("Time in seconds to add the constraints: ", stop - start, "\n")

    # Add Objective
    print("Adding objective function")
    start = timeit.default_timer()
    # TODO: add correct cost function

    obj = quicksum((x[m, i, t] * hpinvestment[m]
                     + quicksum( x[m, i, t_1] * ( hpcosts[m] * electr_timefactor[t_1] * electr_locationfactor[d] 
                                                           + hpCO2[m] * CO2_EMISSION_PRICE_1 * CO2_timefactor[t_1])
                                               * heatdemand[i, t_1] for t_1 in range(t + 1) )
                     + (I[i]['quantity'] - quicksum(x[m, i,  t_1] for t_1 in range(t + 1)))
                                     * ( boilercosts[i] * gas_timefactor[t] * gas_locationfactor[d] 
                                                          + CO2_EMISSION_GAS / BOILER_EFFICIENCY * CO2_EMISSION_PRICE_1 * CO2_timefactor[t] )
                    * heatdemand[i, t])  
                   for m in M for i in I  for d in D for t in range(T))
    model.setObjective(obj, GRB.MINIMIZE)
    stop = timeit.default_timer()
    print('Time in seconds to add the objective function: ', stop - start, "\n")
    model.update()

    # Solve Model
    print("Solving the model")
    start = timeit.default_timer()
    model.write(os.path.join(dirname, "solutions\model.lp"))
    model.optimize()
    stop = timeit.default_timer()
    write_solution_csv(model, D, M, I, T)
    print('Time in seconds to solve the model: ', stop - start, "\n")

    return model

    """ For testing purposes, can be ignored
    print("Set threshold as",MIN_PERCENTAGE)
    k=0
    tot= sum(I[i]["quantity"] for i in I)
    for t in range(T):
        val= int(sum([model.getVarByName(f'hp_type_{str(m)}_at_house_type_{str(i)}_in_month_{str(t)}').X for m in M for i in I]))
        k=k+val
        
        print("t=%02d "%(t,),": build", val,"houses", "with maximum houses", tot)
    p=100*k/tot
    print(p,"% wurde erfüllt beim Threshold ",MIN_PERCENTAGE)    
    """
    return


solve()
