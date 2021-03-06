import pandas as pd
import numpy as np
import os


dirname = os.path.dirname(__file__)
DISTRIBUTOR = os.path.join(dirname, './data-sources/Distributor_data.csv')
df_distributor = pd.read_csv(DISTRIBUTOR)

# https://www.isoenergy.co.uk/latest-news/renewable-energy-news-from-isoenergy/how-long-will-it-take-to-have-a-heat-pump-installed#:~:text=A%20domestic%20air%20source%20heat,setting%20the%20system%20to%20work.
# installation performed by 2 plumbers, 1 eletrician in the first week and then 2 tester in the second week. 
# our assumption:  team of 2 workers can install 1 heat pump per week. 
# Starting point: around 6500 workers in total in 2022 according to: https://www.ehpa.org/fileadmin/red/07._Market_Data/2014/EHPA_European_Heat_Pump_Market_and_Statistics_Report_2015.pdf 
#                                                               and https://www.ehi.eu/fileadmin/user_upload/user_upload/2021-12-03_EHI_Heat_Pump_Report_Final_.pdf


N3 = 70  # 7 distributors (or 1%)
N2 = 40 # 45 distributors (or 1o%)
N1= 15 # 91 distributors (or 20%)
N0= 6 # 311 distributors (or 69%)

n = df_distributor['operating radius'].value_counts(dropna=False).to_list()
print(n)
#print( str( (N3*n[3] + N2*n[2]+N1*n[1] + N0*n[0])*3 ) +   "   employees for German heat pump (installation) sector in 2022")
 






# http://www.wtq-lkk.de/ 45 employees
#https://www.apollo-goessnitz.de/karriere/#:~:text=Mit%20%C3%BCber%20140%20Mitarbeitern%20am,zur%20Produktion%20von%20Systemanlagen%20und 140 employee
# https://www.wer-zu-wem.de/firma/alfred-kaut-co.html 50-100 employees
# assume that company with German-wide op_radius have N3 installation team on average
df_distributor.loc[df_distributor['operating radius'].isna(), 'workforce'] = N3

#  https://www.ait-deutschland.eu/startseite.html > 1000 employees
#  https://www.schrag-kantprofile.de/unternehmen/    500 employees
#  https://die-deutsche-wirtschaft.de/famu_top/otto-schatte-gmbh-luebeck-umsatz-mitarbeiterzahl/ 215 employees
#  https://www.wer-zu-wem.de/firma/elmar-bey.html  44 employees
# https://de.kompass.com/c/alban-technische-anlagen-gmbh/de157795/  20 employees

# assume that all company with op_radius = 150 have N2 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 150, 'workforce'] = N2


# http://www.cube-ing.de/firmenprofil.html#:~:text=Die%20Firma%20besch%C3%A4ftigt%2013%20Mitarbeiter,1%2C5%20Mio. 15 employees
# assume that all company with op_radius = 100 have N1 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 100, 'workforce'] = N1


#  https://de.kompass.com/c/secespol-deutschland-gmbh/de730240/  10-20 employees
# # assume that all company with op_radius = 70 have N0 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 70, 'workforce'] = N0


# #adding variation
# #op_r Germanwide
# rv1 = np.random.normal(0,8,n[3])
# rv1 = rv1.tolist()
# #op_r  150
# rv2 = np.random.normal(0,2,n[2])
# rv2 = rv2.tolist() 
# #op_r  100 
# rv3 = np.random.normal(0,1,n[1])
# rv3 = rv3.tolist()
# #op_r  70
# #rv4 = np.random.normal(1,1,n[0])
# rv4 = np.zeros(n[0])
# rv4 = rv4.tolist()
# rv = rv1+rv2+ rv3 +rv4
# rv =[round(x) for x in rv]

# df_distributor['rv'] = rv
# df_distributor['workforce_rv'] = df_distributor['workforce']+ df_distributor['rv']
# df_distributor.drop(columns='rv',inplace=True)

# 50 weeks/year workweeks. Installation in a team of 2 workers with a capacity of 1 hp/week
df_distributor['max_installations'] = df_distributor['workforce'] * 50 / 2
#df_distributor['max_installations_rv'] = df_distributor['workforce_rv'] * 50 

df_distributor.to_csv(os.path.join(
    dirname, "data-sources/Distributor_data.csv"), index=False)
