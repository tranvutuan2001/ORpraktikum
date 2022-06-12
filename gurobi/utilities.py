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


def get_distance(origin, destination):
    """
    Calculates the distance between two locations using the OSMR API.
    :param origin: The origin location (e.g. "London, UK")
    :param destination: The destination location (e.g. "New York, US")
    :return: The distance between the two locations (in km)
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
                0]['distance']/1000  # convert to km
            time.sleep(1)
            return distance
        raise Exception("No routes found")
    raise Exception(f"Error: {r.status_code}")


def get_zipcode(location):
    lat, lng = get_coordinates(location)
    if lat is None or lng is None:
        return None
    location = geolocator.reverse((lat, lng))
    time.sleep(1)
    return location.raw['address']['postcode']


def get_zipcode_by_coords(lat, lng):
    location = geolocator.reverse((lat, lng))
    time.sleep(1)
    if location is None or not 'postcode' in location.raw['address']:
        return 0
    return location.raw['address']['postcode']

def get_coordinates(location):
    """
    Gets the coordinates of a location using the OSMR API.
    :param location: The location (e.g. "London, UK")
    :return: The latitude and longitude of the location
    """

    # Get the coordinates of the location
    location = geolocator.geocode(location)
    time.sleep(1)
    if location is None:
        return None, None

    lat = location.latitude
    lng = location.longitude

    return lat, lng


# source = "Aachen"
# destination = "Luxembourg"

# distance = get_distance(source, destination)
# print(
#     f'By car, you need to travel {distance} km from {source} to {destination}.')

# print(f"Weather in {source}: ", get_weather_data(source)['main']['temp'], "°C")

# print(f"Zip code for {source}: ", get_zipcode(source))

# print(get_distance({'postalcode': '88279', 'country': 'Germany'}, {
#     'postalcode': '01067', 'country': 'Germany'}))
