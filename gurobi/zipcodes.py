from cmath import nan
from utilities import get_zipcode_by_coords
import pandas as pd
import os
import xlwt
from tqdm import tqdm
import numpy as np
dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, "../data-sources/ACoolHeadZipCodes.xls")

# Check if the zipcode is already known


def get_zipcode_from_df(df, i):
    name = df['Administrative district'][i]
    for j in range(len(df['Administrative district'])):
        if df['Administrative district'][j] == name and not df['zipcode'][j] == None:
            return df['zipcode'][j]
    return df['zipcode'][i]


df = pd.read_excel(ACOOLHEAD)

weather_file_col = df['weather file names']
knownzipcodes = {}
df.fillna(value=0, inplace=True)
print(df['zipcode'].eq(0).sum(), "unknown zipcodes")
for i in tqdm(range(len(weather_file_col))):
    if(i % 1000 == 0):
        df.to_excel(os.path.join(
            dirname, "../data-sources/ACoolHeadZipCodes.xls"), index=False)
    if not df['zipcode'][i] == 0:
        # print(df['zipcode'][i])
        continue
    zipcode = get_zipcode_from_df(df, i)
    if zipcode == 0:
        coords = weather_file_col[i].split('_')[1]
        lat = coords[0:2] + '.' + coords[2:6]  # 54.3288
        lng = coords[6:8] + '.' + coords[8:12]  # 10.1350
        if (lat, lng) in knownzipcodes:
            zipcode = knownzipcodes[(lat, lng)]
        else:
            # Get the zipcode from the coordinates by calling the geolocator api. This is a slow process as we need to limit the number of requests to 1 per second.
            zipcode = get_zipcode_by_coords(lat, lng)
            print("\nrequest for zipcode with coordinates: " +
                  str(lat) + " " + str(lng) + " " + str(zipcode))
            df.to_excel(os.path.join(
                dirname, "../data-sources/ACoolHeadZipCodes.xls"), index=False)
            knownzipcodes[(lat, lng)] = zipcode

    df.loc[df['zipcode'][i]] = zipcode
df.to_excel(os.path.join(
            dirname, "../data-sources/ACoolHeadZipCodes.xls"), index=False)
