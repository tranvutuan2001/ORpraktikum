import pandas as pd
import random
import os

dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, "./data-sources/ACoolHeadAppendix.xlsx")
HEAT_PUMPS = os.path.join(dirname, "./data-sources/heat_pumps.csv")

def data_preprocess():
    """
    This function preprocesses the data from the excel and csv file and returns S,M,I.
    Returns:
        S (dict) : dictionary of district names and workfoce in that district
        M (dict) : dictionary of heat pumps, each containing the keys:
            'brand_name' (str) : brand name of the heat pump
            'cop' (float) : COP of the heat pump
            'produced heat' (float) : heat produced by the heat pump
        I (dict) : dictionary of buildings each containing the keys:
            "building_type" (str) : building type
            "surface_area" (int)  : surface area of the building (in m^2)
            "modernization_status" (str) : status of the building (i.e. whether it is modernized or not)
            "max_heat_demand" (int)  : maximum heat demand of the building (in kWh/m^2)
            "district" (str) : district of the building
            "count" (int) : number of buildings of the same type in the district       
    """
    df = pd.read_excel(ACOOLHEAD, engine='openpyxl')
    df['grouped_building_count'] = df.groupby(["modernization status","Type of building"])["Number of buildings"].transform('sum')
    df = df.head(1000)
    df_hp = pd.read_csv(HEAT_PUMPS)

    district = df['Administrative district'].unique()
    workforce = []
    for i in range(0, len(district)):
        n = random.randint(1, 20)
        workforce.append(n)
    df_hp = df_hp[df_hp["Type"] == "air-water"]
    df_hp = df_hp.head(5)
    df_hp = df_hp.reset_index(drop=True)
    df_hp['hp_name'] = df_hp["Provider"] + "-" + df_hp["Series"]
    df_i = df[['Administrative district', 'Type of building',
               'Surface area [m^2]', 'modernization status', 'max heat demand [kWh/m^2]','grouped_building_count']]
    dict_s = {i:
              {
                  "district": district[i],
                  "workforce": workforce[i]
              }
              for i in range(len(district))}
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
                  "max_heat_demand": df_i['max heat demand [kWh/m^2]'][i] * df_i['Surface area [m^2]'][i] / 3600,
                  "district": df_i['Administrative district'][i],
                  'count': df_i['grouped_building_count']
              }
              for i in range(len(df_i["Administrative district"]))}
    return dict_s, dict_m, dict_i
