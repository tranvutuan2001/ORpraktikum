import pandas as pd
from gurobipy import *
import csv
import timeit
import numpy as np
import re
import os

dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(
    dirname, './data-sources/data_from_Hannah_with_coordinates_zipcodes_heatcapacity_positive_building_count.csv')
DISTRIBUTOR = os.path.join(
    dirname, './data-sources/Distributor_data_with_coordinates.csv')
HEAT_PUMPS = os.path.join(
    dirname, './data-sources/heat_pumps_air_water_price.csv')
FPOWDATA = os.path.join(dirname, './data-sources/fpow.csv')
#FOR THE TIME FACTORS @joern
SCENARIOS = os.path.join(
    dirname, './data-sources/scenarios.csv')

# from https://www.globalpetrolprices.com/Germany/natural_gas_prices/
AVERAGE_BOILER_COST_PER_UNIT = 0.13#0.071  # euro per kWh for private household
# AVERAGE_BOILER_COST_PER_UNIT = 0.17
BOILER_EFFICIENCY = 0.7
# electricity price taken from: https://www.eon.de/de/pk/strom/stromanbieter/guenstiger-stromanbieter.html
# consider the price based on the tarif without minimum contract duration requirement
ELECTRICITY_COST_PER_UNIT = 0.4805
# from https://www.eon.de/de/gk/strom/oekostrom.html#:~:text=Im%20Jahr%201990%20lag%20der,der%20CO%202%2DEmissionen%20leisten.
CO2_EMISSION_EON = 366  # gramm/kwh in 2020


def load_data_and_parameters(T):
    data = data_preprocess()
    districts, heatpumps, housing, _, _ = data

    parameters = prepare_params(
        T, housing, heatpumps, districts)

    return data, parameters


def data_preprocess():
    """    
    This function preprocesses the data from the excel and csv file and returns S,M,I, fitness
    Returns:
        D (dict) : dictionary of district names and workfoce in that district
        M (dict) : dictionary of heat pumps, each containing the keys:
            'brand_name' (str) : brand name of the heat pump
            'cop' (float) : COP of the heat pump
            'produced heat' (float) : heat produced by the heat pump
        I (dict) : dictionary of buildings each containing the keys:
            'building_type' (str) : building type
            'modernization_status' (str) : status of the building (i.e. whether it is modernized or not)
            'max_heat_demand' (int)  : maximum heat demand of the building (in kWh/m^2)
            'district' (str) : district of the building
            'count' (int) : number of buildings of the same type in the district
        fitness (dict): contains info if a heat pump model m can satisfy the demand of a house type i (1 if yes, else 0) 
        """

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


def prepare_fitness():
    """
    reads the csv file containing the fitness data

    """
    fitness = {}
    with open(FPOWDATA) as csvfile:
        datareader = csv.reader(csvfile, delimiter=";")
        next(csvfile)
        for row in datareader:
            fitness[(int(row[0]), int(row[1]))] = int(row[2])
    return fitness


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


def prepare_params(T, I, M, D):
    """Prepares the parameters based on the data

    Args: 
        T (int): number of years to be considered
        M (dict) : dictionary of heat pumps, each containing the keys:
            'brand_name' (str) : brand name of the heat pump
            'cop' (float) : COP of the heat pump
            'produced heat' (float) : heat produced by the heat pump
            'price'(float): price of heat pump including installation and accessories
        I (dict) : dictionary of buildings each containing the keys:
            "building_type" (str) : building type
            "modernization_status" (str) : status of the building (i.e. whether it is modernized or not)
            "max_heat_demand" (int)  : maximum heat demand of the building (in kWh/m^2)
            "district" (str) : district of the building
            "count" (int) : number of buildings of the same type in the district
         D(array): list of unique districts   
    Returns:
        storage[t,m]: stock level of heat pumps
        heatdemand[i,t]: requested heat demand of a house type in a year
        boilercosts[i]: variable costs for gas boilers per unit of heat
        hpcosts[m]: variable costs for heat pumps per unit of heat
        hpinvestment[m]: fixed purchasing costs for heat pump including installation and accessories
        electr_timefactor[t]:  time factor of Eon's electricity price
        gas_timefactor[t]: time factor of gas price 
        electr_locationfactor[d]: location factor  of  Eon's electricity price
        gas_locationfactor[d]: location factor  of  gas price
        CO2_timefactor[t]:  time factor of CO2 emission price (penalty)
        hpCO2[m]: co2 emission per kwh of each heat pump in operation

                            FOR LATER
        __________________________________________________________________________________________________________
        sub[m]: fixed subsidies for heat pump models
        availablepower[renewable,t]: usable power from renewables
    """

    heatdemand = np.empty(shape=(len(I), T))
    #boilercosts = np.empty(shape=(len(I)))
    hpcosts = np.empty(shape=(len(M)))
    hpinvestment = np.empty(shape=(len(M)))
    max_sales = []
    gas_timefactor = np.empty(T)
    electr_locationfactor = {}
    gas_locationfactor = {}
    CO2_timefactor = np.empty(T)
    hpCO2 = np.empty(shape=(len(M)))

    for t in range(T):
        max_sales.append(111000 + 111000 * 0.14 * t)

    for i in I:
        for t in range(T):
            heatdemand[i, t] = I[i]["average heat demand"]

    #for i in I:
    #    boilercosts[i] = AVERAGE_BOILER_COST_PER_UNIT / BOILER_EFFICIENCY
    boilercosts = AVERAGE_BOILER_COST_PER_UNIT / BOILER_EFFICIENCY
    

    for m in M:
        # hpcost is multiplied with heatdemand in obj function, so it should be cost/kwh.
        # we consider it now as the constant elctricity price of one dimension, since acoording to EON this price can be guaranteed till 2024.
        # Price can be made to dependent on time ( added tax might be increased) and districts by adapting the vector timefactor and locationfactor.
        hpcosts[m] = ELECTRICITY_COST_PER_UNIT / M[m]['cop']
        hpinvestment[m] = M[m]['price']

    # there is a base cost per year to sign EON contract
    # https://www.eon.de/de/pk/strom/stromanbieter/guenstiger-stromanbieter.html
    #hpcosts = [x + 134.36 / 12 for x in hpcosts]

    # price of those terms are currently asummed to rise/fall in a linear manner
    st = 1
    ub = 5
    lb = 0.25
    no = 100
    
    electr_timefactor = np.linspace(st,lb,no)
    gas_timefactor = np.linspace(st,ub,no)
    CO2_timefactor = np.linspace(st,ub,no)

    # price of those terms are currently assumed to be the same over differenct districts
    for d in D:
        electr_locationfactor[d] = 1
        gas_locationfactor[d] = 1

    # heatpump co2 emission based on electricity supplied by EON
    for m in M:
        hpCO2[m] = CO2_EMISSION_EON / M[m]['cop']

    return max_sales, heatdemand, boilercosts, hpcosts, hpinvestment, \
           electr_timefactor, gas_timefactor, electr_locationfactor, gas_locationfactor, CO2_timefactor, hpCO2


