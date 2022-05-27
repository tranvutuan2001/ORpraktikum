#!/usr/bin/env python3
# Template for our final model
from gurobipy import *
import numpy as np
from dataprp import data_preprocess
import timeit
# from https://www.haustechnikdialog.de/Forum/t/42992/Auslegung-Waermepumpe-auf-2200-Betriebsstunden-pro-Jahr-#:~:text=Hallo%2C-,ca.,die%20Betriebsdauer%20richtig%20hinzugenommen%20worden.
CONSTANT_HOURS_OF_HEATING_PER_YEAR = 2000
NUMBER_OF_MONTHS = 12  # number of months


def solve(T=NUMBER_OF_MONTHS, S=None, I=None, M=None, D=None):
    """Solves the heat pump problem.

    Args: 
        T (int): number of months startting from January
        S (set): set of districts and workforce in that district
        I (dict): clusters of house types. 
            - 'buidling_type': type of building EFH, 
            - 'surface_area': the surface area 
            - 'modernazation_status': the modernization status of the building
            - 'max_heat_demand': the amount of heat this building requires TODO: make sure if this is for a year
            - 'district': the district in which the building is located
            - 'count': the number of houses in a particular cluster
        M (dict) set of heatpumps from https://www.topten.eu/private/products/heat_pumps
            - 'cop': cop of the heat pump
            - 'produced heat': the amount of heat it can produce TODO: find out what this means probably per hour

                            FOR LATER
        __________________________________________________________________________________________________________

        # D (dict) set of installation providers . 
        #     - 'location': the location of the installation provider
        #     - 'operating_radius': the radius in which the installation provider operates
        #     - 'total_workforce': the work force of the installation provider
        #     TODO find sources for this. Is this even possible??

    """
    print("Preprocess the data")
    start = timeit.default_timer()
    D_S, M, I = data_preprocess()
    D = {i: D_S[i]['workforce'] for i in D_S.keys()}
    S = {i: D_S[i]['district'] for i in D_S.keys()}
    stop = timeit.default_timer()
    print('Time in seconds to prepare the data: ', stop - start)

    print("Prepare the parameters")
    start = timeit.default_timer()
    storage, totalhouses, heatdemand, boilercosts, hpcosts, hpinvestment, workforce = prepare_params(
        T, S, I, M, D)
    stop = timeit.default_timer()
    print('Time in seconds to prepare the parameters ', stop - start)

    print("Preparing A and Fpow")
    start = timeit.default_timer()
    Fpow = dict()
    for i in I:
        for m in M:
            produced_heat = M[m]['produced heat']
            max_heat_demand = I[i]['max_heat_demand']
            if max_heat_demand / produced_heat >= CONSTANT_HOURS_OF_HEATING_PER_YEAR:
                # this means the heatpump matches our heat demand
                Fpow[(i, m)] = 1
            else:
                Fpow[(i, m)] = 0
    A = dict()
    for d in D:
        for s in S:
            if s == d:
                A[(d, s)] = 1
            else:
                A[(d, s)] = 0
    stop = timeit.default_timer()
    print('Time in seconds to prepare A and Fpow: ', stop - start)
    print("Preparing the model\n")
    # Create a new model
    model = Model("Heatpumps")
    print()
    print("Adding variables")
    start = timeit.default_timer()
    # Variables
    # Quantity of installed heat pumps with given conditions
    print("Adding variables for the heatpumps", len(
        M)*len(I)*len(S)*T, "variables will be added")
    x = {}
    for m in M:
        for i in I:
            for s in S:
                for t in range(T):
                    x[m, i, s, t] = model.addVar(
                        vtype=GRB.INTEGER, name="x# hp " + str(m) + "of house " + str(i) + "in" + str(s) + "until" + str(t))
    # Quantity of installed heat pumps by distributor d (at moment 'd' is assumed to be the same as 's')
    print("Adding variables for the heatpumps by distributor", len(S)*len(D)*T, "variables will be added")
    w = {}
    for s in S:
        for t in range(T):
            for d in D:
                w[s, t, d] = model.addVar(
                    vtype=GRB.INTEGER, name="w# distributor" + str(d) + "in" + str(s) + "until" + str(t))
    stop = timeit.default_timer()
    print('Time in seconds to add the variables: ', stop - start)
    
    print("Adding the constraints")
    start = timeit.default_timer()
    # Constraint 1:
    for i in I:
        for m in M:
            for s in S:
                model.addConstr( 
                    quicksum(x[m, i, s, t] <= totalhouses[i, s]*Fpow[(i, m)] for t in range(T)))
    # Constraint 2:
    for i in I:
        for s in S:
            for t in range(T):
                model.addConstr(quicksum(x[m, i, s, t] for m in M) <= totalhouses[i, s]-quicksum(
                    x[m, i, s, ti] for m in M for ti in range(0, t)))
    # Constraint 3:
    for i in I:
        for s in S:
            model.addConstr(
                quicksum(x[m, i, s, t] for m in M for t in range(T)) == totalhouses[i, s])

    # Constraint 4:
    for t in range(T):
        for m in M:
            model.addConstr(quicksum(x[m, i, s, t]
                            for i in I for s in S) <= storage[m, t])
    # Constraint 5:
    for s in S:
        for d in D:
            model.addConstr(
                quicksum(w[d, s, t] <= A[d, s] * quicksum(totalhouses[i, s] for i in I)))
    # Constraint 6:
    for s in S:
        for t in range(T):
            model.addConstr(quicksum(w[d, s, t] for d in D) <= quicksum(
                x[m, i, s, t] for m in M for i in I))
    # Constraint 7:
    for d in D:
        for t in range(T):
            model.addConstr(quicksum(w[d, s, t]
                            for s in S if A[d, s] == 1) <= workforce[d, t])
    # Constraint 8:
    model.addConstrs(
        x[m, i, s, t] >= 0 for m in M for i in I for s in S for t in range(T))
    # Constraint 9:
    model.addConstrs(w[d, s, t] >= 0 for d in D for s in S for t in range(T))
    stop = timeit.default_timer()
    print('Time in seconds to prepare A and Fpow: ', stop - start)

    print("Adding objective function")
    start = timeit.default_timer()
    # Objective
    obj = quicksum(x[m, i, s, t]*hpinvestment[m] + quicksum(x[m, i, s, t_1] * hpcosts[s, m]*heatdemand[i, t_1] for t_1 in range(t+1)) +
                   (totalhouses[i, s] - quicksum(x[m, i, s, t_1]
                                                 for t_1 in range(t+1))) * boilercosts[i, s] * heatdemand[i, t]
                   for m in M for i in I for s in S for t in range(T))
    model.setObjective(obj, GRB.MINIMIZE)
    stop = timeit.default_timer()
    print('Time in seconds to add the objective function: ', stop - start)
    model.update()
    print("Solving the model")
    start = timeit.default_timer()
    model.optimize()
    stop = timeit.default_timer()
    print('Time in seconds to solve the model: ', stop - start)
    return model


