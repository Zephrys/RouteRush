import requests
import ast
from key import sabre_api_key as sabre_key
import json
import random
from datetime import datetime
from geopy.distance import vincenty

from pygeocoder import Geocoder

api_key = 'AIzaSyBYNhvCYTT7iIZNKavmTf9lplS57WQeCJw'


def getDays(city,country, budget):
    citycostson = json.loads(open('city_price.json').read())
    location = Geocoder.geocode(city)
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=%s&location=%s,%s&radius=3000'%(api_key,location.latitude,location.longitude)
    response = requests.get(url)
    allowed = ["point_of_interest", "establishment", "natural_feature", "museum", "amusement_park", "aquarium", "church", "hindu_temple", "mosque", "casino", "city_hall", "place_of_worship", "synagogue", "shopping_mall"]
    places = []
    if response.status == 200:
        data = response.json()
        data = data["results"]
        for location in data:
            if "point_of_interest" not in data["types"]:
                continue
            else:
                flag = True
                for x in data["types"]:
                    if x not in allowed:
                        flag = False
                if not flag:
                    continue
                else:
                    if location.has_key["photos"]:
                        location["image"] = getPhoto(location["photos"]["photo_reference"])
                        places.append(location)

    days = 0
    number_of_places = len(places)
    while true:
        if budget - citycostson[country][city] < 0:
            break
        days += 1
        number_of_places -= 4
        if number_of_places < 0:
            break
        budget -= citycostson[country][city]

    return dict(city=city, country=country, days=days, places=places[:days * 4]), budget


def getNextCity(lat, lon, country, visited_cities, sameCountry=True):
    cityson = json.loads(open('city_geo.json').read())
    citycostson = json.loads(open('city_price.json').read())
    nearest_city = None
    nearest_measure = 320000
    country_changed = country
    if sameCountry:
        for city_temp in cityson[country]:
            if not (citycostson.has_key[country] and citycostson[country].has_key[city_temp]) or city_temp in visited_cities:
                continue
            city = cityson[country][city_temp]
            distance = vincenty((lat, lon), (city['lan'], city['lon']))
            if distance < nearest_measure:
                nearest_measure = distance
                nearest_city = city
    if not nearest_city:
        nearest_city = None
        nearest_measure = 320000
        for country_temp in cityson:
            if country == country_temp:
                continue
            for city_temp in cityson[country_temp]:
                if not (citycostson.has_key[country] and citycostson[country].has_key[city_temp]) or city_temp in visited_cities:
                    continue
                city = cityson[country][city_temp]
                distance = vincenty((lat, lon), (city['lan'], city['lon']))
                if distance < nearest_measure:
                    nearest_measure = distance
                    nearest_city = city
                    country_changed = country_temp

    if nearest_city:
        visited_cities.append(nearest_city)

    return nearest_city, country_changed


def rome2rio(city_1, city_2, budget):
    url = 'http://free.rome2rio.com/api/1.2/json/Search?key=jaWnO4YP&oName=%s&dName=%s' % (city_1, city_2)
    response = requests.get(url)
    data = response.json()["routes"]
    for route in routes:
        if route["indicativePrice"]["price"] < budget:
            return route
    return False


def go_nearby(location, price, visited_cities):
    while price > 0:
        city, curr_country = getNextCity(location.latitude, location.longitude, location.country, visited_cities)
        route = rome2rio(location.city, city, price)
        price -= route['indicativePrice']['price']

        dest = Geocoder.geocode(city)
        at = authenticate()

        budget = get_min_fare(location.city, getNearestAirport(dest.latitude, dest.longitude), at['access_token'])
        if budget < 1.2 * price:
            (di, price) = getDays(dest.city, dest.country, price - budget)
            visited_cities.append(di)
        else:
            return visited_cities


def getNearestAirport(lat, lon):
    airson = json.loads(open('airports.json').read())
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

        if x < (0.2 * price):
            destinations.append((price - 2 * x, dest_location))

    try:
        return random.choice(destinations)
    except IndexError:
        return (price, None)


def roam_nearby_places(place, price):
    pass
