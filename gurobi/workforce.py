import pandas as pd
import numpy as np
import os


dirname = os.path.dirname(__file__)
DISTRIBUTOR = os.path.join(dirname, './data-sources/Distributor_data_with_coordinates.csv')
df_distributor = pd.read_csv(DISTRIBUTOR)

# based on this https://www.isoenergy.co.uk/latest-news/renewable-energy-news-from-isoenergy/how-long-will-it-take-to-have-a-heat-pump- 
# installed#:~:text=A%20domestic%20air%20source%20heat,setting%20the%20system%20to%20work.
# We assume that  the installation performed by 2 plumbers, 1 eletrician in the first week and then 2 tester in the second week. 


#realistic assumption, however it takes more than T =60 years and can still not reach min_PERCENTAGE = 0.005 (model infeasible)
# N3 = 15
# N2 = 6
# N1= 2
# N0= 1

# minimum number of teams to make model with T =12, min_PERCENTAGE = 0.05 feasible, 
# but assumption is not realistic, since in total there should be only 5000 employees of heat pump sector in total
N3= N2 =N1= N0 = 95



# those company can have 20 - 1000 employees, see
# https://de.kompass.com/c/alban-technische-anlagen-gmbh/de157795/  
# https://www.schrag-kantprofile.de/unternehmen/    
# https://www.google.com/search?q=ait-deutschland+gmbh+mitarbeiter&sxsrf=ALiCzsZYKI-VLqM9_DSU13d9kXqeHV8R3w%3A1656279667118&ei=c9K4YqvoBqDc7_UP0YycqAY&oq=ait-deutschland+gmbh+mitar&gs_lcp=Cgdnd3Mtd2l6EAMYADIFCCEQoAEyBQghEKABMgUIIRCgAToHCAAQRxCwAzoECCMQJzoGCAAQHhAWOggIABAeEA8QFkoECEEYAEoECEYYAFCjBFjhC2CJEWgBcAF4AIABX4gBiAOSAQE2mAEAoAEByAEIwAEB&sclient=gws-wiz
# assume that they have N3 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 800, 'workforce'] = N3

#based on this  https://www.wer-zu-wem.de/firma/elmar-bey.html  44 employees
# assume that all company with op_radius = 400 have N2 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 400, 'workforce'] = N2

# based on this http://www.cube-ing.de/firmenprofil.html#:~:text=Die%20Firma%20besch%C3%A4ftigt%2013%20Mitarbeiter,1%2C5%20Mio. 15 employees
# assume that all company with op_radius = 200 have N1 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 200, 'workforce'] = N1

# assume that all company with op_radius = 150 have N0 installation team on average
df_distributor.loc[df_distributor['operating radius'] == 150, 'workforce'] = N0


#adding variation
n = df_distributor['operating radius'].value_counts().to_list()
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