from functools import reduce
from locale import atof, setlocale, LC_NUMERIC
import pandas as pd
import numpy as np
import math

AVERAGE_PRICE_FOR_ELECTRICITY = 32.12


def load_csv(path, delimiter=","):
    """Loads a csv file from a path and returns a pandas dataframe

        Args:
            path (str): path of the csv file, either local or remote
            delimiter (str): delimiter used in the csv file (default: ",") some datasets will use ; instead of ,
        Returns:
            pandas.DataFrame: dataframe containing the data from the csv file

    """
    df = pd.read_csv(path, delimiter=delimiter)
    return df


def get_when2heat_dataset():
    """Loads the when2heat dataset from the local machine

    Returns:
        pandas.DataFrame: dataframe containing the when2heat dataset
    """
    file_path = "C:\Repositories\ORpraktikum\data-sources\when2heat.csv"
    df = load_csv(file_path, delimiter=";")
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
    df_germany.to_csv(
        "C:\Repositories\ORpraktikum\data-sources\when2heat_germany.csv", index=False)
    print(df_germany.describe())
    print()

    heat_demand = df_germany[["DE_heat_demand_space_MFH", "DE_heat_demand_space_SFH", "DE_heat_demand_water_MFH", "DE_heat_demand_water_SFH"]].mean(
    ).tolist()
    cop = df_germany[["DE_COP_ASHP_floor",
                      "DE_COP_ASHP_radiator", "DE_COP_ASHP_water"]].mean().tolist()

    energy_consumption = get_mean(heat_demand)/get_mean(cop)
    energy_price = math.ceil(
        AVERAGE_PRICE_FOR_ELECTRICITY*energy_consumption/100)
    # TODO: check the units that we used in the dataset
    print(
        f"An average german household needs {get_mean(heat_demand)} of heating capacity.\nThe average heat pump has a COP of {get_mean(cop)}.\nThe price is thus {energy_price} Euros")

    return df_germany, energy_price


def get_mean(lst):
    return reduce(lambda a, b: a + b, lst) / len(lst)
# Example


get_when2heat_dataset()
# we assume heat demand = heat produced by a heatpump and thereby can calculate the energy consumption of a heat pump installation
