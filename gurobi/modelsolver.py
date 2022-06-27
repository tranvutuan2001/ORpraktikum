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
          electr_timefactor, gas_timefactor, CO2_timefactor, configurations):
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

    P = configurations
    index_heatpump = set(k[0] for k in P)
    index_housing = set(k[1] for k in P)
    print("index_housing",index_housing)
    index_distributor = set(k[2] for k in P)
    index_time = set(k[3] for k in P)
    # Add Variables
    print("Adding variables")
    start = timeit.default_timer()
    print(len(P), "variables will be added")
    # Quantity of installed heat pumps with given conditions
    x = {}
    for p in P:
        if p[3] >= 0:
            
            x[p] = model.addVar(vtype='I', lb=0,
                                         name=f'hp_type_{str(p[0])}_at_house_type_{str(p[1])}_by_distributor_{str(distributors[p[2]]["name"])}_in_year_{str(p[3])}')
        else: x[p] = 0

    stop = timeit.default_timer()
    print('Time to add the variables: ', f"{round(stop - start, 2)} seconds\n")

    print("Adding the constraints")
    start = timeit.default_timer()

    # Constraint 1: Consider Installability : never assign Heat Pump to a housetype if they do not fit to the house type
    # removed because this is handled by get_configurations

    # Constraint 2:  Install heat pumps in AT LEAST the specified percentage of all houses
    house_count = sum(housing[i]['quantity'] for i in housing)
    
    model.addConstr(
        quicksum(x[p] for p in P.select('*', '*', '*', T-1)) >= MIN_PERCENTAGE * house_count, name="C2"
    )
    print("T-1=",T-1)
    # Constraint 3: Only install as many heatpumps in a house category as the total quantity of houses of that type


    for i in index_housing:
        model.addConstr(quicksum(x[p] for p in P.select("*", i, "*", T-1)) <= housing[i]['quantity'], name="C3")
        #print("for i=",i,"=",P.select("*",i,"*",T-1))

    # Constraint 4: Only install up to the current expected sales volume
    for t in range(T):
        model.addConstr(quicksum(x[p] - x[(p[0],p[1],p[2],p[3]-1)] for p in P.select("*", "*", "*", t)) <= max_sales[t], name="C4")

    # Constraints 5: Respect the operation radius for each distributor
    # removed because this is handled by get_configurations

    # Constraint 6: Respect max_installations capacity
    # TODO: implement the constraint "yearly workforce <= qty of heat pumps installed by the distributor"

    # Constraint 7: x[p] is a cumulative value
    for t in range(T):
        for p in P.select("*","*","*",t):
                #print(p,"und",p[0],p[1],p[2],p[3]-1)
                model.addConstr(x[p]-x[(p[0],p[1],p[2],p[3]-1)] >= 0, name="C7")

    stop = timeit.default_timer()
    print("Time to add the constraints: ",
          f"{round(stop - start, 2)} seconds\n")

    # Add Objective
    print("Adding objective function")
    start = timeit.default_timer()
    # TODO: add other objective function

    """
          We calculate and sum yearly operation costs for each house and add the costs for inital
          installations of heat pumps.
    """
    # TODO: find a better cost function : lifespan of boiler/heatpumps, total cost of ownership/
    investcost= quicksum((x[p]-x[(p[0],p[1],p[2],p[3]-1)])* heatpumps[p[0]]['price'] for p in P if p[3]>=0)
    hpcost= quicksum(x[p] * ((ELECTRICITY_COST_PER_UNIT * electr_timefactor[p[3]]+ CO2_EMISSION_EON * CO2_EMISSION_PRICE * CO2_timefactor[p[3]])/heatpumps[p[0]]['cop']) for p in P if p[3]>=0)   
    gascost= quicksum((house_count-x[p])*((AVERAGE_BOILER_COST_PER_UNIT * gas_timefactor[p[3]]+ CO2_EMISSION_GAS * CO2_EMISSION_PRICE * CO2_timefactor[p[3]])/ BOILER_EFFICIENCY) for p in P if p[3]>=0)  


                   
    obj = investcost+(hpcost+gascost) * housing[p[1]]['average heat demand']
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


