from utilities import get_distance
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
dirname = os.path.dirname(__file__)

MAX_OPERATING_RADIUS = 100  # in km
distances = {}
known_distances = {}


def add_operating_radius():
    # if file exists, load it
    # # if os.path.isfile(os.path.join(
    # #         dirname, "data-sources/Distributor_data_with_radius.csv")):
    # #     DISTRIBUTERS_DATA = os.path.join(
    # #         dirname, "data-sources/Distributor_data_with_radius.csv")
    # #     df = pd.read_csv(DISTRIBUTERS_DATA)
    # #     if(not 'operating radius' in df.columns):
    # #         df['operating radius'] = None
    # #     # if not, create it from data_from_Hannah_with_coordinates.csv
    # else:
    DISTRIBUTERS_DATA = os.path.join(
        dirname, "data-sources/Distributor_data.csv")
    df = pd.read_csv(DISTRIBUTERS_DATA)
    df['operating radius'] = None
    df['operating radius'] = df['operating radius'].fillna(0)
    df.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)

    df['operating radius'] = df['operating radius'].astype(int)

    for i in tqdm(range(len(df))):
        df.iloc[i, df.columns.get_loc('operating radius')] = 100

    df.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)


def add_operating_districts():
    # if file exists, load it
    if os.path.isfile(os.path.join(
            dirname, "data-sources/Distributor_data_with_radius.csv")):
        DISTRIBUTERS_DATA = os.path.join(
            dirname, "data-sources/Distributor_data_with_radius.csv")
        df = pd.read_csv(DISTRIBUTERS_DATA)
        if(not 'operating districts' in df.columns):
            df['operating districts'] = None
        # if not, create it from data_from_Hannah_with_coordinates.csv
    else:
        raise Exception("Distributor_data_with_radius.csv not found")

    df['operating districts'] = df['operating districts'].astype(object)
    # get missing operating regions

    # get the districts from the ACOOLHEAD data
    ACOOLHEAD = os.path.join(
        dirname, "data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv")

    df_acoolhead = pd.read_csv(ACOOLHEAD)
    districts = df_acoolhead[['Administrative district', 'zipcode']].groupby(
        'Administrative district')

    # get the operating regions for each missing row
    for i in tqdm(df.index):
        zipcode = df.loc[i, 'zipcode']
        radius = df.loc[i, 'operating radius']
        regions = [key for key in get_operating_districts(
            districts, str(zipcode), radius).keys()]
        df.iloc[i, df.columns.get_loc(
            'operating districts')] = ';'.join(regions)

        # missing_operating_regions['operating districts'][i] = np.array([
        #     key for key in regions.keys()], dtype=object)
        df.to_csv(os.path.join(
            dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)

    # save the dataframe
    df.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)


def get_operating_districts(districts, zipcode, op_radius=MAX_OPERATING_RADIUS):
    zipcode = '0'+str(zipcode) if len(str(zipcode)) == 4 else str(zipcode)
    regions = {}

    # get the distance between the zipcode and each district
    for district, zipcodes in districts.groups.items():
        zipcode_of_district = '0' + \
            str(zipcodes[0]) if len(
                str(zipcodes[0])) == 4 else str(zipcodes[0])

        if op_radius > 700:
            regions[district] = 1

        if zipcode_of_district == zipcode:
            regions[district] = 0
            continue
        if zipcode_of_district[0] != zipcode[0]:
            continue
        if district in regions.keys():
            continue
        if zipcode_of_district[:3] != zipcode[:3]:
            continue

        if (zipcode_of_district, zipcode) in known_distances.keys():
            distance = known_distances[(zipcode_of_district, zipcode)]
        elif (zipcode, zipcode_of_district) in known_distances.keys():
            distance = known_distances[(zipcode, zipcode_of_district)]
        else:
            distance = get_distance({'postalcode': zipcode, 'country': 'Germany'}, {
                'postalcode': zipcode_of_district, 'country': 'Germany'})
            known_distances[zipcode_of_district, zipcode] = distance

            if not distance == None and distance < op_radius:
                regions[district] = distance

    return regions


# add_operating_radius()
add_operating_districts()
