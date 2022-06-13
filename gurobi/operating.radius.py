from utilities import get_distance
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
dirname = os.path.dirname(__file__)

MAX_OPERATING_RADIUS = 90  # in km
distances = {}
known_distances = {}


def add_operating_radius():
    # if file exists, load it
    if os.path.isfile(os.path.join(
            dirname, "data-sources/Distributor_data_with_radius.csv")):
        DISTRIBUTERS_DATA = os.path.join(
            dirname, "data-sources/Distributor_data_with_radius.csv")
        df = pd.read_csv(DISTRIBUTERS_DATA)
        if(not 'operating_regions' in df.columns):
            df['operating_regions'] = None
        # if not, create it from data_from_Hannah_with_coordinates.csv
    else:
        DISTRIBUTERS_DATA = os.path.join(
            dirname, "data-sources/Distributor_data.csv")
        df = pd.read_csv(DISTRIBUTERS_DATA)
        df['operating_regions'] = None
        df['operating_regions'] = df['operating_regions'].astype(object)
        df.to_csv(os.path.join(
            dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)

    df['operating_regions'] = df['operating_regions'].astype(object)
    # get missing operating regions
    missing_operating_regions = df[df['operating_regions'].isna()]
    # get the districts from the ACOOLHEAD data
    ACOOLHEAD = os.path.join(
        dirname, "data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv")

    df_acoolhead = pd.read_csv(ACOOLHEAD)
    districts = df_acoolhead[['Administrative district', 'zipcode']].groupby(
        'Administrative district')

    # get the operating regions for each missing row
    for i in tqdm(missing_operating_regions.index):
        zipcode = missing_operating_regions.loc[i, 'zipcode']
        regions = [key for key in get_operating_regions(
            districts, str(zipcode))]
        df.iloc[i, df.columns.get_loc(
            'operating_regions')] = ';'.join(regions)

        # missing_operating_regions['operating_regions'][i] = np.array([
        #     key for key in regions.keys()], dtype=object)
        df.to_csv(os.path.join(
            dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)

    # save the dataframe
    df.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)


def get_operating_regions(districts, zipcode):
    zipcode = '0'+str(zipcode) if len(str(zipcode)) == 4 else str(zipcode)
    regions = {}

    # get the distance between the zipcode and each district
    for district, zipcodes in districts.groups.items():
        zipcode_of_district = '0' + \
            str(zipcodes[0]) if len(
                str(zipcodes[0])) == 4 else str(zipcodes[0])
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

        if not distance == None and distance < MAX_OPERATING_RADIUS:
            regions[district] = distance

    return regions


add_operating_radius()
