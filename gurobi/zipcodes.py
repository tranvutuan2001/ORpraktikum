from utilities import get_zipcode_by_coords
import pandas as pd
import os
import xlwt

dirname = os.path.dirname(__file__)
ACOOLHEAD = os.path.join(dirname, "../data-sources/ACoolHeadAppendix.xlsx")

# Check if the zipcode is already known


def get_zipcode_from_df(df, i):
    name = df['Administrative district'][i]
    for j in range(len(df['Administrative district'])):
        if df['Administrative district'][j] == name and not df['zipcode'][j] == None:
            return df['zipcode'][j]
    return df['zipcode'][i]


df = pd.read_excel(ACOOLHEAD, engine='openpyxl')

weather_file_col = df['weather file names']
zipcodes = [None]*len(weather_file_col)
df['zipcode'] = zipcodes
knownzipcodes = {}
print(df.head())
for i in range(len(weather_file_col)):
    zipcode = get_zipcode_from_df(df, i)
    if zipcode is None:
        coords = weather_file_col[i].split('_')[1]
        lat = coords[0:2] + '.' + coords[2:6]  # 54.3288
        lng = coords[6:8] + '.' + coords[8:12]  # 10.1350
        if (lat, lng) in knownzipcodes:
            zipcode = knownzipcodes[(lat, lng)]
        else:
            # Get the zipcode from the coordinates by calling the geolocator api. This is a slow process as we need to limit the number of requests to 1 per second.
            print("request for zipcode with coordinates: " +
                  str(lat) + " " + str(lng))
            zipcode = get_zipcode_by_coords(lat, lng)
            knownzipcodes[(lat, lng)] = zipcode
            df.to_excel(os.path.join(
                dirname, "../data-sources/ACoolHeadZipCodes.xls"), index=False)
    df['zipcode'][i] = zipcode
df.to_excel(os.path.join(
            dirname, "../data-sources/ACoolHeadZipCodes.xls"), index=False)
