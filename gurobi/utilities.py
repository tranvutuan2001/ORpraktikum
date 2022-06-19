import requests
import time
from geopy import geocoders
import json

geolocator = geocoders.Nominatim(user_agent="ORLab")
OPEN_WEATHERMAP_API_KEY = "665ae88c4680cd60d0dd1bb22b151a75"


def get_weather_data(city):
    """
    Gets the weather data for a location using the OpenWeatherMap API.
    :param city: The location (e.g. "London, UK")
    :return: The weather data for the location  (e.g. "{'coord': {'lon': 6.0827, 'lat': 50.7759},
                                                        'weather': [{'id': 801, 'main': 'Clouds', 'description': 'few clouds', 'icon': '02d'}],
                                                        'base': 'stations', 
                                                        'main': {'temp': 19.48, 'feels_like': 19.13, 'temp_min': 16.59, 'temp_max': 22.19, 'pressure': 1016, 'humidity': 63},
                                                        'visibility': 10000,
                                                        'wind': {'speed': 2.23, 'deg': 30, 'gust': 2.04},
                                                        'clouds': {'all': 11}, 
                                                        'dt': 1655280324, 
                                                        'sys': {'type': 2, 'id': 2013497, 'country': 'DE', 'sunrise': 1655263317, 'sunset': 1655322623},
                                                        'timezone': 7200,
                                                        'id': 3247449, 
                                                        'name': 'Aachen',
                                                        'cod': 200
                                                        }")
    """

    lat, lng = get_coordinates(city)

    # Get the weather data for the location
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&units=metric&appid={OPEN_WEATHERMAP_API_KEY}"
    r = requests.get(url)
    time.sleep(1)
    if r.status_code == 200:
        weather_data = json.loads(r.content)
        return weather_data
    raise Exception(f"Error: {r.status_code}")


def get_driving_distance(origin, destination):
    """
    Calculates the distance between two locations using the OSMR API. 
    :param origin: The origin location (e.g. "London, UK")
    :param destination: The destination location (e.g. "New York, US")
    :return: The distance between the two locations (in km)
    Examples:
        - get_distance({'postalcode': '88279', 'country': 'Germany'}, {
               'postalcode': '01067', 'country': 'Germany'})
        - get_distance("Aachen", "Luxembourg")
    """

    # Get the coordinates of the origin and destination
    origin_coords = get_coordinates(origin)
    destination_coords = get_coordinates(destination)

    origin_lat, origin_lng = origin_coords
    destination_lat, destination_lng = destination_coords

    if origin_lat is None or origin_lng is None or destination_lat is None or destination_lng is None:
        return None
    coordinates = f'{origin_lng},{origin_lat};{destination_lng},{destination_lat}'
    r = requests.get(
        f"http://router.project-osrm.org/route/v1/driving/{coordinates}?overview=false""")
    if r.status_code == 200:
        routes = json.loads(r.content)
        if len(routes.get('routes')) > 0:
            distance = routes.get("routes")[
                           0]['distance'] / 1000  # convert to km
            time.sleep(1)
            return distance
        raise Exception("No routes found")
    raise Exception(f"Error: {r.status_code}")


def get_zipcode(location):
    """Get the zip code from a location

    Args:
        location: The location either a tuple of (lat, lng) or a string of the location name

    Returns:
        float: the zipcode of the location
    Examples:
        - get_zipcode("London, UK")
    """
    if type(location) is tuple:
        lat, lng = location
    else:
        lat, lng = get_coordinates(location)
    if lat is None or lng is None:
        return None
    location = geolocator.reverse((lat, lng))
    time.sleep(1)
    return location.raw['address']['postcode']


def get_coordinates(location):
    """
    Gets the coordinates of a location using the OSMR API.
    :param location: The location (e.g. "London, UK")
    :return: The latitude and longitude of the location
    """

    try:
        location = geolocator.geocode(location)
    except:
        return None, None
    time.sleep(1)
    if location is None:
        return None, None

    return location.latitude, location.longitude


from math import radians, cos, sin, asin, sqrt

# from https://www.geeksforgeeks.org/program-distance-two-points-earth/#:~:text=For%20this%20divide%20the%20values,is%20the%20radius%20of%20Earth.
def distance(lat1, lat2, lon1, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return c * r


def cal_dist(x1, x2):
    lat_x1 = x1[0]
    long_x1 = x1[1]
    lat_x2 = x2[0]
    long_x2 = x2[1]
    result = distance(lat_x1, lat_x2, long_x1, long_x2)
    return result
