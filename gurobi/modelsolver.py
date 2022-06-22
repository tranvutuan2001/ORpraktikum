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
          electr_timefactor, gas_timefactor, CO2_timefactor, operating_radius=2000):
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

    # Determine possible configurations
    print("Determining possible configurations\n")
    start = timeit.default_timer()

    # list of all possible configurations
    configurations = get_configurations(
        heatpumps, housing, distributors, T, operating_radius)
    print(f"{len(configurations)} possible configurations")
    heatpump_index = list(dict.fromkeys(
        configuration[0] for configuration in configurations))  # an index of all possbile heat pumps
    housing_index = list(dict.fromkeys(
        configuration[1] for configuration in configurations))  # an index of all possible housings
    distributor_index = list(dict.fromkeys(
        configuration[2] for configuration in configurations))  # an index of all possible distributors
    # currently no filtering done but maybe later there could be a time filter
    # time_index = list(dict.fromkeys(configuration[3] for configuration in configurations)) # an index of all possible times

    stop = timeit.default_timer()
    print('Time to determine configurations: ',
          f"{round(stop - start, 2)} seconds\n")

    # Add Variables
    print("Adding variables")
    start = timeit.default_timer()
    print(len(configurations), "variables will be added")
    # Quantity of installed heat pumps with given conditions
    x = {}
    # TODO: only add the variables for house/heatpump combinations that are feasible, do not add variables if fitness=0
    for m in heatpump_index:
        for i in housing_index:
            for t in range(T):
                for d in distributor_index:
                    x[m, i, t, d] = model.addVar(vtype='I',
                                                 name=f'hp_type_{str(m)}_at_house_type_{str(i)}_in_year_{str(t)}_by_distributor_{str(distributors[d]["name"])}'
                                                 )
    stop = timeit.default_timer()
    print('Time to add the variables: ', f"{round(stop - start, 2)} seconds\n")

    print("Adding the constraints")
    start = timeit.default_timer()

    # Constraint 2:  Install heat pumps in AT LEAST the specified percentage of all houses
    house_count = sum(housing[i]['quantity'] for i in housing_index)
    model.addConstr(
        quicksum(x[m, i, t, d] for m in heatpump_index for i in housing_index for t in range(
            T) for d in distributor_index) >= MIN_PERCENTAGE * house_count, name="C2"
    )

    # Constraint 3: Only install as many heatpumps in a house category as the total quantity of houses of that type

    model.addConstrs(
        (quicksum(x[m, i, t, d] for m in heatpump_index for t in range(T)
                  for d in distributor_index) <= housing[i]['quantity'] for i in housing_index), name="C3"
    )

    # Constraint 4: Only install up to the current expected sales volume
    model.addConstrs((quicksum(
        x[m, i, t, d] for i in housing_index for m in heatpump_index for d in distributor_index) <= max_sales[t] for t in range(T)), name="C4")

    # Constraints 5: Respect the operation radius for each distributor
    # not needed since we already have this in get configurations

    # Constraint 6: Respect max_installations capacity
    # TODO: implement the constraint "yearly workforce <= qty of heat pumps installed by the distributor"

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
    # TODO: find a better cost function : lifespan of boiler/heatpumps, total cost of ownership
    obj = quicksum((
        x[m, i, t, d] * heatpumps[m]['price']

        + quicksum(x[m, i, t_1, d] * (ELECTRICITY_COST_PER_UNIT * electr_timefactor[t_1]
                                      + CO2_EMISSION_EON * CO2_EMISSION_PRICE * CO2_timefactor[t_1])
                   * housing[i]['average heat demand'] / heatpumps[m]['cop'] for t_1 in range(t + 1))

        + (housing[i]['quantity'] - quicksum(x[m, i, t_1, d]
                                             for t_1 in range(t + 1)))
        * (AVERAGE_BOILER_COST_PER_UNIT * gas_timefactor[t] + CO2_EMISSION_GAS * CO2_EMISSION_PRICE * CO2_timefactor[t])
        * housing[i]['average heat demand'] / BOILER_EFFICIENCY)
        for i in housing_index for m in heatpump_index for d in distributor_index for t in range(T))
    model.setObjective(obj, GRB.MINIMIZE)

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
    write_solution_csv(model, districts, heatpumps, housing, T, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
                       CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
                       CO2_EMISSION_PRICE, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
                       electr_timefactor, gas_timefactor, CO2_timefactor)
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


def get_configurations(heatpumps, housing, distributors, T, operating_radius=2000):
    """Generate the possible configurations for the model.
       A configuration is possible only if the heatpump can fulfill the demand of the house and the house is in the operating radius of the distributor.

    Args:
        heatpumps (dict)
        housing (dict)
        distributors (dict)
        T (dict)
        operating_radius (int, optional). Defaults to 2000.

    Returns:
        _type_: _description_
    """
    configurations = []
    for m in heatpumps:
        for i in housing:
            produced_heat = heatpumps[m]['produced heat']
            max_heat_demand = housing[i]['max_heat_demand_W/m^2']
            if produced_heat >= max_heat_demand:
                for d in distributors:
                    dist = cal_dist((housing[i]['lat'], housing[i]['long']),
                                    (distributors[d]['lat'], distributors[d]['long']))
                    if dist <= operating_radius:
                        for t in range(T):
                            configurations.append((m, i, d, t))
    initial_count = len(heatpumps) * len(housing) * len(distributors) * T
    print("Variable set reduced to", round(
        len(configurations)/initial_count * 100, 3), "%\n")
    return configurations
