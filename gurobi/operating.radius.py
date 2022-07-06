
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
        dirname, "data-sources/HOUSING.csv")
    if not os.path.isfile(DISTRIBUTERS_DATA):
        raise Exception(DISTRIBUTERS_DATA, "not found")
    if not os.path.isfile(ACOOLHEAD):
        raise Exception(ACOOLHEAD, "not found")

    df_acoolhead = pd.read_csv(ACOOLHEAD)
    df_distributors = pd.read_csv(DISTRIBUTERS_DATA)
    if (not 'operating districts' in df_distributors.columns):
        df_distributors['operating districts'] = None

    df_distributors['operating districts'] = df_distributors['operating districts'].astype(
        str)

    if (operating_radius is not None):
        # if operating_radius is set then only work with distributors with that radius
        df_distributors = df_distributors[df_distributors['operating radius']
                             == operating_radius]

    districts = df_acoolhead[['zipcode', 'lat', 'long']].groupby(
        'zipcode').agg({'lat': 'first', 'long': 'first'}).reset_index()

    # get the operating regions for each missing row
    # check_coverage(districts, df_acoolhead)
    for i in tqdm(range(len(df_distributors))):
        # i = (len(df)-1) - j  # start at bottom of df
        lat = df_distributors.loc[i, 'lat']
        lng = df_distributors.loc[i, 'long']
        radius = df_distributors.loc[i, 'operating radius']

        if np.isnan(radius):
            continue

        regions = get_operating_districts(
            districts,  lat, lng, radius, sample_size=sample_size, max_districts=max_districts)
        
        df_distributors.iloc[i, df_distributors.columns.get_loc(
            'operating districts')] = ';'.join(regions)

        df_distributors.to_csv(os.path.join(
            dirname, "data-sources", "Distributor_data.csv"), index=False)

    # save the dataframe
    check_coverage(df_distributors, df_acoolhead)
    df_distributors.to_csv(os.path.join(
        dirname, "data-sources", "Distributor_data.csv"), index=False)


