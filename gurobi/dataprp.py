import pandas as pd
from gurobipy import *
import timeit
import numpy as np
import re
import modelsolver


dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, './data-sources/data_from_Hannah_with_coordinates_zipcodes_heatcapacity_positive_building_count.csv')
DISTRIBUTOR = os.path.join(dirname, './data-sources/Distributor_data_with_coordinates.csv')
HEAT_PUMPS = os.path.join(dirname, './data-sources/heat_pumps_air_water_price.csv')
FPOWDATA = os.path.join(dirname, './data-sources/fpow.csv')
PARAMETERS = os.path.join(dirname, './data-sources/parameters.xlsx')

# function calls and combines all other function except for prepare_params
def data_preprocess():
    print("Prepare the data")
    start = timeit.default_timer()

    housing_dataframe = pd.read_csv(ACOOLHEAD)
    heatpump_dataframe = pd.read_csv(HEAT_PUMPS)
    distributors_dataframe = pd.read_csv(DISTRIBUTOR)

    housing_data = prepare_housing_data(
        housing_dataframe, max_entries=None, zipcodes_of_interest="^(5[0-3])"
    )
    districts = get_districts(housing_dataframe)
    heatpump_data = prepare_heatpump_data(heatpump_dataframe, max_entries=4)
    distributor_data = prepare_distributor(
        distributors_dataframe, zipcodes_of_interest="^(5[0-3])", max_entries=10
    )
    # fitness_data = prepare_fitness()
    fitness_data = prepare_fitness_on_run_time(heatpump_data, housing_data)

    stop = timeit.default_timer()
    print('Time to prepare the data: ', round(stop - start, 2), "s\n")

    return districts, heatpump_data, housing_data, fitness_data, distributor_data


def prepare_fitness_on_run_time(M, I):
    res = {}
    for i in I:
        for m in M:
            produced_heat = M[m]['produced heat']
            max_heat_demand = I[i]['max_heat_demand_Patrick']

            if max_heat_demand <= produced_heat:
                # this means the heatpump matches our heat demand
                res[(i, m)] = 1
            else:
                res[(i, m)] = 0
    return res


def prepare_housing_data(df, RADIUS_OF_INTEREST=None, max_entries=None, zipcodes_of_interest=None):
    housing_data = {i:
        {
            "district": df["Administrative district"][i],
            "type of building": df["Type of building"][i],
            "quantity": int(round(df["Number of buildings"][i], 0)),
            "Surface area": int(df["Surface area [m^2]"][i]),
            "modernization status": df["modernization status"][i],
            "max heat demand [kWh/m^2]": df["max heat demand [kWh/m^2]"][i],
            "average heat demand": df["average heat demand [kWh/m^2]"][i],
            "Heatcapacity": df["Heatcapacity"][i],
            "Klimazone": df["Klimazone"][i],
            "year of construction": df["Year of construction"][i],
            "max_heat_demand_Patrick": round(int(df["Surface area [m^2]"][i]) * df["Heatcapacity"][i] / 1000, 2),
            'long': df['long'][i],
            'lat': df['lat'][i]
            # "Floors": df["Floors"][i]
        }
        for i in range(len(df["long"]))
        if len(str(df["zipcode"][i])) == 5 and re.match(zipcodes_of_interest, str(df["zipcode"][i]))
    }

    if max_entries is None:
        return {i: list(housing_data.values())[i] for i in range(
            len(housing_data.values()))}
    else:
        return {i: list(housing_data.values())[i] for i in range(
            len(housing_data.values())) if i < max_entries}


def prepare_heatpump_data(df_hp, max_entries=None):
    df_hp = df_hp.sort_values(by=['Heat output A2/W35 (kW)'], ascending=False)
    heatpump_data = {i:
        {
            'brand_name': df_hp['hp_name'][i],
            'cop': df_hp['COP A2/W35'][i],
            'produced heat': df_hp['Heat output A2/W35 (kW)'][i],
            'price': df_hp['price'][i]
        }
        for i in range(len(df_hp['hp_name']))}
    if max_entries is not None:
        return {i: list(heatpump_data.values())[i] for i in range(
            len(heatpump_data.values())) if i < max_entries}
    return heatpump_data


def get_districts(df):
    return df['Administrative district'].unique()


def prepare_distributor(df, RADIUS_OF_INTEREST=20, zipcodes_of_interest=None, max_entries=None):
    distributors = {
        i: {
            'name': df['Distributors'][i],
            'long': df['long'][i],
            'lat': df['lat'][i]
        }
        for i in range(len(df))
        if len(str(df["zipcode"][i])) == 5 and re.match(zipcodes_of_interest, str(df["zipcode"][i]))
    }
    if max_entries is None:
        return distributors
    else:
        return {i: list(distributors.values())[i] for i in range(
            len(distributors.values())) if i < max_entries}


def prepare_params():

    # read parameter input file
    paras = pd.read_excel(PARAMETERS, engine='openpyxl', sheet_name=['basic_costs', 'constant_values', 'location_factors', 'time_factors', 'subsidies'])
    paras_const, paras_costs, paras_time, paras_location, paras_subsidies = paras['constant_values'], paras['basic_costs'], paras['time_factors'], paras['location_factors'], paras['subsidies']

    # get constant parameters
    NUMBER_OF_YEARS = paras_const['time horizon in years'][0]
    MIN_PERCENTAGE = paras_const['percentage of housing receiving a hp'][0]
    CO2_EMISSION_GAS = paras_const['CO2 emission (petrol) in g/kWh'][0]
    CO2_EMISSION_EON = paras_const['CO2 emission (eon) in g/kWh'][0]
    BOILER_EFFICIENCY = paras_const['boiler efficiency index'][0]
    CO2_EMISSION_PRICE_GAS = paras_costs['CO2 emission price (petrol) in €/g'][0]
    CO2_EMISSION_PRICE_EON = paras_costs['CO2 emission price (eon) in €/g'][0]
    AVERAGE_BOILER_COST_PER_UNIT = paras_costs['petrol costs in €/kWh'][0]
    ELECTRICITY_COST_PER_UNIT = paras_costs['electricity costs in €/kWh'][0]

    # get non-constant parameters
    electr_timefactor, gas_timefactor, CO2_timefactor, max_sales = ((np.empty(shape=len(paras_time["year"]))) for i in range(4))
    for t in range(len(paras_time["year"])):
        electr_timefactor[t] = (paras_time['electricity time factor'][t])
        gas_timefactor[t] = (paras_time['petrol time factor'][t])
        CO2_timefactor[t] = (paras_time['CO2 time factor'][t])
        max_sales[t] = (paras_time['maximum hp stock'][t])

    return NUMBER_OF_YEARS, MIN_PERCENTAGE, CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY, CO2_EMISSION_PRICE_GAS, CO2_EMISSION_PRICE_EON,\
           max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT, electr_timefactor, gas_timefactor, CO2_timefactor

# get prepared data
(districts, heatpumps, housing, fitness, distributors) = data_preprocess()

# get prepared parameters
(NUMBER_OF_YEARS, MIN_PERCENTAGE, CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY, CO2_EMISSION_PRICE_GAS,
     CO2_EMISSION_PRICE_EON, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT, electr_timefactor,
     gas_timefactor, CO2_timefactor) = prepare_params()

# solve model
modelsolver.solve(districts, heatpumps, housing, fitness, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
          CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY, CO2_EMISSION_PRICE_GAS,
          CO2_EMISSION_PRICE_EON, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
          electr_timefactor, gas_timefactor, CO2_timefactor)