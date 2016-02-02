import requests
import ast
from key import sabre_api_key as sabre_key
# from views import getNearestAirport
import json
import random
from datetime import datetime
from geopy.distance import vincenty


def go_nearby():
    pass

def getNearestAirport(lat, lon):
    airson = json.loads(open('../airports.json').read())
    nearest_airport = None
    nearest_measure = 320000
    for airport in airson:
        if not airport.has_key('lat') and not airport.has_key('lon') or (airport.has_key('size') and airport['size']!='large'):
            continue
        distance = vincenty((lat,lon),(airport['lat'],airport['lon']))
        if distance < nearest_measure:
            nearest_measure = distance
            nearest_airport = airport

    return nearest_airport


def authenticate():
    url = "https://api.test.sabre.com" + "/v2/auth/token"

    payload = {
        'grant_type': "client_credentials",
    }

    headers = {
        'Authorization': "Basic " + sabre_key,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    r = requests.post(url, data=payload, headers=headers)

    return ast.literal_eval(r.text)


def get_min_fare(source, destination, token):
    url = "https://api.test.sabre.com/v2/shop/flights/fares?origin=%s&destination=%s&departuredate=%s&lengthofstay=15"
    url = url % (source, destination, str(datetime.now().date()))

    print url
    res = requests.get(url, headers={ 'Authorization': 'Bearer ' + token})

    di = ast.literal_eval(res.text)

    print di
    cost = di['FareInfo'][0]['LowestFare']['Fare']
    return cost


def places_to_visit(location, price):
    """
    :param location: coordinates
    :param price: Total Money that the use can spend
    :return: flight Cost of the cheapest (top) destination the user could visit
    """
    url = "https://api.test.sabre.com/v1/lists/top/destinations?origin=%s&lookbackweeks=2&topdestinations=5&destinationtype=International"
    lat, longi = [float(x.encode('ascii', 'ignore').strip()) for x in location.split(',')]
    air_code = getNearestAirport(lat, longi)["iata"]
    at = authenticate()
    token = at['access_token']

    url = url % air_code


    res = requests.get(url, headers={'Authorization': 'Bearer ' + token})

    di = ast.literal_eval(res.text)


    destinations = []

    for dest in di['Destinations']:
        dest_location = dest['Destination']['DestinationLocation']
        try:
            x = get_min_fare(air_code, dest_location, token)
        except:
            try:
                x = get_min_fare(dest_location, air_code, token)
            except:
                continue

        if 2 * x < 0.4 * price:
            destinations.append((price - 2 * x, dest_location))

    try:
        return random.choice(destinations)
    except IndexError:
        return (price, None)


def roam_nearby_places(place, price):
    pass
