
import pandas as pd
import os
from gurobipy import *
from gurobipy import GRB
import csv
import timeit
import numpy as np
import json

dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, './data-sources/data_from_Hannah_with_coordinates_zipcodes_heatcapacity.csv')
HEAT_PUMPS = os.path.join(dirname, './data-sources/heat_pumps_air_water_only.csv')
FPOWDATA = os.path.join(dirname, './data-sources/fpow.csv')



def data_preprocess():
    """    
    This function preprocesses the data from the excel and csv file and returns S,M,I, fitness
    Returns:
        S (dict) : dictionary of district names and workfoce in that district
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
    
    print("Preprocess the data")
    start = timeit.default_timer()
    
    df = pd.read_csv(ACOOLHEAD)
    df = df.head(1000)
    df = df.reset_index(drop=True)

    df_hp = pd.read_csv(HEAT_PUMPS)
    df_hp = df_hp.head(15)
    df_hp = df_hp.reset_index(drop=True)

    dict_i = prepare_housing_data(df)
    dict_s = prepare_workforce_data(df)
    dict_m = prepare_heatpump_data(df_hp)
    
    fitness= prepare_fitness()
    
    stop = timeit.default_timer()
    print('Time in seconds to prepare the data: ', stop - start, "\n")
    return  dict_s, dict_m,dict_i, fitness


def prepare_fitness():
    """
    reads the csv file containing the fitness data

    """
    fitness={}
    with open(FPOWDATA) as csvfile:
        datareader = csv.reader(csvfile,delimiter=";")
        next(csvfile)
        for row in datareader:
            fitness[(int(row[0]),int(row[1]))]=int(row[2])
    return fitness
   

def prepare_housing_data(df):
    dict_i= {i:
             {
                 "district": df["Administrative district"][i],
                 "type of building": df["Type of building"][i],
                 "quantity": int(round(df["Number of buildings"][i],0)),
                 "Surface area": int(df["Surface area [m^2]"][i]),
                 "modernization status": df["modernization status"][i],
                 "max heat demand [kWh/m^2]": df["max heat demand [kWh/m^2]"][i],
                 "average heat demand": df["average heat demand [kWh/m^2]"][i],
                 "Heatcapacity": df["Heatcapacity"][i],
                 "Klimazone": df["Klimazone"][i],
                 "year of construction": df["Year of construction"][i],
                 "max_heat_demand_Patrick": round(int(df["Surface area [m^2]"][i])*df["Heatcapacity"][i]/1000,2),
                 #"Floors": df["Floors"][i]
                 }
             for i in range(len(df["long"]))}
        
    return dict_i


def prepare_heatpump_data(df_hp):
    dict_m = {i:
        {
            'brand_name': df_hp['hp_name'][i],
            'cop': df_hp['COP A2/W35'][i],
            'produced heat': df_hp['Heat output A2/W35 (kW)'][i]
        }
        for i in range(len(df_hp['hp_name']))}
        
    return dict_m




def prepare_workforce_data(df):
    district = df['Administrative district'].unique()
    workforce = []

#TODO: replace below with functional realistic code

    for i in range(0, len(district)):
        n = 10000000000000
        if i < len(district) / 2:
            n = 100000000000000
        workforce.append(n)

    dict_s = {district[i]: workforce[i] for i in range(len(district))}

    return dict_s





def prepare_params(T, I, M):
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
    
    print("Prepare the parameters")
    start = timeit.default_timer()
    AVERAGE_BOILER_COST_PER_UNIT = 0.17
    heatdemand = np.empty(shape=(len(I), T))
    boilercosts = np.empty(shape=(len(I)))
    hpcosts = np.empty(shape=(len(M)))
    hpinvestment = np.empty(shape=(len(M)))
    max_sales= []
    
    for t in range(T):
        max_sales.append(111000+111000*0.14*t)
        
    for i in I:
        for t in range(T):
            heatdemand[i, t] = I[i]["average heat demand"]

    for i in I:
        boilercosts[i] = AVERAGE_BOILER_COST_PER_UNIT

    for m in M:
        hpcosts[m] = 0.56 / M[m]['cop']
        
        hpinvestment[m] = 1
    stop = timeit.default_timer()
    print('Time in seconds to prepare the parameters ', stop - start)
    
    return max_sales, heatdemand, boilercosts, hpcosts, hpinvestment



""" -> Instead of calculating Fpow within the model, 
we calculate it once in advance and save it as a csv
def calcFpow():
    D, M, I = data_preprocess()
    Fpow = dict()
    f = open('fpow.csv', 'w',newline="")
    writer= csv.writer(f,delimiter=";")
    writer.writerow(["house","model","fitness"])
    for i in I:
        for m in M:
            produced_heat = M[m]['produced heat']
            max_heat_demand = I[i]['max_heat_demand_Patrick']
           
            if max_heat_demand <= produced_heat:
                # this means the heatpump matches our heat demand
                row = [i,m,1]
                writer.writerow(row)  
            else:
                row = [i,m,0]
                writer.writerow(row)  
    f.close() 
    return 
calcFpow()
"""
