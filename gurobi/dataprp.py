import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

def data_preprocess():
    df = pd.read_excel("../data-sources/ACoolHeadAppendix.xlsx")
    df_hp = pd.read_csv("../data-sources/heat_pumps.csv")
    district = df['Administrative district'].unique()
    workforce = []
    for i in range(0,399):
        n = random.randint(1,20)
        workforce.append(n)
    dict_s =  {i: {"district": district[i], "workforce": workforce[i]} for i in range(len(workforce))}
    df_hp = df_hp[df_hp["Type"]=="air-water"]
    df_hp = df_hp.reset_index(drop=True)
    df_hp['hp_name']= df_hp["Provider"] + "-" + df_hp["Series"]
    dict_m =  {i: {"brand_name":df_hp['hp_name'][i], "cop":df_hp['COP A2/W35'][i], "produced heat":df_hp['Heat output A2/W35 (kW)'][i]} for i in range(len(df_hp['hp_name']))}
    df_i = df[['Administrative district','Type of building','Surface area [m^2]','modernization status','max heat demand [kWh/m^2]' ]]
    dict_i =  {i: {"building_type":df_i['Type of building'][i], "surface_area":df_i['Surface area [m^2]'][i], "modernization_status":df_i['modernization status'][i],"max_heat_demand":df_i['max heat demand [kWh/m^2]'][i],"district":df_i['Administrative district'][i],'count':3990} for i in range(len(df_i["Administrative district"]))}
    return dict_s,dict_m,dict_i