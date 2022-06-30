import pandas as pd
import numpy as np
import os


dirname = os.path.dirname(__file__)
DISTRIBUTOR = os.path.join(dirname, './data-sources/Distributor_data.csv')
df_distributor = pd.read_csv(DISTRIBUTOR)

# based on this https://www.isoenergy.co.uk/latest-news/renewable-energy-news-from-isoenergy/how-long-will-it-take-to-have-a-heat-pump- 
# installed#:~:text=A%20domestic%20air%20source%20heat,setting%20the%20system%20to%20work.
# We assume that  the installation performed by 2 plumbers, 1 eletrician in the first week and then 2 tester in the second week. 


#realistic assumption, however it takes more than T = 100 years and can still not reach min_PERCENTAGE = 0.005 (model infeasible)
# N3 = 40
# N2 = 10
# N1= 4
# N0= 3

# # minimum number of teams to make model with T =12, min_PERCENTAGE = 0.05 feasible, 
# # however, this assumption is not realistic, since in total there should be only < 6000 employees of heat pump sector.
N3= N2 =N1= N0 = 95




 
  
# 


# http://www.wtq-lkk.de/ 45 employees
#https://www.apollo-goessnitz.de/karriere/#:~:text=Mit%20%C3%BCber%20140%20Mitarbeitern%20am,zur%20Produktion%20von%20Systemanlagen%20und 140 employee
# https://www.wer-zu-wem.de/firma/alfred-kaut-co.html 50-100 employees
# assume that company with German-wide op_radius have N3 installation team on average
df_distributor.loc[df_distributor['operating radius'].isna(), 'workforce'] = N3

#  https://www.ait-deutschland.eu/startseite.html > 1000 employees
#  https://die-deutsche-wirtschaft.de/famu_top/otto-schatte-gmbh-luebeck-umsatz-mitarbeiterzahl/ 215 employees
#  https://www.wer-zu-wem.de/firma/elmar-bey.html  44 employees
#  https://www.schrag-kantprofile.de/unternehmen/    500 employees
# https://de.kompass.com/c/alban-technische-anlagen-gmbh/de157795/  20 employees

# assume that all company with op_radius = 150 have N2 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 150, 'workforce'] = N2


# http://www.cube-ing.de/firmenprofil.html#:~:text=Die%20Firma%20besch%C3%A4ftigt%2013%20Mitarbeiter,1%2C5%20Mio. 15 employees
# assume that all company with op_radius = 100 have N1 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 100, 'workforce'] = N1


#  https://de.kompass.com/c/secespol-deutschland-gmbh/de730240/  10-20 employees
# # assume that all company with op_radius = 150 have N0 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 70, 'workforce'] = N0


#adding variation
n = df_distributor['operating radius'].value_counts(dropna=False).to_list()
print(n)


print( str( (N3*n[3] + N2*n[2]+N1*n[1] + N0*n[0])*5 ) +   "   employees for German heat pump (installation) sector")





#op_r = 800 
rv1 = np.random.normal(0,8,n[3])
rv1 = rv1.tolist()
#op_r = 400 
rv2 = np.random.normal(0,2,n[2])
rv2 = rv2.tolist() 
#op_r = 200 
rv3 = np.random.normal(0,1,n[1])
rv3 = rv3.tolist()
#op_r = 150 
#rv4 = np.random.normal(1,1,n[0])
rv4 = np.zeros(n[0])
rv4 = rv4.tolist()
rv = rv1+rv2+ rv3 +rv4
rv =[round(x) for x in rv]

df_distributor['rv'] = rv
df_distributor['workforce_rv'] = df_distributor['workforce']+ df_distributor['rv']
df_distributor.drop(columns='rv',inplace=True)
# 50 week /year  for work
df_distributor['max_installations'] = df_distributor['workforce'] * 50 
df_distributor['max_installations_rv'] = df_distributor['workforce_rv'] * 50 

df_distributor.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data_with_workforce.csv"), index=False)