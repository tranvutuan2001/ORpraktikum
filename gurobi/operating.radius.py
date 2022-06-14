from this import d
from utilities import get_distance
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from random import sample
from datetime import datetime

dirname = os.path.dirname(__file__)

known_distances = {}  # {(zipcode1, zipcode2): distance}


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
    df['operating radius'] = df['operating radius'].fillna(150)
    df.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)

    df['operating radius'] = df['operating radius'].astype(int)

    for i in tqdm(range(len(df))):
        if i <= round(5*len(df)/100):
            df.iloc[i, df.columns.get_loc('operating radius')] = 800
        elif i <= round(5*len(df)/100) + round(10*len(df)/100):
            df.iloc[i, df.columns.get_loc('operating radius')] = 400
        elif i <= round(20*len(df)/100) + round(5*len(df)/100) + round(10*len(df)/100):
            df.iloc[i, df.columns.get_loc('operating radius')] = 200

    print("Generated operating radius")
    print(round(len(df[df['operating radius'] == 200])/len(df)
          * 100, 2), "% of distributors have operating radius of 200")
    print(round(len(df[df['operating radius'] == 400])/len(df)
          * 100, 2), "% of distributors have operating radius of 400")
    print(round(len(df[df['operating radius'] == 800])/len(df)
          * 100, 2), "% of distributors have operating radius of 800")

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
        'Administrative district').agg({'zipcode': 'first'}).reset_index()

    # get the operating regions for each missing row
    for j in tqdm(df.index):
        i = (len(df)-1) - j  # start at bottom of df
        zipcode = df.loc[i, 'zipcode']
        radius = df.loc[i, 'operating radius']
        if(df.loc[i, 'operating districts'] is None or df.loc[i, 'operating districts'] is np.nan):
            regions = get_operating_districts(
                districts, str(zipcode), radius, sample_size=0.2).keys()
            df.iloc[i, df.columns.get_loc(
                'operating districts')] = ';'.join(regions)

            # missing_operating_regions['operating districts'][i] = np.array([
            #     key for key in regions.keys()], dtype=object)
            df.to_csv(os.path.join(
                dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)

    # save the dataframe
    df.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data_with_radius.csv"), index=False)


def get_operating_districts(districts, zipcode, op_radius=100, timeout=120, max_districts=5, sample_size=1):
    """Find the districts that are within the operating radius of the zipcode.

    Args:
        districts (DataFrame): dataframe of district names and zipcodes
        zipcode (int or str): zipcode of the distributor
        op_radius (int, optional): the operating radius of the distributor. Defaults to 100.
        timeout (int, optional): time in seconds after which the search should stop. Defaults to 120.
        max_districts (int, optional): number of districts in radius after which the search should stop. Defaults to 5.
        sample_size (float, optional): size of the sample from the districts . Defaults to 1.

    Raises:
        Exception: if calculated distance is 0 and zipcodes are not the same

    Returns:
        dict: dictionary of districts and their distances
    """
    # add 0 to zipcode if it is 4 digits
    zipcode = '0'+str(zipcode) if len(str(zipcode)) == 4 else str(zipcode)
    operating_districts = {}  # {district: distance}
    districts = sample(districts.values.tolist(), round(sample_size*len(districts))
                       )  # sample sample_size% of districts

    start = datetime.now()
    for i in tqdm(range(len(districts)), leave=False):
        diff_time = datetime.now() - start  # time since start
        if diff_time.total_seconds() > timeout:  # stop search if execution time is exceeded
            return operating_districts

        district_name, z = districts[i]
        if district_name in operating_districts.keys():
            continue  # skip if already found

        if len(operating_districts.keys()) >= max_districts:
            return operating_districts  # return if max_districts regions found

        zipcode_of_district = '0' + \
            str(z) if len(
                str(z)) == 4 else str(z)  # add 0 to zipcode if only 4 digits

        if zipcode_of_district == zipcode:
            # if zipcode is in district, set distance to 0
            operating_districts[district_name] = 0
            continue

        if (zipcode_of_district, zipcode) in known_distances.keys():  # if distance is already known
            distance = known_distances[(zipcode_of_district, zipcode)]
        elif (zipcode, zipcode_of_district) in known_distances.keys():  # if distance is already known
            distance = known_distances[(zipcode, zipcode_of_district)]
        else:
            # get distance between zipcodes if not known
            distance = get_distance({'postalcode': zipcode, 'country': 'Germany'}, {
                'postalcode': zipcode_of_district, 'country': 'Germany'})
            if distance == 0 and zipcode != zipcode_of_district:
                raise Exception('Distance is 0 for zipcodes: ' +
                                zipcode + ' and ' + zipcode_of_district)  # raise error if distance is 0 and zipcodes are not the same
            if distance is not None:
                known_distances[zipcode_of_district,
                                zipcode] = distance  # save distance
                if distance < op_radius:
                    # add to district if distance is less than op_radius
                    operating_districts[district_name] = distance

    return operating_districts


# add_operating_radius()
add_operating_districts()