""" -> Instead of calculating Fpow within the model, 
we calculate it once in advance and save it as a csv """


# def calcFpow():
#     _, M, I,_,_ = data_preprocess()
#     Fpow = dict()
#     f = open('fpow_test.csv', 'w',newline="")
#     writer= csv.writer(f,delimiter=";")
#     writer.writerow(["house","model","fitness"])
#     for i in I:
#         for m in M:
#             produced_heat = M[m]['produced heat']
#             max_heat_demand = I[i]['max_heat_demand_Patrick']

#             if max_heat_demand <= produced_heat:
#                 # this means the heatpump matches our heat demand
#                 row = [i,m,1]
#                 writer.writerow(row)  
#             else:
#                 row = [i,m,0]
#                 writer.writerow(row)  
#     f.close() 
#     return 
# calcFpow()


def add_price_to_heatpumps():
    heatpump_dataframe = pd.read_csv(HEAT_PUMPS)
    heatpump_dataframe = heatpump_dataframe.iloc[:, 1:]
    df_hp_s = heatpump_dataframe.sort_values(
        ['COP A2/W35', 'Heat output A2/W35 (kW)'], ascending=[True, True])
    heatpump_dataframe = df_hp_s.iloc[::10, :]
    heatpump_dataframe = heatpump_dataframe.reset_index(drop=True)
    # price can't be found
    heatpump_dataframe.drop([0, 3, 10, 12], axis=0, inplace=True)
    heatpump_dataframe = heatpump_dataframe.append(df_hp_s.iloc[-3])
    heatpump_dataframe = heatpump_dataframe.reset_index(drop=True)
    price = [13025, 14316.4, 14108.64, 15175, 9930.55,
             17005.37, 19104.95, 12066.6, 17983.20, 28680]

    #  installation + accessories from https://www.energieheld.de/heizung/waermepumpe/kosten
    price = [x + 3000 for x in price]
    # # if there is discount, original price is taken
    # # https://domotec.ch/wp-content/uploads/2022/06/1.1-pl-allgemein-06.2022-DE.pdf
    # # https://heizung-billiger.de/69503-stiebel-eltron-luft-wasser-warmepumpe-wpl-09-ikcs-classic-stiebel-236377-4017212363775.html?hbdc=DE&utm_source=guenstiger&utm_medium=cpc&utm_campaign=guenstiger-de
    # # https://www.heizungsdiscount24.de/waermepumpen/vaillant-versotherm-plus-vwl-775-luft-wasser-waermepumpe.html?gclid=CjwKCAjwnZaVBhA6EiwAVVyv9MQZvSx9QQuF56cGi9y1Cq8h1lNVzaH_q0FYiCaP7LpHmW8Vs_3EeBoCkU4QAvD_BwE&cq_cmp=13242830342&cq_plt=gp&cq_src=google_ads&cq_net=u
    # # https://domotec.ch/wp-content/uploads/2022/06/1.1-pl-allgemein-06.2022-DE.pdfhttps://domotec.ch/wp-content/uploads/2022/06/1.1-pl-allgemein-06.2022-DE.pdf
    # # https://www.heizungsdiscount24.de/waermepumpen/vaillant-flexotherm-exclusive-vwf-574-heizungswaermepumpe-solewasser.html?cq_src=google_ads&cq_net=u&cq_cmp=13242830342&cq_plt=gp&gclid=CjwKCAjwnZaVBhA6EiwAVVyv9LDV4ncrTDuayjy2mZ2XWxvqs-T0jg902k_jxM-pgcEy8--TXt17SRoCTbwQAvD_BwE
    # # https://docplayer.org/82079403-Preisliste-waermepumpen-systeme-der-cta-ag.html
    # # https://shop.smuk.at/shop/USER_ARTIKEL_HANDLING_AUFRUF.php?Kategorie_ID=9389&Ziel_ID=12271890

    heatpump_dataframe.insert(3, 'price', price, True)

    heatpump_dataframe.to_csv(os.path.join(
        dirname, './data-sources/heat_pumps_air_water_price.csv'), index=False)
