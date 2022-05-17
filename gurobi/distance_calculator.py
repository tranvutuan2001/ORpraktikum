import requests
from geopy import geocoders
import json

geolocator = geocoders.Nominatim(user_agent="ORLab")


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
    coordinates = f'{origin_lng},{origin_lat};{destination_lng},{destination_lat}'
    print(coordinates)
    r = requests.get(
        f"http://router.project-osrm.org/route/v1/car/{coordinates}?overview=false""")

    if r.status_code == 200:
        routes = json.loads(r.content)
        if len(routes.get('routes')) > 0:
            distance = routes.get("routes")[
                0]['distance']/1000  # convert to km
            return distance
        raise Exception("No routes found")
    raise Exception(f"Error: {r.status_code}")


def get_coordinates(location):
    """
    Gets the coordinates of a location using the OSMR API.
    :param location: The location (e.g. "London, UK")
    :return: The latitude and longitude of the location
    """

    # Get the coordinates of the location
    location = geolocator.geocode(location)
    lat = location.latitude
    lng = location.longitude

    return lat, lng


source = "London"
destination = "Luxembourg"
distance = get_distance(source, destination)
print(
    f'By car, you need to travel {distance} km from {source} to {destination}.')