def prepare_params(T, S, I, M, D):
    """Prepares the parameters based on the data

    Args: 
        T (int): number of months startting from January
        S (set): set of districts and workforce in that district
        I (dict): clusters of house types. each entry is a representative of the cluster (take average values or median or majority). 
            Each entry has the following attributes:
            - 'buidling_type': type of building EFH, 
            - 'surface_area': the surface area 
            - 'modernazation_status': the modernization status of the building
            - 'max_heat_demand': the amount of heat this building requires TODO: make sure if this is for a year
            - 'district': the district in which the building is located
            - 'count': the number of houses in a particular cluster
        M (dict) set of heatpumps from https://www.topten.eu/private/products/heat_pumps
            - 'cop': cop of the heat pump
            - 'produced heat': the amount of heat it can produce TODO: find out what this, means probably per hour
            - 'investment': the investment cost of the heat pump
        B (dict) set of boilers. Each entry is a representative of the cluster (take average values or median or majority).
            Each entry has the following attributes:
                - 'name': the name of the boiler
                - 'cost': the costs per unit of heat

                            FOR LATER
        __________________________________________________________________________________________________________

        # D (dict) set of installation providers . 
        #     - 'location': the location of the installation provider
        #     - 'operating_radius': the radius in which the installation provider operates
        #     - 'total_workforce': the work force of the installation provider
        #     TODO find sources for this. Is this even possible??
    Returns:
        storage[t,m]: stock level of heat pumps
        totalhouses[i,s]: total count of similar houses in a district
        heatdemand[i,t]: requested heat demand of a house type in a month
        boilercosts[b,s]: variable costs for gas boilers per unit of heat
        hpcosts[m,s]: variable costs for heat pumps per unit of heat
        hpinvestment[m,s]: fixed purchasing costs for heat pump
        workforce[d,t]: workforce capacities of distributors per month

                            FOR LATER
        __________________________________________________________________________________________________________
        sub[m]: fixed subsidies for heat pump models
        availablepower[renewable,t]: usable power from renewables
    """
    # from https://www.raponline.org/wp-content/uploads/2022/02/Heat-pump-running-costs-v271.pdf
    AVERAGE_BOILER_COST_PER_UNIT = 0.07  # pounds per kWh

    storage = np.empty(shape=(T, len(M)))
    totalhouses = np.empty(shape=(len(I), len(S)))
    heatdemand = np.empty(shape=(len(I), T))
    boilercosts = np.empty(shape=(len(S)))
    hpcosts = np.empty(shape=(len(M), len(S)))
    hpinvestment = np.empty(shape=(len(M), len(S)))
    workforce = np.empty(shape=(len(D), T))
    # sub = np.empty(shape=(len(M)))
    # availablepower = np.empty(shape=(len(renawable), T))
    for t in range(T):
        for m in M:
            storage[t, m] = 1000

    for i in I:
        for s in S:
            totalhouses[i, s] = I[i]['count']
        for t in range(T):
            heatdemand[i, t] = I[i]['max_heat_demand'] * I[i]["surface_area"]

    for s in S:
        boilercosts[s] = AVERAGE_BOILER_COST_PER_UNIT

    for m in M:
        for s in S:
            hpcosts[m, s] = M[m]['produced heat'] / M[m]['cop']
            hpinvestment[m, s] = 1000

    for d in D:
        for t in range(T):
            workforce[d, t] = D[d]

    return storage, totalhouses, heatdemand, boilercosts, hpcosts, hpinvestment, workforce


solve()
