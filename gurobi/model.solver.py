#!/usr/bin/env python3
# Template for our final model
from gurobipy import *

#
# from https://www.haustechnikdialog.de/Forum/t/42992/Auslegung-Waermepumpe-auf-2200-Betriebsstunden-pro-Jahr-#:~:text=Hallo%2C-,ca.,die%20Betriebsdauer%20richtig%20hinzugenommen%20worden.
CONSTANT_HOURS_OF_HEATING_PER_YEAR = 2000
NUMBER_OF_MONTHS = 12  # number of months


def preprocess():
    """Preprocess the data TODO: figure out what input is needed for this function
    Args: 
        Our data sets 
    Returns:
        T (set/or int): set of months from now on or range(T) if integer TODO: decide on what type to use
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
        T (set/or int): set of months from now on or range(T) if integer TODO: decide on what type to use
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

    Fpow=dict()
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
    obj = None # TODO
    model.setObjective(obj, GRB.MINIMIZE)
    model.update()
    model.optimize()
    return model


def prepare_data():
    """Prepares the parameters based on the data

    Args: 
        T (set/or int): set of months from now on or range(T) if integer TODO: decide on what type to use
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


def determine_possible_configurations(buildings, heatpumps, installation_providers):
    """Determine possible configurations of heatpumps. There are many configurations that are not possible because of certain conditions: 
        - heatpumps need to be able to produce at least as much heat as the demand for the building in which they are installed
        - the heatpump that needs to be installed is in stock (stock>0)
        - the installation provider needs to be able to install the selected heatpump
        - the installation provider needs to operate in the location that the building is in   

    Args:
        buildings (dict): a dictionary of buildings. each building should contain the following keys: 'location': its location (should be the name of a region) , 'emission_factor': the amount of emmissions produces by it, 'heat_demand': the amount of heat this building requires
        heatpumps (dict): a dictionary of heatpumps representing our heatpump stock. each entry should contain  the following keys: 'cop': cop of the heat pump, 'produced heat': the amount of heat it can produce, 'count': number of heatpumps of this type in stock
        installation_providers (dict): a dictionary of installation providers. each installation provider should contain the following keys: 'locations': locations in which this provider operates, 'installation_cost': fixed cost per installation, 'heat_pumps': types of heat pump they can install (maybe also supplementary installation costs)

    Returns:
        list: a list of possible configurations (h,b,i) where h is the heatpump type, b is the building type and i is the installation provider
    """
    # for provider in installation_providers:
    #     for building in buildings:
    #         # - the installation provider needs to operate in the location that the building is in
    #         if building['location'] in installation_providers[provider]['locations']:
    #             for heatpump in heatpumps:
    #                 # - the heatpump that needs to be installed is in stock(stock > 0)
    #                 if heatpump['stock'] > 0:
    #                 # - heatpumps need to be able to produce at least as much heat as the demand for the building in which they are installed
    #                 if heatpump['produced heat'] >= building['heat demand']:
    #                 # - the installation provider needs to be able to install the selected heatpump
    #                 if heatpump in provider['heat_pumps']:

    return
