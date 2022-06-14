import pandas as pd
import random
import os

dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, './data-sources/ACoolHeadAppendix.xlsx')
HEAT_PUMPS = os.path.join(dirname, './data-sources/heat_pumps_air_water_only.csv')


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
            'building_type' (str) : building type
            'modernization_status' (str) : status of the building (i.e. whether it is modernized or not)
            'max_heat_demand' (int)  : maximum heat demand of the building (in kWh/m^2)
            'district' (str) : district of the building
            'count' (int) : number of buildings of the same type in the district
    """
    df = pd.read_excel(ACOOLHEAD, engine='openpyxl')
    df = df.head(40)

    df_hp = pd.read_csv(HEAT_PUMPS)
    df_hp = df_hp.head(5)
    df_hp = df_hp.reset_index(drop=True)

    dict_i = prepare_housing_data(df)
    dict_s = prepare_workforce_data(df)
    dict_m = prepare_heatpump_data(df_hp)

    return dict_s, dict_m, dict_i


def prepare_housing_data(df):
    df_i = df[['Administrative district', 'Type of building', 'Number of buildings',
               'Surface area [m^2]', 'modernization status', 'max heat demand [kWh/m^2]']]

    df_i['max heat demand [kWh/m^2]'] = df_i['max heat demand [kWh/m^2]'] * df_i['Surface area [m^2]'] / 3600

    df_i = df_i.groupby(by=['Administrative district', 'Type of building', 'modernization status']).agg(
        max_heat_demand=pd.NamedAgg(column='max heat demand [kWh/m^2]', aggfunc=max),
        quantity=pd.NamedAgg(column='Number of buildings', aggfunc='sum'),
        building_type=pd.NamedAgg(column='Type of building', aggfunc='first'),
        district=pd.NamedAgg(column='Administrative district', aggfunc='first'),
        modernization_status=pd.NamedAgg(column='modernization status', aggfunc='first')
    )

    df_i = df_i[df_i['max_heat_demand'] < 30]
    df_i['quantity'] = df_i['quantity'].round(0)
    df_i = df_i.reset_index(drop=True)

    return df_i.to_dict('index')


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

    for i in range(0, len(district)):
        n = 1000
        if i < len(district) / 2:
            n = 2000
        workforce.append(n)

    dict_s = {district[i]: workforce[i] for i in range(len(district))}

    return dict_s
