from utilities import get_zipcode
import pandas as pd
import os
from tqdm import tqdm
dirname = os.path.dirname(__file__)

# Check if the zipcode is already known


def get_zipcode_from_df(df, i):
    # There are duplicate district names in the dataframe.
    # Thus we can check if the zipcode is already known, since the zipcode will be the same.
    name = df['Administrative district'][i]
    for j in range(len(df['Administrative district'])):
        if df['Administrative district'][j] == name and df['zipcode'][j] != None and df['zipcode'][j] != 0:
            return df['zipcode'][j]
    return 0


def add_zipcodes_to_csv():
    """
    Add zipcodes to the csv file.
    The csv is assumed to have the column "long" which contains the longitude and "lat" which contains the latitude
    It uses these coordinates to get the zipcode from the Nominatim API.
    """
    knownzipcodes = {}  # zipcode for lat and lng that are known

    # if file exists, load it
    if os.path.isfile(os.path.join(
            dirname, "data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv")):
        ACOOLHEAD = os.path.join(
            dirname, "data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv")
        df = pd.read_csv(ACOOLHEAD)
        if(not 'zipcode' in df.columns):
            df['zipcode'] = None
    # if not, create it from data_from_Hannah_with_coordinates.csv
    else:
        ACOOLHEAD = os.path.join(
            dirname, "data-sources\data_from_Hannah_with_coordinates.csv")
        df = pd.read_csv(ACOOLHEAD)
        df['zipcode'] = None
        df.to_csv(os.path.join(
            dirname, "data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv"))

    # fill all null values with 0
    df['zipcode'] = df['zipcode'].fillna(value=0)

    if df['zipcode'].eq(0).sum() == 0:  # if all zipcodes are known
        print("No missing zipcodes")
        return

    print(str(df['zipcode'].eq(0).sum()) + " missing zipcodes")
    change_count = 0  # number of changes made
    last_save = 0  # the last time the csv was saved
    # get the zipcode for each missing row
    for i in tqdm(df[df['zipcode'].eq(0)].index):
        # save the csv every 100 changes
        if(change_count % 100 == 0 and change_count != last_save):
            last_save = change_count
            df.to_csv(os.path.join(
                dirname, "data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv"), index=False)
        # check if the zipcode is unknown.
        if df['zipcode'][i] == 0:
            # get the zipcode from the dataframe
            zipcode = get_zipcode_from_df(df, i)
            if zipcode == 0:  # if the zipcode is unknown
                lng = df['long'][i]  # get the longitude
                lat = df['lat'][i]  # get the latitude
                if lng == 0 or lat == 0:  # if the longitude or latitude is unknown
                    raise Exception(
                        "No longitude or latitude for row " + str(i))

                if (lat, lng) in knownzipcodes:  # if the coordinates are already known in the dictionary
                    zipcode = knownzipcodes[(lat, lng)]
                else:
                    # Get the zipcode from the coordinates by calling the geolocator api.
                    # This is a slow process as we need to limit the number of requests to 1 per second.
                    zipcode = get_zipcode((lat, lng))
                    if zipcode != None and zipcode != 0:
                        knownzipcodes[(lat, lng)] = zipcode
                    else:
                        continue  # if the zipcode is unknown, continue to the next row

            # update the zipcode in the dataframe
            df.iat[i, df.columns.get_loc('zipcode')] = zipcode
            change_count += 1
    print("Done filling in zipcodes")
    df.to_csv(os.path.join(
        dirname, "data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv"), index=False)  # save the csv
    # there might be some zipcodes that are still 0
    # missing_zipcodes = df[df['zipcode'].eq(0)].drop_duplicates()
    # print(str(missing_zipcodes.sum()) +
    #       " zipcodes could not be found")
    # print(missing_zipcodes)


def add_coordinates_to_csv():
    """
    Add longitude and latitude to the csv.
    The csv is assumed to have the column "weather file name" which contains the longitude and latitude in the form:
        DATASET_longitudelatitude_*
        e.g. TRY2015_543288101350_Jahr_City_Kiel
    """
    # ckeck if file exists
    if os.path.isfile(os.path.join(
            dirname, "data-sources/data_from_Hannah_with_coordinates.csv")):
        ACOOLHEAD = os.path.join(
            dirname, "data-sources/data_from_Hannah_with_coordinates.csv")
        df = pd.read_csv(ACOOLHEAD)
        if(not 'long' in df.columns):
            df['long'] = None  # add longitude column
        if(not 'lat' in df.columns):
            df['lat'] = None  # add latitude column
    else:
        raise Exception("No data file found")

    # fill all null values with 0
    df['lat'] = df['lat'].fillna(value=0)
    df['long'] = df['long'].fillna(value=0)

    # if all coordinates are known
    if df['lat'].eq(0).sum() == 0 and df['long'].eq(0).sum() == 0:
        print("No missing latitudes or longitudes")
        return

    print(str(df['lat'].eq(0).sum()) + " latitudes missing")
    print(str(df['long'].eq(0).sum()) + " longitudes missing")

    change_count = 0  # number of changes made
    last_save = 0  # the last time the csv was saved
    # get the lat and long for each missing row
    for i in tqdm(df[df['lat'].eq(0)].index):
        # save the dataframe every 100 changes
        if(change_count % 100 == 0 and change_count != last_save):
            last_save = change_count
            df.to_csv(os.path.join(
                dirname, "data-sources/data_from_Hannah_with_coordinates.csv"), index=False)
        # get the coordinates from the weather file name column
        coords = df['weather file names'][i].split(
            '_')[1]  # will be smth like 543288101350
        lat = coords[0:2] + '.' + coords[2:6]  # will be smth like 54.3288
        lng = coords[6:8] + '.' + coords[8:12]  # will be smth like 10.1350
        df.iat[i, df.columns.get_loc('lat')] = lat
        df.iat[i, df.columns.get_loc('long')] = lng
        change_count += 1
    print("Done filling in latitudes")

    # now do the same for longitudes. Although they should be filled in already, we do it again just to be sure
    change_count = 0
    last_save = 0
    for i in tqdm(df[df['long'].eq(0)].index):
        if(change_count % 100 == 0 and change_count != last_save):
            last_save = change_count
            df.to_csv(os.path.join(
                dirname, "data-sources/data_from_Hannah_with_coordinates.csv"), index=False)
        if not df['long'][i] == 0:
            continue
        coords = df['weather file names'][i].split('_')[1]
        # lat = coords[0:2] + '.' + coords[2:6]  # 54.3288
        lng = coords[6:8] + '.' + coords[8:12]  # 10.1350
        df.iat[i, df.columns.get_loc('long')] = lng
        change_count += 1
    print("Done filling in longitudes")

    df.to_csv(os.path.join(
        dirname, "data-sources/data_from_Hannah_with_coordinates.csv"), index=False)
    # assert that all latitudes are filled in
    assert df['lat'].eq(0).sum() == 0
    # assert that all longitudes are filled in
    assert df['long'].eq(0).sum() == 0


add_coordinates_to_csv()
add_zipcodes_to_csv()
