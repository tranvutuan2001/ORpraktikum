#!/usr/bin/env python3
# Template for our final model
from gurobipy import *
import numpy as np

#
# from https://www.haustechnikdialog.de/Forum/t/42992/Auslegung-Waermepumpe-auf-2200-Betriebsstunden-pro-Jahr-#:~:text=Hallo%2C-,ca.,die%20Betriebsdauer%20richtig%20hinzugenommen%20worden.
CONSTANT_HOURS_OF_HEATING_PER_YEAR = 2000
NUMBER_OF_MONTHS = 12  # number of months


def preprocess():
    """Preprocess the data TODO: figure out what input is needed for this function
    Args: 
        Our data sets 
    Returns:
        S (set): set of districts and workforce in that district
        I (dict): clusters of house types. 
            - 'buidling_type': type of building EFH, 
            - 'surface_area': the surface area 
            - 'modernazation_status': the modernization status of the building
            - 'max_heat_demand': the amount of heat this building requires TODO: make sure if this is for a year
            - 'district': the district in which the building is located
            - 'count': the number of houses in a particular cluster
        M (dict) set of heatpumps from https://www.topten.eu/private/products/heat_pumps
            - 'cop': cop of the heat pump
            - 'produced heat': the amount of heat it can produce TODO: find out what this means probably per hour
    """
    raise NotImplementedError("preprocess")
    S = set()
    I = dict()
    M = dict()
    D = None  # for now just return None
    return S, I, M, D


def solve(T=NUMBER_OF_MONTHS, S=None, I=None, M=None, D=None):
    """Solves the heat pump problem.

    Args: 
        T (int): number of months startting from January
        S (set): set of districts and workforce in that district
        I (dict): clusters of house types. 
            - 'buidling_type': type of building EFH, 
            - 'surface_area': the surface area 
            - 'modernazation_status': the modernization status of the building
            - 'max_heat_demand': the amount of heat this building requires TODO: make sure if this is for a year
            - 'district': the district in which the building is located
            - 'count': the number of houses in a particular cluster
        M (dict) set of heatpumps from https://www.topten.eu/private/products/heat_pumps
            - 'cop': cop of the heat pump
            - 'produced heat': the amount of heat it can produce TODO: find out what this means probably per hour

                            FOR LATER
        __________________________________________________________________________________________________________

        # D (dict) set of installation providers . 
        #     - 'location': the location of the installation provider
        #     - 'operating_radius': the radius in which the installation provider operates
        #     - 'total_workforce': the work force of the installation provider
        #     TODO find sources for this. Is this even possible??

    """

    storage, totalhouses, heatdemand, boilercosts, hpcosts, hpinvestment, workforce = prepare_data(
        T, S, I, M, D)

    Fpow = dict()
    for i in I:
        for m in M:
            produced_heat = M[m]['produced heat']
            max_heat_demand = I[i]['max_heat_demand']
            if max_heat_demand / produced_heat >= CONSTANT_HOURS_OF_HEATING_PER_YEAR:
                # this means the heatpump matches our heat demand
                Fpow[(i, m)] = 1
            else:
                Fpow[(i, m)] = 0

    model = Model("Heatpumps")

    # Variables
    x  # Quantity of installed heat pumps with given conditions
    w  # Quantity of installed heat pumps by distributor d

    # Constraints TODO: add constraints

    # Objective
    obj = None  # TODO
    model.setObjective(obj, GRB.MINIMIZE)
    model.update()
    model.optimize()
    return model


def prepare_data():
    """Prepares the parameters based on the data

    Args: 
        T (int): number of months startting from January
        S (set): set of districts and workforce in that district
        I (dict): clusters of house types. each entry is a representative of the cluster (take average values or median or majority). 
            Each entry has the following attributes:
            - 'buidling_type': type of building EFH, 
            - 'surface_area': the surface area 
            - 'modernazation_status': the modernization status of the building
            - 'max_heat_demand': the amount of heat this building requires TODO: make sure if this is for a year
            - 'district': the district in which the building is located
            - 'count': the number of houses in a particular cluster
        M (dict) set of heatpumps from https://www.topten.eu/private/products/heat_pumps
            - 'cop': cop of the heat pump
            - 'produced heat': the amount of heat it can produce TODO: find out what this, means probably per hour

                            FOR LATER
        __________________________________________________________________________________________________________

        # D (dict) set of installation providers . 
        #     - 'location': the location of the installation provider
        #     - 'operating_radius': the radius in which the installation provider operates
        #     - 'total_workforce': the work force of the installation provider
        #     TODO find sources for this. Is this even possible??
    Returns:
        storage[t,m]: stock level of heat pumps
        totalhouses[i,s]: total count of similar houses in a district
        heatdemand[i,t]: requested heat demand of a house type in a month
        boilercosts[b,s]: variable costs for gas boilers per unit of heat
        hpcosts[m,s]: variable costs for heat pumps per unit of heat
        hpinvestment[m,s]: fixed purchasing costs for heat pump
        workforce[d,t]: workforce capacities of distributors per month

                            FOR LATER
        __________________________________________________________________________________________________________
        sub[m]: fixed subsidies for heat pump models
        availablepower[renewable,t]: usable power from renewables
    """

    storage = np.empty(shape=(T, len(M)))
    totalhouses = np.empty(shape=(len(I), len(S)))
    heatdemand = np.empty(shape=(len(I), T))
    boilercosts = np.empty(shape=(len(B), len(S)))
    hpcosts = np.empty(shape=(len(M), len(S)))
    hpinvestment = np.empty(shape=(len(M), len(S)))
    workforce = np.empty(shape=(len(D), T))
    # sub = np.empty(shape=(len(M)))
    # availablepower = np.empty(shape=(len(renawable), T))
    for t in range(T):
        for m in M:
            storage[t, m] = 1000

    for i in I:
        for s in S:
            totalhouses[i, s] = I[i]['count']
        for t in range(T):
            heatdemand[i, t] = I[i]['max_heat_demand'] / \
                12  # to get the heat demand per month

    for b in B:
        for s in S:
            boilercosts[b, s] = B[b]['cost']

    for m in M:
        for s in S:
            hpcosts[m, s] = M[m]['produced heat'] / M[m]['cop']
            hpinvestment[m, s] = M[m]['investment']

    for d in D:
        for t in range(T):
            workforce[d, t] = D[d]['total_workforce']

    return storage, totalhouses, heatdemand, boilercosts, hpcosts, hpinvestment, workforce
