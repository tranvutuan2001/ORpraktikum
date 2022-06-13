import pandas as pd
import os

dirname = os.path.dirname(__file__)
HEAT_PUMPS = os.path.join(dirname, './data-sources/heat_pumps_air_water_only.csv')


df_hp = pd.read_csv(HEAT_PUMPS)
df_hp_s= df_hp.sort_values(['COP A2/W35','Heat output A2/W35 (kW)'], ascending=[True, True])
df_hp = df_hp_s.iloc[ ::10,:]
df_hp = df_hp.reset_index(drop=True)
#print(df_hp['hp_name'])

# price can't be found
df_hp = df_hp.drop([0,3,10,12])
df_hp = df_hp.append(df_hp_s.iloc[-3])
#df_hp = df_hp.reset_index(drop=True)
df_hp = df_hp.reset_index()

#print(df_hp['hp_name'])


# if there is discount, original price is taken
# https://domotec.ch/wp-content/uploads/2022/06/1.1-pl-allgemein-06.2022-DE.pdf
# https://heizung-billiger.de/69503-stiebel-eltron-luft-wasser-warmepumpe-wpl-09-ikcs-classic-stiebel-236377-4017212363775.html?hbdc=DE&utm_source=guenstiger&utm_medium=cpc&utm_campaign=guenstiger-de
# https://www.heizungsdiscount24.de/waermepumpen/vaillant-versotherm-plus-vwl-775-luft-wasser-waermepumpe.html?gclid=CjwKCAjwnZaVBhA6EiwAVVyv9MQZvSx9QQuF56cGi9y1Cq8h1lNVzaH_q0FYiCaP7LpHmW8Vs_3EeBoCkU4QAvD_BwE&cq_cmp=13242830342&cq_plt=gp&cq_src=google_ads&cq_net=u
# https://domotec.ch/wp-content/uploads/2022/06/1.1-pl-allgemein-06.2022-DE.pdfhttps://domotec.ch/wp-content/uploads/2022/06/1.1-pl-allgemein-06.2022-DE.pdf
# https://www.heizungsdiscount24.de/waermepumpen/vaillant-flexotherm-exclusive-vwf-574-heizungswaermepumpe-solewasser.html?cq_src=google_ads&cq_net=u&cq_cmp=13242830342&cq_plt=gp&gclid=CjwKCAjwnZaVBhA6EiwAVVyv9LDV4ncrTDuayjy2mZ2XWxvqs-T0jg902k_jxM-pgcEy8--TXt17SRoCTbwQAvD_BwE
# https://docplayer.org/82079403-Preisliste-waermepumpen-systeme-der-cta-ag.html
# https://shop.smuk.at/shop/USER_ARTIKEL_HANDLING_AUFRUF.php?Kategorie_ID=9389&Ziel_ID=12271890

price =[13025, 14316.4, 14108.64, 15175, 9930.55, 17005.37, 19104.95, 12066.6,  17983.20, 28680]

# installation + accessories from https://www.energieheld.de/heizung/waermepumpe/kosten
price = [x+3000 for x in price]

df_hp.insert(4, 'Price', price, True)


