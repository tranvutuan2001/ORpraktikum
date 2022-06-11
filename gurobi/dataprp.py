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

    df["Number of buildings"] = df["Number of buildings"].round(0).astype("int")  #rounding of the no of buildings
    df = df[df["Number of buildings"]>0]   #removing all the data with no of buildings as zero
    df['max heat demand [kWh]'] = df['max heat demand [kWh/m^2]'] * df['Surface area [m^2]'] / 3600   #since heat demand was in [kWh/m^2]  
    df = df[df['max heat demand [kWh]']<30]   #for now only considering the data with heat demand less than 30
    
    df1 = df[df['Year of construction']<1994] 
    df2 = df[df['Year of construction']>1994] #data to group together for year 2001,2009 and 2015
    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)

    df_i = df2[['Administrative district', 'Type of building', 'Number of buildings',
               'Surface area [m^2]', 'modernization status', 'max heat demand [kWh]']] 

    #grouping only data for yeae 2001, 2009 and 2015
    df_i = df_i.groupby(by=['Administrative district', 'Type of building', 'modernization status']).agg(
        max_heat_demand=pd.NamedAgg(column='max heat demand [kWh]', aggfunc=max),
        quantity=pd.NamedAgg(column='Number of buildings', aggfunc='sum'),
        building_type=pd.NamedAgg(column='Type of building', aggfunc='first'),
        district=pd.NamedAgg(column='Administrative district', aggfunc='first'),
        modernization_status=pd.NamedAgg(column='modernization status', aggfunc='first')
    )  

    df_i = df_i.reset_index(drop=True)
    #grouped data for the above years transformed into a dictionary
    dict1 = df_i.to_dict('index')
    index = len(dict1)

   #taking rest of the data for year before 2001 as it is without grouping
    dict2 = {i:
              {
                  "max_heat_demand": df1['max heat demand [kWh]'][i-index],
                  "quantity": df1['Number of buildings'][i-index],
                  "building_type":df1['Type of building'][i-index],
                  'district':df1['Administrative district'][i-index],
                  "modernization_status": df1['modernization status'][i-index],
              }
              for i in range(index,index+len(df1["Administrative district"]))}
    
    #combining both the dictionaries together  , the length of combined dictionary is 17442
    return dict1 | dict2


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
