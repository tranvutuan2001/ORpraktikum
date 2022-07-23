# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# Template for our final model

from gurobipy import Model, quicksum, GRB, tuplelist
import os
from printsolution import write_solution_csv
import timeit

dirname = os.path.dirname(__file__)


def solve(districts, heatpumps, housing, fitness, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
          CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY, CO2_EMISSION_PRICE,
          max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
          electr_timefactor, gas_timefactor, CO2_timefactor, CO2EMIS_timefactor, configurations, WORKFORCE_FACTOR, ELECTRICITY_SUBS, HEATPUMP_SUBS):
    """Solves the heat pump problem.

    NUMBER OF YEARS (int): number of years to be considered for the model
    heatpumps (dict) : dictionary of heat pumps, each containing the keys:
        'brand_name' (str) : brand name of the heat pump
        'cop' (float) : COP (A2/W35) of the heat pump
        'produced heat' (float) : heat produced by the heat pump
        'price'(float) : price of heat pump including installation and accessories
    housing (dict) : dictionary of buildings each containing the keys:
        "type of building" (str) : building type
        "modernization_status" (str) : status of the building (i.e. whether it is modernized or not)
        "max_heat_demand_W/m^2" (int)  : Standard heating load according to DIN12831 in the form of standard values from technical literature/BWP w/m^2
        "district" (str) : district of the building
        "quantity" (int) : number of buildings of the same type in the district
        "Surface area" (float) : size of residental space
        "average heat demand" (float): demand kwh/m^2
        "year of construction" (int): year of construction
        "long" (float): longitude of house
        "lat" (float): latitude of house
    distributors (dict) : dictionary of heat pump installers
        "name" (str): name of the company
        "long" (str): longitude of company location
        "lat" (str): latitude of company location
        "zipcode" (int) : zipcode
        "max_installations" (int):  amount of possible total heat pump installation by the company per year

    __________________________________________________________________________________________________________

    """

    T = NUMBER_OF_YEARS
    # Create a new model
    print("Preparing the model\n")
    model = Model("Heatpumps")

    P = configurations
    index_heatpump = set(m for m, _, _, _ in P)
    index_housing = set(i for _, i, _, _ in P)
    # print("index_housing", index_housing)
    index_distributor = set(d for _, _, d, _ in P)
    index_time = set(t for _, _, _, t in P)
    # Add Variables
    print("Adding variables")
    start = timeit.default_timer()
    print(len(P), "variables will be added")
    # Quantity of newly installed heat pumps with given conditions
    
    x = {}
    for m, i, d, t in P:
        # if t >= 0:
        x[m, i, d, t] = model.addVar(vtype='I', lb=0,
                                     name=f'hp_type_{str(m)}_at_house_type_{str(i)}_by_distributor_{str(distributors[d]["name"])}_in_year_{str(t)}')
        # else:
        #     x[m, i, d, t] = 0

    stop = timeit.default_timer()
    print('Time to add the variables: ', f"{round(stop - start, 2)} seconds\n")

    print("Adding the constraints")
    start = timeit.default_timer()

    # Constraint 1: Consider Installability : never assign Heat Pump to a housetype if they do not fit to the house type
    # removed because this is handled by get_configurations

    # Constraint 2:  Install heat pumps in AT LEAST the specified percentage of all houses
    house_count = sum(housing[i]['quantity'] for i in housing) 

    # model.addConstr(
    #     quicksum(x[p] for p in P.select('*', '*', '*', T - 1)) >= MIN_PERCENTAGE * house_count, name="C2")

    # Constraint 3: Only install as many heatpumps in a house category as the total quantity of houses of that type
    for i in index_housing:
        model.addConstr(quicksum(x[p] for p in P.select("*", i, "*", "*")) <= housing[i]['quantity'], name="C3")

    # Constraint 4: Only install up to the current expected sales volume
    for t in range(T):
        model.addConstr(quicksum(x[m, i, d, t] for m, i, d, _ in P.select("*", "*", "*", t)) <= max_sales[t], name="C4")

    # Constraints 5: Respect the operation radius for each distributor
    # removed because this is handled by get_configurations

    # Constraint 6: Respect max_installations capacity
    # yearly workforce <= qty of heat pumps installed by the distributor
    for t in range(T):
        for d in index_distributor:
                model.addConstr(quicksum(x[m, i, d, t] for m, i, _, _ in P.select("*", "*", d, t)) <= distributors[d]['max_installations'] * pow(WORKFORCE_FACTOR,t), name = "C6")


    stop = timeit.default_timer()
    print("Time to add the constraints: ",
          f"{round(stop - start, 2)} seconds\n")

    # Add Objective
    print("Adding objective function")
    start = timeit.default_timer()
    
    """
          We calculate and sum yearly operation costs for each house and add the costs for inital
          installations of heat pumps.
    """
    # TODO: find a better cost function : lifespan of boiler/heatpumps, total cost of ownership/
    investcost = quicksum(x[m, i, d, t]* heatpumps[m]['price']* 1e-6 * HEATPUMP_SUBS * (T - t) / T for m, i, d, t in P)

    hpcost =quicksum(quicksum(x[m, i, d, t] for t in range(t)) * ((ELECTRICITY_COST_PER_UNIT * ELECTRICITY_SUBS * electr_timefactor[t] + CO2_EMISSION_EON * CO2_EMISSION_PRICE *CO2_timefactor[t] * CO2EMIS_timefactor[t]) / heatpumps[m]['cop'] * housing[i]['average heat demand'])for m,i,d,t in P)

    
    gascost = quicksum((house_count - quicksum(x[m, i, d, t] for t in range(t))) * ((AVERAGE_BOILER_COST_PER_UNIT * gas_timefactor[t] + CO2_EMISSION_GAS * CO2_EMISSION_PRICE * CO2_timefactor[t]) / BOILER_EFFICIENCY * housing[i]['average heat demand']) for m, i, d, t in P)

    obj = investcost + hpcost + gascost
    model.setObjective(obj, GRB.MINIMIZE)
    #    for p in P:
    #        print(p[2])
    stop = timeit.default_timer()
    print('Time to add the objective function: ',
          f"{round(stop - start, 2)} seconds\n")
    model.update()

    # Solve Model
    print("Solving the model")
    start = timeit.default_timer()
    model.write(os.path.join(dirname, "solutions\model.lp"))
    model.optimize()

    # Print model details and solution
    # model.computeIIS()
    # model.write(os.path.join(dirname, "solutions\model.ilp"))
    stop = timeit.default_timer()

    print('Time to solve the model: ',
          f"{round(stop - start, 2)} seconds\n")

    return model

