#INSTANCES
from gurobipy import *
import numpy as np
import numpy_financial as npf
import modelsolver
from dataprp import data_preprocess
import os

#paths
dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, './data-sources/data_from_Hannah_with_coordinates_zipcodes_heatcapacity_positive_building_count.csv')
DISTRIBUTOR = os.path.join(dirname, './data-sources/Distributor_data_with_coordinates.csv')
HEAT_PUMPS = os.path.join(dirname, './data-sources/heat_pumps_air_water_price.csv')
FPOWDATA = os.path.join(dirname, './data-sources/fpow.csv')
PARAMETERS = os.path.join(dirname, './data-sources/parameters.xlsx')

#Parameters
NUMBER_OF_YEARS = 12
MIN_PERCENTAGE = 0.8 #actually not percentage :)
CO2_EMISSION_GAS = 433 #g/kWh
CO2_EMISSION_EON = 266 #g/kwh
BOILER_EFFICIENCY = 0.7 #between 0 and 1
GAS_PRIZE_FACTOR = 5 #Compared to Initial Value
ELECTRICITY_PRICE_FACTOR = 0.2 #Compared to Initial Value
CO2_PRIZE_FACTOR = 5 #Compared to Initial Value
Max_Sales_Growth = 0.05 #per year
Max_Sales_Initial = 1100000000 #units per year
OPERATING_RADIUS = 2000  # km

#Emission Prices can be either static welfare based values, or on the CO2 prices. We decided to consider more than the certificat price
#then balanced with the welfare losses caused by climate change for current and future generations, alternatively 698E-6
CO2_EMISSION_PRICE = 201E-6  # euro/gramm,  suggestion by German Environment Agency euro/gram,  

# from https://www.globalpetrolprices.com/Germany/natural_gas_prices/
AVERAGE_BOILER_COST_PER_UNIT = 0.13

# from https://www.eon.de/de/gk/strom/oekostrom.html#:~:text=Im%20Jahr%201990%20lag%20der,der%20CO%202%2DEmissionen%20leisten.
ELECTRICITY_COST_PER_UNIT = 0.4805

##ADD TIME DEPENDANT FACTORS
electr_timefactor = np.linspace(1,ELECTRICITY_PRICE_FACTOR ,NUMBER_OF_YEARS) #The second factor is the multiplying factor for the final value, so the price is x times the starting price
gas_timefactor = np.linspace(1,GAS_PRIZE_FACTOR ,NUMBER_OF_YEARS) #The second factor is the multiplying factor for the final value, so the price is x times the starting price
CO2_timefactor = np.linspace(1,CO2_PRIZE_FACTOR ,NUMBER_OF_YEARS) #The second factor is the multiplying factor for the final value, so the price is x times the starting price
max_sales = npf.fv(Max_Sales_Growth, np.linspace(0,NUMBER_OF_YEARS+1,NUMBER_OF_YEARS, dtype = int), 0, -Max_Sales_Initial) #Third value is fixed addition
print(max_sales)
# get prepared data
(districts, heatpumps, housing, fitness, distributors) = data_preprocess()

# solve model
modelsolver.solve(districts, heatpumps, housing, fitness, distributors, NUMBER_OF_YEARS, MIN_PERCENTAGE,
          CO2_EMISSION_GAS, CO2_EMISSION_EON, BOILER_EFFICIENCY, 
          CO2_EMISSION_PRICE, max_sales, AVERAGE_BOILER_COST_PER_UNIT, ELECTRICITY_COST_PER_UNIT,
          electr_timefactor, gas_timefactor, CO2_timefactor,operating_radius = OPERATING_RADIUS)