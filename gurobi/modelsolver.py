# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# Template for our final model

from gurobipy import Model, quicksum, GRB
import os
from printsolution import write_solution_csv
import timeit
from utilities import cal_dist

dirname = os.path.dirname(__file__)


def solve(districts, heatpumps, housing, fitness, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
          CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY, CO2_EMISSION_PRICE,
          max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
          electr_timefactor, gas_timefactor, CO2_timefactor):
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
        "max_installations" (int): #TODO amount of possible total heat pump installation by the company per year

    __________________________________________________________________________________________________________

    """

    T = NUMBER_OF_YEARS
    # Create a new model
    print("Preparing the model\n")
    model = Model("Heatpumps")
    # Add Variables
    print("Adding variables")
    start = timeit.default_timer()
    print(len(heatpumps) * len(housing) * T *
          len(distributors), "variables will be added")
    # Quantity of installed heat pumps with given conditions
    x = {}
    # TODO: only add the variables for house/heatpump combinations that are feasible, do not add variables if fitness=0
    for m in heatpumps:
        for i in housing:
            if fitness[i,m]==0:
                for t in range(T):
                    for d in distributors:
                        x[m,i,t,d]=0
            else:
                for t in range(T):
                    for d in distributors:
                        x[m, i, t, d] = model.addVar(vtype='I',
                        name=f'hp_type_{str(m)}_at_house_type_{str(i)}_in_year_{str(t)}_by_distributor_{str(distributors[d]["name"])}'
                    )
    stop = timeit.default_timer()
    print('Time in seconds to add the variables: ', stop - start, "\n")

    print("Adding the constraints")
    start = timeit.default_timer()
   """
    # Constraint 1: Consider Installability : never assign Heat Pump to a housetype if they do not fit to the house type
    for i in housing:
        for m in heatpumps:
            if fitness[i, m] == 0:
                for t in range(T):
                    for d in distributors:
                        model.addConstr(x[m, i, t, d] == 0, name="C1")
    """
    # Constraint 2:  Install heat pumps in AT LEAST the specified percentage of all houses
    model.addConstr(
        quicksum(x[m, i, t, d] for m in heatpumps for i in housing for t in range(
            T) for d in distributors) >= MIN_PERCENTAGE * quicksum(housing[i]['quantity'] for i in housing), name="C2"
    )

    # Constraint 3: Only install as many heatpumps in a house category as the total quantity of houses of that type
    for i in housing:
        model.addConstr(
            quicksum(x[m, i, t, d] for m in heatpumps for t in range(T)
                     for d in distributors) <= housing[i]['quantity'], name="C3"
        )

    # Constraint 4: Only install up to the current expected sales volume
    for t in range(T):
        model.addConstr(quicksum(
            x[m, i, t, d] for i in housing for m in heatpumps for d in distributors) <= max_sales[t], name="C4")

    # Constraints 5: Respect the operation radius for each distributor
    # TODO: add the constraint 5 as explained above
    for d in distributors:
        for i in housing:
            dist = cal_dist((housing[i]['lat'], housing[i]['long']),
                            (distributors[d]['lat'], distributors[d]['long']))
            if dist > 2000:
                for m in heatpumps:
                    for t in range(T):
                        model.addConstr(x[m, i, t, d] == 0, name="C5")

    # Constraint 6: Respect max_installations capacity
    # TODO: implement the constraint "yearly workforce <= qty of heat pumps installed by the distributor"

    stop = timeit.default_timer()
    print("Time in seconds to add the constraints: ", stop - start, "\n")

    # Add Objective
    print("Adding objective function")
    start = timeit.default_timer()
    # TODO: add other objective function

    """
          We calculate and sum yearly operation costs for each house and add the costs for inital
          installations of heat pumps.
    """
    # TODO: find a better cost function : lifespan of boiler/heatpumps, total cost of ownership
    obj = quicksum((x[m, i, t, d] * heatpumps[m]['price']
                    + quicksum(x[m, i, t_1, d] * (ELECTRICITY_COST_PER_UNIT * electr_timefactor[t_1]
                                                  + CO2_EMISSION_EON * CO2_EMISSION_PRICE * CO2_timefactor[t_1])
                               * housing[i]['average heat demand'] / heatpumps[m]['cop'] for t_1 in range(t + 1))
                    + (housing[i]['quantity'] - quicksum(x[m, i, t_1, d]
                       for t_1 in range(t + 1)))
                    * (AVERAGE_BOILER_COST_PER_UNIT * gas_timefactor[t]
                       + CO2_EMISSION_GAS * CO2_EMISSION_PRICE * CO2_timefactor[t])
                    * housing[i]['average heat demand']) / BOILER_EFFICIENCY
                   for i in housing for m in heatpumps for d in distributors for t in range(T))
    model.setObjective(obj, GRB.MINIMIZE)

    stop = timeit.default_timer()
    print('Time in seconds to add the objective function: ', stop - start, "\n")
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
    write_solution_csv(model, districts, heatpumps, housing, T, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
                       CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
                       CO2_EMISSION_PRICE, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
                       electr_timefactor, gas_timefactor, CO2_timefactor)
    print('Time in seconds to solve the model: ', stop - start, "\n")

    return model

    """ For testing purposes, can be ignored
    print("Set threshold as",MIN_PERCENTAGE)
    k=0
    tot= sum(I[i]["quantity"] for i in I)
    for t in range(T):
        val= int(sum([model.getVarByName(f'hp_type_{str(m)}_at_house_type_{str(i)}_in_year_{str(t)}').X for m in M for i in I]))
        k=k+val

        print("t=%02d "%(t,),": build", val,"houses", "with maximum houses", tot)
    p=100*k/tot
    print(p,"% wurde erfüllt beim Threshold ",MIN_PERCENTAGE)    
   
    return
    """
