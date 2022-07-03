import pandas as pd
from gurobipy import tuplelist
import timeit
import re
import os
from utilities import cal_dist
import numpy as np


dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(
    dirname, './data-sources/HOUSING.csv')
DISTRIBUTOR = os.path.join(dirname, './data-sources/Distributor_data.csv')
HEAT_PUMPS = os.path.join(
    dirname, './data-sources/heat_pumps_air_water_price.csv')
FPOWDATA = os.path.join(dirname, './data-sources/fpow.csv')
PARAMETERS = os.path.join(dirname, './data-sources/parameters.xlsx')


# function calls and combines all other function except for prepare_params
def data_preprocess(T, operating_radius):
    print("Prepare the data")
    start = timeit.default_timer()

    housing_dataframe = pd.read_csv(ACOOLHEAD)
    heatpump_dataframe = pd.read_csv(HEAT_PUMPS)
    distributors_dataframe = pd.read_csv(DISTRIBUTOR)

    housing_data = prepare_housing_data(
        housing_dataframe, max_entries=None,
    )
    districts = get_districts(housing_dataframe)
    heatpump_data = prepare_heatpump_data(heatpump_dataframe, max_entries=4)
    distributor_data = prepare_distributor(
        distributors_dataframe,  max_entries=None
    )

    fitness_data = prepare_fitness_on_run_time(heatpump_data, housing_data)

    stop = timeit.default_timer()
    print('Time to prepare the data: ', round(stop - start, 2), "s\n")

    configurations = get_configurations(
        heatpump_data, housing_data, distributor_data, T, operating_radius)

    return districts, heatpump_data, housing_data, fitness_data, distributor_data, configurations


def prepare_fitness_on_run_time(M, I):
    fitness = {}
    for i in I:
        for m in M:
            produced_heat = M[m]['produced heat']
            max_heat_demand = I[i]['max_heat_demand_W/m^2']

            if max_heat_demand <= produced_heat:
                # this means the heatpump matches our heat demand
                fitness[(i, m)] = 1
            else:
                fitness[(i, m)] = 0
    return fitness


def prepare_housing_data(df,  max_entries=None, zipcodes_of_interest=None):
    housing_data = {i:
                    {
                        "district": df["Administrative district"][i],
                        "type of building": df["Type of building"][i],
                        "quantity": int(round(df["Number of buildings"][i], 0)),
                        "Surface area": int(df["Surface area [m^2]"][i]),
                        "modernization status": df["modernization status"][i],
                        "max heat demand [kWh/m^2]": df["max heat demand [kWh/m^2]"][i],
                        "average heat demand": df["average heat demand [kWh/m^2]"][i]*int(df["Surface area [m^2]"][i]),
                        "Heatcapacity": df["Heatcapacity"][i],
                        "year of construction": df["Year of construction"][i],
                        "max_heat_demand_W/m^2": round(int(df["Surface area [m^2]"][i]) * df["Heatcapacity"][i] / 1000, 2),
                        'long': df['long'][i],
                        'lat': df['lat'][i],
                        'zipcode': df['zipcode'][i]
                    }
                    for i in range(len(df["long"]))
                    if len(str(df["zipcode"][i])) == 5 and (zipcodes_of_interest == None or re.match(zipcodes_of_interest, str(df["zipcode"][i])))
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
    df['operating districts'] = df['operating districts'].astype(
        str)
    distributors = {
        i: {
            'name': df['Distributors'][i],
            'long': df['long'][i],
            'lat':  df['lat'][i],
            'op_r': df['operating radius'][i],
            'max_installations': df['max_installations'][i],
            'operating radius': df['operating radius'][i],
            'operating districts': df['operating districts'][i],
        }
        for i in range(len(df))
        if len(str(df["zipcode"][i])) == 5 and (zipcodes_of_interest == None or re.match(zipcodes_of_interest, str(df["zipcode"][i])))
    }
    if max_entries is None:
        return distributors
    else:
        return {i: list(distributors.values())[i] for i in range(
            len(distributors.values())) if i < max_entries}


def get_configurations(heatpumps, housing, distributors, T, operating_radius):
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
    configurations = tuplelist()
    for m in heatpumps:
        for i in housing:
            produced_heat = heatpumps[m]['produced heat']
            max_heat_demand = housing[i]['max_heat_demand_W/m^2']
            if produced_heat >= max_heat_demand:
                zipcode = housing[i]['zipcode']
                for d in distributors:
                    if distributor_serves_zipcode(distributors[d], zipcode):
                        for t in range(-1, T):
                            configurations.append((m, i, d, t))
    initial_count = len(heatpumps) * len(housing) * len(distributors) * T
    print("Variable set reduced to", round(
        len(configurations) / initial_count * 100, 3), "%\n")

    return configurations


def distributor_serves_zipcode(distributor, zipcode):
    """Determines whether a particular distributor serves a particular district.
       german wide suppliers supply all districts. They are identified by an operating radius of None 
       distributors with an operating radius serve the district if that one is in its operating districts
    Args:
        distributor (dict)
        zipcode (str)
    Returns:
        bool 
    """
    return np.isnan(distributor['operating radius']) or zipcode in distributor['operating districts']
