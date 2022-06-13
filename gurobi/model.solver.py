#!/usr/bin/env python3
# Template for our final model
from gurobipy import *
import numpy as np
from dataprp import data_preprocess
import timeit, json

# from https://www.haustechnikdialog.de/Forum/t/42992/Auslegung-Waermepumpe-auf-2200-Betriebsstunden-pro-Jahr-#:~:text=Hallo%2C-,ca.,die%20Betriebsdauer%20richtig%20hinzugenommen%20worden.
CONSTANT_HOURS_OF_HEATING_PER_YEAR = 2000
NUMBER_OF_MONTHS = 10  # number of months
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
    print("Preprocess the data")
    start = timeit.default_timer()
    D, M, I = data_preprocess()
    T = NUMBER_OF_MONTHS
    stop = timeit.default_timer()
    print('Time in seconds to prepare the data: ', stop - start)

    print("Prepare the parameters")
    start = timeit.default_timer()

    storage, heatdemand, boilercosts, hpcosts, hpinvestment, electr_timefactor, \
        gas_timefactor, electr_locationfactor, gas_locationfactor, CO2_timefactor, hpCO2 = prepare_params( T, I, M, D)

    stop = timeit.default_timer()
    print('Time in seconds to prepare the parameters ', stop - start)

    print("Preparing A and Fpow")
    start = timeit.default_timer()
    Fpow = dict()
    for i in I:
        for m in M:
            produced_heat = M[m]['produced heat']
            max_heat_demand = I[i]['max_heat_demand']
            if max_heat_demand <= produced_heat:
                # this means the heatpump matches our heat demand
                Fpow[(i, m)] = 1
            else:
                Fpow[(i, m)] = 0

    stop = timeit.default_timer()
    print('Time in seconds to prepare A and Fpow: ', stop - start)
    print("Preparing the model\n")
    # Create a new model
    model = Model("Heatpumps")
    print()
    print("Adding variables")
    start = timeit.default_timer()
    # Variables
    print()
    
    print(len(M))

    print("Adding variables for the heatpumps", len(
        M) * len(I) * T, "variables will be added")
    # Quantity of installed heat pumps with given conditions
    x = {}
    for m in M:
        for i in I:
            for t in range(T):
                # name = f"x: install hp_{str(m)} in house_{str(i)} in district_{str(s)} in month_{str(t)}"
                x[m, i, t] = model.addVar(
                    vtype=GRB.INTEGER,
                    name=f'x#install_hp_of_type_{str(m)}#at_house_type_{str(i)}#in_month_{str(t)}'
                )

    stop = timeit.default_timer()
    print('Time in seconds to add the variables: ', stop - start)

    print("Adding the constraints")
    start = timeit.default_timer()
    # Constraint 1:
    for i in I:
        for m in M:
            for t in range(T):
                if Fpow[(i, m)] == 0:
                    model.addConstr(x[m, i, t] == 0)

    # Constraint 3:
    for i in I:
        model.addConstr(
            quicksum(x[m, i, t] for m in M for t in range(T)) == I[i]['quantity']
        )

    # Constraint 4:
    for t in range(T):
        for m in M:
            model.addConstr(quicksum(x[m, i, t] for i in I) <= storage[m, t])

    # For every district in every month, the number of installed heatpump must be smaller or equal
    # the maximum capacity (workforce)
    # d is a string as key of dictionary!
    for d in D:
        workforce = D[d]
        for t in range(T):
            l = []
            for i in I:
                if I[i]['district'] == d:
                    for m in M:
                            l.append(x[m, i, t])

            model.addConstr(quicksum(l) <= workforce)

    # Constraint 8:
    model.addConstrs(
        x[m, i, t] >= 0 for m in M for i in I for t in range(T)
    )

    stop = timeit.default_timer()
    print('Time in seconds to adding constraints: ', stop - start)

    print("Adding objective function")
    start = timeit.default_timer()
    # Objective
    obj = quicksum( ( x[m, i, t] * hpinvestment[m]
                    + quicksum( x[m, i, t_1] * ( hpcosts[m] * electr_timefactor[t_1] * electr_locationfactor[d] 
                                                           + hpCO2[m] * CO2_EMISSION_PRICE_1 * CO2_timefactor[t_1])
                                               * heatdemand[i, t_1] for t_1 in range(t + 1) )
                    + (I[i]['quantity'] - quicksum(x[m, i,  t_1] for t_1 in range(t + 1)))
                                     * ( boilercosts[i] * gas_timefactor[t] * gas_locationfactor[d] 
                                                          + CO2_EMISSION_GAS / BOILER_EFFICIENCY * CO2_EMISSION_PRICE_1 * CO2_timefactor[t] )
                                     * heatdemand[i, t]) 
                    for m in M for i in I for d in D for t in range(T) )

    model.setObjective(obj, GRB.MINIMIZE)
    stop = timeit.default_timer()
    print('Time in seconds to add the objective function: ', stop - start)
    model.update()
    print("Solving the model")
    start = timeit.default_timer()
    model.write("model.lp")
    model.optimize()
    # model.computeIIS()
    stop = timeit.default_timer()
    write_solution(model, D, M, I)
    print('Time in seconds to solve the model: ', stop - start)
    return model


