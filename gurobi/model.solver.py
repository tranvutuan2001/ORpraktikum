#!/usr/bin/env python3
# Template for our final model
from gurobipy import *

#
# from https://www.haustechnikdialog.de/Forum/t/42992/Auslegung-Waermepumpe-auf-2200-Betriebsstunden-pro-Jahr-#:~:text=Hallo%2C-,ca.,die%20Betriebsdauer%20richtig%20hinzugenommen%20worden.
CONSTANT_HOURS_OF_HEATING_PER_YEAR = 2000


def solve(T, S, I, M, D):
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
        # D (dict) set of installation providers
        #     - 'location': the location of the installation provider
        #     - 'operating_radius': the radius in which the installation provider operates
        #     - 'total_workforce': the work force of the installation provider
        #     TODO find sources for this. Is this even possible??

    """
    #     (1) Instead of calculating distances from heating installer to districts, we can

    # calculate a matrix/dict Ad, s, which tells us if a district is within the operating
    # radius of a distributor.
    # Iff → | distributorlocationd − districtlocations | ≤ opradiusd → Ad, s = 1, else 0.

    model = Model("Heatpumps")

    # Variables
    P = {}
    costs = {}
    benefits = {}
    possibile_configs = determine_possible_configurations(
        buildings, heatpumps, installation_providers)
    for (building, heatpump, provider) in possibile_configs:
        P[(building, heatpump, provider)] = model.addVar(
            vtype=GRB.BINARY, name=f'P({building},{heatpump},{provider})')
        costs[(building, heatpump, provider)] = determine_costs(
            building, heatpump, provider)
        benefits[(building, heatpump, provider)] = determine_benefits(
            building, heatpump, provider)

    # Constraints TODO: add constraints

    # Objective
    # minimize the costs
    obj1 = weights[0]*quicksum(P[(building, heatpump, provider)] * costs[(building, heatpump, provider)]
                               for building in buildings
                               for heatpump in heatpumps
                               for provider in installation_providers)
    # maximize the benefits
    obj2 = weights[1]*quicksum(P[(building, heatpump, provider)] * benefits[(building, heatpump, provider)]
                               for building in buildings
                               for heatpump in heatpumps
                               for provider in installation_providers)
    # benefits are negative costs in this case
    model.setObjective(obj1-obj2, GRB.MINIMIZE)
    model.update()
    model.optimize()
    return model


def determine_costs(building, heatpump, provider):
    """Determine the cost of installing this heatpump in that building by the given provider

    Args:
        building (_type_): the building that we might install the heatpump in
        heatpump (_type_): the heatpump to be installed
        provider (_type_): the provider that we choose

    Returns:
        float: the cost of installing the heatpump in the building by the given provider
    """
    return


def determine_benefits(building, heatpump, provider):
    """Determine the benefits of installing this heatpump in that building by the given provider

    Args:
        building (_type_): the building that we might install the heatpump in
        heatpump (_type_): the heatpump to be installed
        provider (_type_): the provider that we choose

    Returns:
        float: the benefits of installing the heatpump in the building by the given provider
    """
    return


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


def preprocess():
    """Preprocess the data TODO: figure out what input is needed for this function

    Returns:
        buildings (dict): a dictionary of buildings. each building should contain the following keys: 'location': its location (should be the name of a region) , 'emission_factor': the amount of emmissions produces by it, 'heat_demand': the amount of heat this building requires
        heatpumps (dict): a dictionary of heatpumps representing our heatpump stock. each entry should contain  the following keys: 'cop': cop of the heat pump, 'produced heat': the amount of heat it can produce, 'count': number of heatpumps of this type in stock
        installation_providers (dict): a dictionary of installation providers. each installation provider should contain the following keys: 'locations': locations in which this provider operates, 'installation_cost': fixed cost per installation, 'heat_pumps': types of heat pump they can install (maybe also supplementary installation costs)
    """
    return
