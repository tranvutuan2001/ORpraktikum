
from utilities import get_driving_distance, cal_dist, get_driving_distance_by_coords
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from random import sample
from datetime import datetime

dirname = os.path.dirname(__file__)

known_distances = {}  # {(zipcode1, zipcode2): distance}

# https://www.waermepumpe.de/fachpartnersuche shows distributors in a radius of ~70 km in most cases, so well take that as our default.
# A raduis of None indicates a german-wide range. Those are crucial for our scenario to ensure that we have a good coverage of the districts.


def add_operating_radius(distributor_data_file=None, default_radius=70):
    """Adds the operating radius to the csv file. The radius is set to have a default value of 150km for 65% of the rows. 

    Args:
        origin (str, optional): Location of the original data file. Defaults to None. If None, the file is assumed to be data-sources/Distributor_data.csv
        default_radius (int, optional): The default radius to use. Defaults to 150.
    """
    DISTRIBUTERS_DATA = distributor_data_file if distributor_data_file is not None else os.path.join(
        dirname, "data-sources", "Distributor_data.csv")
    df = pd.read_csv(DISTRIBUTERS_DATA)

    # this will potentially overwrite existing values
    df['operating radius'] = None
    df['operating radius'] = df['operating radius'].fillna(default_radius)

    df.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data.csv"), index=False)

    df['operating radius'] = df['operating radius'].astype(int)

    for i in tqdm(range(len(df))):
        if i <= round(1 * len(df) / 100):
            df.iloc[i, df.columns.get_loc('operating radius')] = None
        elif i <= round(1 * len(df) / 100) + round(10 * len(df) / 100):
            df.iloc[i, df.columns.get_loc('operating radius')] = 150
        elif i <= round(20 * len(df) / 100) + round(1 * len(df) / 100) + round(10 * len(df) / 100):
            df.iloc[i, df.columns.get_loc('operating radius')] = 100

    df.to_csv(os.path.join(
        dirname, "data-sources/Distributor_data.csv"), index=False)

    print("Generated operating radius")
    print_radius_distributions(df)


def add_operating_districts(distributor_data_file=None, districts_file=None, sample_size=0.3, max_districts=None, operating_radius=None):
    """Adds the operating districts to the csv file. The districts are sampled from the list of districts.

    Args:
        distributor_data_file (str, optional): path to the distributor data file. Defaults to None. if None, the file is assumed to be data-sources/Distributor_data_with_radius.csv
        districts_file (str, optional): path to the file contain the districts. Defaults to None. if None, the file is assumed to be data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv
        sample_size (float, optional): sample size between (0,1] for the districts to search in. Defaults to 0.3. Higher values will take longer to run.
        max_districts (int, optional): number of districts in radius after which the search should stop. Defaults to 5. Higher values will take longer to run.
        operating_radius (int, optional): filter distributers by only considering ones with the specified radius. Defaults to None. If None, all distributors are considered.

    Raises:
        Exception: If the distributors data file is not found.
        Exception: If the districts file is not found.
    """

    DISTRIBUTERS_DATA = distributor_data_file if distributor_data_file is not None else os.path.join(
        dirname, "data-sources/Distributor_data.csv")
    ACOOLHEAD = districts_file if districts_file is not None else os.path.join(
        dirname, "data-sources/data_from_Hannah_with_coordinates_and_zipcodes.csv")
    if not os.path.isfile(DISTRIBUTERS_DATA):
        raise Exception(DISTRIBUTERS_DATA, "not found")
    if not os.path.isfile(ACOOLHEAD):
        raise Exception(ACOOLHEAD, "not found")

    df_acoolhead = pd.read_csv(ACOOLHEAD)
    df = pd.read_csv(DISTRIBUTERS_DATA)
    if (not 'operating districts' in df.columns):
        df['operating districts'] = None

    df['operating districts'] = df['operating districts'].astype(
        str)

    df_distributors = df

    if (operating_radius is not None):
        # if operating_radius is set then only work with distributors with that radius
        df_distributors = df[df['operating radius']
                             == operating_radius]

    districts = df_acoolhead[['Administrative district', 'lat', 'long']].groupby(
        'Administrative district').agg({'lat': 'first', 'long': 'first'}).reset_index()

    # get the operating regions for each missing row
    for i in tqdm(df_distributors.index):
        # i = (len(df)-1) - j  # start at bottom of df
        lat = df.loc[i, 'lat']
        lng = df.loc[i, 'long']
        radius = df.loc[i, 'operating radius']

        if np.isnan(radius):
            continue

        regions = get_operating_districts(
            districts,  lat, lng, radius, sample_size=sample_size, max_districts=max_districts)
        df.iloc[i, df.columns.get_loc(
            'operating districts')] = ';'.join(regions)

        df.to_csv(os.path.join(
            dirname, "data-sources/test.csv"), index=False)

    # save the dataframe
    df.to_csv(os.path.join(
        dirname, "data-sources/test.csv"), index=False)
    check_coverage(df, df_acoolhead)


