from functools import reduce
from locale import atof, setlocale, LC_NUMERIC
import pandas as pd
import numpy as np
import math

AVERAGE_PRICE_FOR_ELECTRICITY = 32.12


def load_csv(path, delimiter=",", dtype=str):
    """Loads a csv file from a path and returns a pandas dataframe

        Args:
            path (str): path of the csv file, either local or remote
            delimiter (str): delimiter used in the csv file (default: ",") some datasets will use ; instead of ,
        Returns:
            pandas.DataFrame: dataframe containing the data from the csv file

    """
    df = pd.read_csv(path, delimiter=delimiter, dtype=dtype)
    return df


def get_when2heat_dataset():
    """Loads the when2heat dataset from the local machine. Infor about this dataset can be found on https://data.open-power-system-data.org/when2heat/latest

    Returns:
        pandas.DataFrame: dataframe containing the when2heat dataset
    """
    print('Downloading dataset...')
    df = load_csv(
        "https://data.open-power-system-data.org/when2heat/latest/when2heat.csv", delimiter=";")
    print('Download done.')
    desired_column_names = ["utc_timestamp", "DE_COP_ASHP_floor",
                            "DE_COP_ASHP_radiator", "DE_COP_ASHP_water", "DE_heat_demand_space_MFH", "DE_heat_demand_space_SFH", "DE_heat_demand_water_MFH", "DE_heat_demand_water_SFH"]

    df_germany = df[desired_column_names].copy()

    # clean dataset
    for column in df_germany.columns:
        if column != "utc_timestamp":
            df_germany[column] = df_germany[column].astype(str).str.replace(
                ",", ".")
            # data set stores numbers with a comma instead of a dot so we need to replace them
            df_germany[column] = df_germany[column].astype(
                "float64")  # transform into float values
    # print(df_germany.describe())
    # print()

    heat_demand = df_germany[["DE_heat_demand_space_MFH", "DE_heat_demand_space_SFH", "DE_heat_demand_water_MFH", "DE_heat_demand_water_SFH"]].mean(
    ).tolist()
    cop = df_germany[["DE_COP_ASHP_floor",
                      "DE_COP_ASHP_radiator", "DE_COP_ASHP_water"]].mean().tolist()
    # we assume heat demand = heat produced by a heatpump and thereby can calculate the energy consumption of a heat pump installation
    energy_consumption = get_mean(heat_demand)/get_mean(cop)
    energy_price = math.ceil(
        AVERAGE_PRICE_FOR_ELECTRICITY*energy_consumption/100)
    # TODO: check the units that we used in the dataset
    # print(
    #     f"An average german household needs {get_mean(heat_demand)} of heating capacity.\nThe average heat pump has a COP of {get_mean(cop)}.\nThe price is thus {energy_price} Euros")

    return df_germany, energy_price


def get_mean(lst):
    return reduce(lambda a, b: a + b, lst) / len(lst)
# Example


def yearly_electric_costs():
    """Calculates the yearly costs of electricity

    Returns:
        float: yearly costs of electricity
    """
    _, costs = get_when2heat_dataset()
    return costs