def get_operating_districts(districts, distributor_latitude, distributor_longitude, op_radius=100, timeout=None, max_districts=None, sample_size=1):
    """Find the districts that are within the operating radius of the zipcode.

    Args:
        districts (DataFrame): dataframe of district names and zipcodes
        distributor_latitude (float): latitude of the distributor
        distributor_longitude (float): longitude of the distributor	
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
    if sample_size < 1:
        # sample sample_size% of districts
        districts = sample(districts, round(sample_size * len(districts)))

    if np.isnan(op_radius):
        return []

    start = datetime.now()
    for i in tqdm(range(len(districts)), leave=False):
        diff_time = datetime.now() - start  # time since start
        if timeout is not None and diff_time.total_seconds() > timeout:  # stop search if execution time is exceeded
            return operating_districts

        zipcode, latitude, longitude = districts[i]
        zipcode = str(int(zipcode))

        if max_districts is not None and len(operating_districts.keys()) >= max_districts:
            return operating_districts  # return if max_districts regions found

        # zipcode_of_district = '0' + \
        #                       str(z) if len(
        #                           str(z)) == 4 else str(z)  # add 0 to zipcode if only 4 digits

        if distributor_latitude == latitude and distributor_longitude == longitude:
            # if zipcode is in district, set distance to 0
            operating_districts[zipcode] = 0
            continue

        if ((distributor_latitude, distributor_longitude), (latitude, longitude)) in known_distances.keys():  # if distance is already known
            driving_distance = known_distances[(
                (distributor_latitude, distributor_longitude), (latitude, longitude))]
        elif ((latitude, longitude), (distributor_latitude, distributor_longitude)) in known_distances.keys():  # if distance is already known
            driving_distance = known_distances[(
                (latitude, longitude), (distributor_latitude, distributor_longitude))]
        else:
            # get distance between zipcodes if not known

            # since driving distance takes longer to calculate, we first check if the air distance is less than the operating radius + 70km and only then check the driving distance
            air_distance = cal_dist((distributor_latitude, distributor_longitude), (latitude, longitude))
            if air_distance > op_radius + 70:
                continue

            driving_distance = get_driving_distance_by_coords(
                (distributor_latitude, distributor_longitude), (latitude, longitude))
            # commented out because in some cases the driving distance is 0 for coordinates that are only slightly different
            # if driving_distance == 0:
            #     # raise error if distance is 0 and zipcodes are not the same
            #     raise Exception(
            #         'Distance is 0 for different coordinates: ', (lat, lng), (latitude, longitude))
            if driving_distance is not None:
                known_distances[((distributor_latitude, distributor_longitude), (latitude, longitude))
                                ] = driving_distance  # save distance
                if driving_distance < op_radius:
                    # add to district if distance is less than op_radius
                    operating_districts[zipcode] = driving_distance

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


def prepend_zipcodes():
    """ Ajusts the zipcode column to have zipcodes of lenght 5.
    The ones with lenght 4 get a 0 prepended (e.g. 8056->08056)
    """
    df = pd.read_csv(os.path.join(dirname, "data-sources", "HOUSING.csv"))
    df['zipcode'] = df['zipcode'].astype(str)
    df['zipcode'] = df['zipcode'].apply(
        lambda x: '0' + x if len(x) == 4 else x)

    print(df['zipcode'].apply(lambda x: len(str(x)) < 5).sum())
    assert df['zipcode'].apply(lambda x: len(str(x)) < 5).sum(
    ) == 0, 'Some zipcodes are not of lenght 5'

    df.to_csv(os.path.join(dirname, "data-sources", "HOUSING.csv"), index=False)

    # check the csv if all zipcode are of lenght 5#
    df = pd.read_csv(os.path.join(dirname, "data-sources", "HOUSING.csv"))
    print(df['zipcode'].apply(lambda x: len(str(x)) < 5).sum())
    assert df['zipcode'].apply(lambda x: len(str(x)) < 5).sum(
    ) == 0, 'Some zipcodes are not of lenght 5'


def create_distance_matrix():
    DISTRIBUTERS = os.path.join(
        dirname, "data-sources/Distributor_data.csv")
    HOUSING = os.path.join(
        dirname, "data-sources/HOUSING.csv")

    if not os.path.isfile(DISTRIBUTERS):
        raise Exception(DISTRIBUTERS, "not found")
    if not os.path.isfile(HOUSING):
        raise Exception(HOUSING, "not found")

    df_housing = pd.read_csv(HOUSING)
    df_distributors = pd.read_csv(DISTRIBUTERS)

    housing = df_housing[['zipcode', 'lat', 'long']].groupby(
        'zipcode').agg({'lat': 'first', 'long': 'first'})

    distances = {}  # distances for each distributor to each housing

    for i in tqdm(range(len(df_distributors))):
        # get the lat, long from the distributor
        distributor_lat = df_distributors['lat'][i]
        distributor_lng = df_distributors['long'][i]
        distributor_zipcode = df_distributors['zipcode'][i]
        op_radius = df_distributors['operating radius'][i]

        for j in tqdm(range(len(housing)), leave=False):
            # get the lat, long from the housing
            lat_housing = df_housing['lat'][j]
            lng_housing = df_housing['long'][j]

            if not distributor_zipcode in distances:
                distances[distributor_zipcode] = []
            housing_zipcode = df_housing['zipcode'][j]
            # get index in housing_names
            # index = housing_names.index(housing_name)

            air_distance = cal_dist(
                (distributor_lat, distributor_lng), (lat_housing, lng_housing))
            if air_distance > op_radius + 100:
                distances[distributor_zipcode].append(None)
                continue

            try:
                driving_distance = get_driving_distance_by_coords(
                    (distributor_lat, distributor_lng), (lat_housing, lng_housing))
                distances[distributor_zipcode].append(driving_distance)
            except:
                distances[distributor_zipcode].append(None)

    df = pd.DataFrame(distances, index=list(
        housing['lat'].keys()))

    df.head()
    df.to_csv(os.path.join(dirname, "data-sources", "DISTANCES.csv"))


# add_operating_radius()
# prepend_zipcodes()
# add_operating_districts(sample_size=1)
# create_distance_matrix()
