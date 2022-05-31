from utilities import get_zipcode_by_coords
import pandas as pd
import os

dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, "../data-sources/ACoolHeadAppendix.xlsx")

df = pd.read_excel(ACOOLHEAD, engine='openpyxl')

weather_file_col = df['weather file names']

for i in range(len(weather_file_col)):
    coords = weather_file_col[i].split('_')[1]
    lat = coords[0:2] + '.' + coords[2:6]  # 54.3288
    lng = coords[6:8] + '.' + coords[8:12]  # 10.1350
    print(get_zipcode_by_coords(lat, lng))
