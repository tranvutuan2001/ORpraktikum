import pandas as pd
import random
import os

dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, "../data-sources/ACoolHeadAppendix.xlsx")
HEAT_PUMPS = os.path.join(dirname, "../data-sources/heat_pumps.csv")

def data_preprocess():
    df = pd.read_excel(ACOOLHEAD, engine='openpyxl')
    df_hp = pd.read_csv(HEAT_PUMPS)
    district = df['Administrative district'].unique()
    workforce = []
    for i in range(0, 399):
        n = random.randint(1, 20)
        workforce.append(n)
    df_hp = df_hp[df_hp["Type"] == "air-water"]
    df_hp = df_hp.reset_index(drop=True)
    df_hp['hp_name'] = df_hp["Provider"] + "-" + df_hp["Series"]
    df_i = df[['Administrative district', 'Type of building',
               'Surface area [m^2]', 'modernization status', 'max heat demand [kWh/m^2]']]
    dict_s = {i:
              {
                  "district": district[i],
                  "workforce": workforce[i]
              }
              for i in range(len(workforce))}
    dict_m = {i:
              {
                  "brand_name": df_hp['hp_name'][i],
                  "cop": df_hp['COP A2/W35'][i],
                  "produced heat": df_hp['Heat output A2/W35 (kW)'][i]
              }
              for i in range(len(df_hp['hp_name']))}
    dict_i = {i:
              {
                  "building_type": df_i['Type of building'][i],
                  "surface_area": df_i['Surface area [m^2]'][i],
                  "modernization_status": df_i['modernization status'][i],
                  "max_heat_demand": df_i['max heat demand [kWh/m^2]'][i],
                  "district": df_i['Administrative district'][i],
                  'count': 3990
              }
              for i in range(len(df_i["Administrative district"]))}
    return dict_s, dict_m, dict_i