def prepare_params(T, I, M, D):
    """Prepares the parameters based on the data

    Args: 
        T (int): number of months startting from January
        M (dict) : dictionary of heat pumps, each containing the keys:
            'brand_name' (str) : brand name of the heat pump
            'cop' (float) : COP of the heat pump
            'produced heat' (float) : heat produced by the heat pump
        I (dict) : dictionary of buildings each containing the keys:
            "building_type" (str) : building type
            "modernization_status" (str) : status of the building (i.e. whether it is modernized or not)
            "max_heat_demand" (int)  : maximum heat demand of the building (in kWh/m^2)
            "district" (str) : district of the building
            "count" (int) : number of buildings of the same type in the district
    Returns:
        storage[t,m]: stock level of heat pumps
        heatdemand[i,t]: requested heat demand of a house type in a month
        boilercosts[i]: variable costs for gas boilers per unit of heat
        hpcosts[m]: variable costs for heat pumps per unit of heat
        hpinvestment[m]: fixed purchasing costs for heat pump

                            FOR LATER
        __________________________________________________________________________________________________________
        sub[m]: fixed subsidies for heat pump models
        availablepower[renewable,t]: usable power from renewables
    """
    # # from https://www.raponline.org/wp-content/uploads/2022/02/Heat-pump-running-costs-v271.pdf
    # AVERAGE_BOILER_COST_PER_UNIT = 0.07  # pounds per kWh

    # from https://www.globalpetrolprices.com/Germany/natural_gas_prices/
    AVERAGE_BOILER_COST_PER_UNIT = 0.071  #  euro per kWh for private household

    storage = np.empty(shape=(len(M), T))
    heatdemand = np.empty(shape=(len(I), T))
    boilercosts = np.empty(shape=(len(I)))
    hpcosts = np.empty(shape=(len(M)))
    hpinvestment = np.empty(shape=(len(M)))
    # workforce = np.empty(shape=(len(D), T))
    electr_timefactor =  np.empty(T)
    gas_timefactor = np.empty(T)
    electr_locationfactor = {}
    gas_locationfactor = {}
    CO2_timefactor = np.empty(T)
    hpCO2 = np.empty(shape=(len(M)))
    # sub = np.empty(shape=(len(M)))
    # availablepower = np.empty(shape=(len(renawable), T))

    for t in range(T):
        for m in M:
            storage[m, t] = 100000

    for i in I:
        for t in range(T):
            heatdemand[i, t] = I[i]['max_heat_demand']



    for i in I:
            # boiler assumed to have the energy efficiency of 70%
            boilercosts[i] = AVERAGE_BOILER_COST_PER_UNIT / BOILER_EFFICIENCY

    # for m in M:
    #     for s in S:
    #         hpcosts[m, s] = M[m]['produced heat'] / M[m]['cop']
    #     hpinvestment[m] = 1000
    
     # electricity price taken from: https://www.eon.de/de/pk/strom/stromanbieter/guenstiger-stromanbieter.html
     # consider the price based on the tarif without minimum contract duration requirement
    ELECTRICITY_COST_PER_UNIT = 0.4805

    for m in M:
            # hpcost is multiplied with heatdemand in obj function, so it should be cost/kwh. 
            # we consider it now as the constant elctricity price of one dimension, since acoording to EON this price can be guaranteed till 2024. 
            # Price can be made to dependent on time ( added tax might be increased) and districts by adapting the vector timefactor and locationfactor.
            hpcosts[m] = ELECTRICITY_COST_PER_UNIT / M[m]['cop']
            hpinvestment[m] = M[m]['price']
    
    # there is a base cost per year to sign EON contract
    hpcosts = 134.36/12 + hpcosts        
        
    # price of those terms are currently asummed to be constant over time
    electr_timefactor = np.ones(T)
    gas_timefactor = np.ones(T)
    CO2_timefactor = np.ones(T)

    # price of those terms are currently assumed to be the same over differenct districts
    # d is a string as key of dictionary!
    for d in D:
        electr_locationfactor[d] = 1  
        gas_locationfactor[d] = 1

    

    # heatpump co2 emission based on electricity supplied by EON
    for  m in M:
        hpCO2[m] = CO2_EMISSION_EON / M[m]['cop']
       
    
   
    return storage, heatdemand, boilercosts, hpcosts,  hpinvestment,  \
             electr_timefactor, gas_timefactor, electr_locationfactor, gas_locationfactor, CO2_timefactor, hpCO2


def write_solution(model, D, M, I):
    with open('optimization_result.txt', 'w') as f:
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

solve()