def get_operating_districts(districts, lat, lng, op_radius=100, timeout=120, max_districts=None, sample_size=1):
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
    # # add 0 to zipcode if it is 4 digits
    # zipcode = '0' + str(zipcode) if len(str(zipcode)) == 4 else str(zipcode)
    operating_districts = {}  # {district: distance}
    districts = districts.values.tolist()
    districts = sample(districts, round(sample_size * len(districts))
                       )  # sample sample_size% of districts

    if np.isnan(op_radius):
        return operating_districts.keys()

    start = datetime.now()
    for i in tqdm(range(len(districts)), leave=False):
        diff_time = datetime.now() - start  # time since start
        # if diff_time.total_seconds() > timeout:  # stop search if execution time is exceeded
        #     return operating_districts

        district_name, latitude, longitude = districts[i]
        # if district_name in operating_districts.keys():
        #     continue  # skip if already found

        # if max_districts is not None and len(operating_districts.keys()) >= max_districts:
        #     return operating_districts  # return if max_districts regions found

        # zipcode_of_district = '0' + \
        #                       str(z) if len(
        #                           str(z)) == 4 else str(z)  # add 0 to zipcode if only 4 digits

        if lat == latitude and lng == longitude:
            # if zipcode is in district, set distance to 0
            operating_districts[district_name] = 0
            continue

        if ((lat, lng), (latitude, longitude)) in known_distances.keys():  # if distance is already known
            driving_distance = known_distances[(
                (lat, lng), (latitude, longitude))]
        elif ((latitude, longitude), (lat, lng)) in known_distances.keys():  # if distance is already known
            driving_distance = known_distances[(
                (latitude, longitude), (lat, lng))]
        else:
            # get distance between zipcodes if not known

            # since driving distance takes longer to calculate, we first check if the air distance is less than the operating radius + 70km and only then check the driving distance
            air_distance = cal_dist((lat, lng), (latitude, longitude))
            if air_distance > op_radius + 70:
                continue

            driving_distance = get_driving_distance_by_coords(
                (lat, lng), (latitude, longitude))
            if driving_distance == 0:
                # raise error if distance is 0 and zipcodes are not the same
                raise Exception(
                    'Distance is 0 for different coordinates: ', (lat, lng), (latitude, longitude))
            if driving_distance is not None:
                known_distances[((lat, lng), (latitude, longitude))
                                ] = driving_distance  # save distance
                if driving_distance < op_radius:
                    # add to district if distance is less than op_radius
                    operating_districts[district_name] = driving_distance

    operating_districts = {k: v for k, v in sorted(  # sort by distance
        operating_districts.items(), key=lambda item: item[1])}

    # take the 10 first if operating radius is smaller or equal to 100. Else take the 15 first
    if op_radius <= 100:
        return list(operating_districts.keys())[:10]
    else:
        return list(operating_districts.keys())[:15]


def print_radius_distributions(df):
    """Print the distribution of the dataframe.

    Args:
        df (DataFrame): dataframe to print the distribution of the radius column
    """
    print('Distribution of operating radius:')
    # list of unique operating radius
    unique_radius = df['operating radius'].unique()
    for radius in unique_radius:
        print(
            f"{round(len(df[df['operating radius'] == radius]) / len(df)* 100, 2)}% of distributors have operating radius of {radius}")


def check_coverage(df, df_districts):
    """Checks if how many districts are covered by the distributers that have an operating radius that is not None

    """
    df = df.notna()
    # get the set of all operating districts
    operating_districts = set()
    for i in range(len(df)):
        operating_districts.update(df['operating districts'][i].split(';'))

    # get the unique Administrative districts
    unique_districts = set(df_districts['Administrative District'].unique())
    # missing districts
    missing_districts = unique_districts - operating_districts
    print(f"{len(missing_districts)} districts are not covered by the distributors")


# add_operating_radius()
# add_operating_districts(sample_size=1)
