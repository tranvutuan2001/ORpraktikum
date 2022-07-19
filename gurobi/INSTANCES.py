#Parameters
NUMBER_OF_YEARS = 15 # also the average lifespan of a heat pump
MIN_PERCENTAGE = 0 # actually not percentage :)
CO2_EMISSION_GAS = 433 # g/kWh
CO2_EMISSION_EON = 222 # g/kwh
BOILER_EFFICIENCY = 0.7 # between 0 and 1
GAS_PRIZE_FACTOR = 2.4 # Compared to Initial Value
ELECTRICITY_PRICE_FACTOR = 1.21  #Compared to Initial Value
CO2_EMISSION_FACTOR = 0.8
ELECTRICITY_SUBS = 1
HEATPUMP_SUBS = 0.55 # BEG funding 2021
CO2_PRIZE_FACTOR = 6.25 # Compared to Initial Value
Max_Sales_Growth = 0.05 # per year
Max_Sales_Initial = 110000 # units per year
WORKFORCE_FACTOR = 1.05  # Compared to Initial value

#Emission Prices can be either static welfare based values, or on the CO2 prices. We decided to consider more than the certificat price
#then balanced with the welfare losses caused by climate change for current and future generations, alternatively 698E-6
CO2_EMISSION_PRICE = 80E-6  # euro/gramm, 2021 nEHS

# from https://www.globalpetrolprices.com/Germany/natural_gas_prices/
AVERAGE_BOILER_COST_PER_UNIT = 0.13

# from https://www.finanztip.de/stromvergleich/strompreis/#:~:text=Strom%20hat%20in%20Deutschland%20einen,und%20Wasserwirtschaft%20(BDEW)%20hervor.
ELECTRICITY_COST_PER_UNIT = 0.3714

# -*- coding: utf-8 -*-
#INSTANCES
from gurobipy import *
import numpy as np
import numpy_financial as npf
import modelsolver
from dataprp import data_preprocess
import os
from printsolution import write_solution_csv
import sys
from datetime import datetime

name=os.path.basename(__file__)+"_"+datetime.now().strftime("%m_%d-%I_%M")
print(name)


# This writes our console output to a log file
dirname = os.path.dirname(__file__)
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        if not os.path.exists(os.path.join(dirname, '/logs')):
            os.makedirs('\logs')
        current_time = datetime.now()
        file_name = os.path.join(
            dirname, '/logs/log_' + current_time.strftime("%Y-%m-%d_%H-%M-%S") + '.log')
        self.log = open(file_name, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass


sys.stdout = Logger()

#paths
ACOOLHEAD = os.path.join(dirname, './data-sources/HOUSING.csv')
DISTRIBUTOR = os.path.join(dirname, './data-sources/Distributor_data.csv')
HEAT_PUMPS = os.path.join(dirname, './data-sources/heat_pumps_air_water_price.csv')
FPOWDATA = os.path.join(dirname, './data-sources/fpow.csv')
PARAMETERS = os.path.join(dirname, './data-sources/parameters.xlsx')

##ADD TIME DEPENDANT FACTORS
electr_timefactor = np.linspace(1,ELECTRICITY_PRICE_FACTOR ,NUMBER_OF_YEARS) #The second factor is the multiplying factor for the final value, so the price is x times the starting price
gas_timefactor = np.linspace(1,GAS_PRIZE_FACTOR ,NUMBER_OF_YEARS) #The second factor is the multiplying factor for the final value, so the price is x times the starting price
CO2_timefactor = np.linspace(1,CO2_PRIZE_FACTOR ,NUMBER_OF_YEARS) #The second factor is the multiplying factor for the final value, so the price is x times the starting price
# The second factor is the multiplying factor for the final value, so the emission is x times the starting emission
CO2EMIS_timefactor = np.linspace(1, CO2_EMISSION_FACTOR, NUMBER_OF_YEARS)
max_sales = npf.fv(Max_Sales_Growth, np.linspace(0,NUMBER_OF_YEARS+1,NUMBER_OF_YEARS, dtype = int), 0, -Max_Sales_Initial) #Third value is fixed addition
# get prepared data


(districts, heatpumps, housing, fitness, distributors, configurations) = data_preprocess(NUMBER_OF_YEARS, operating_radius)




# solve model
model = modelsolver.solve(districts, heatpumps, housing, fitness, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
          CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY, 
          CO2_EMISSION_PRICE, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
          electr_timefactor, gas_timefactor, CO2_timefactor,CO2EMIS_timefactor, configurations, WORKFORCE_FACTOR, ELECTRICITY_SUBS, HEATPUMP_SUBS)

write_solution_csv(model, districts, heatpumps, housing, NUMBER_OF_YEARS, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
                   CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY,
                   CO2_EMISSION_PRICE, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
                   electr_timefactor, gas_timefactor, CO2_timefactor, configurations,  ELECTRICITY_SUBS, HEATPUMP_SUBS, name)
