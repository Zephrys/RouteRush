import requests
import ast
from key import sabre_api_key as sabre_key
import json
import random
from datetime import datetime
from geopy.distance import vincenty

from pygeocoder import Geocoder

api_key = 'AIzaSyBYNhvCYTT7iIZNKavmTf9lplS57WQeCJw'

def getPhoto(reference):
    url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=%s&key=%s" % (reference,
                                                                                                      api_key)
    response = requests.get(url).url
    return response


def getDays(city,country, budget):
    citycostson = json.loads(open('cities.json').read())
    location = Geocoder.geocode(city)
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=%s&location=%s,%s&radius=3000'%(api_key,location.latitude,location.longitude)
    response = requests.get(url)
    allowed = ["point_of_interest", "establishment", "natural_feature", "museum", "amusement_park", "aquarium", "church", "hindu_temple", "mosque", "casino", "city_hall", "place_of_worship", "synagogue", "shopping_mall"]
    places = []
    if response.status_code == 200:
        data = response.json()
        data = data["results"]
        for location in data:
            if "point_of_interest" not in location["types"]:
                continue
            else:
                flag = True
                for x in location["types"]:
                    if x not in allowed:
                        flag = False
                if not flag:
                    continue
                else:
                    if location.has_key("photos") and len(location["photos"])!=0 :
                        location["image"] = getPhoto(location["photos"][0]["photo_reference"])
                        places.append(location)

    days = 0
    number_of_places = len(places)
    while True:
        if budget - float(citycostson[country][city]["cost"]) < 0:
            break
        days += 1
        number_of_places -= 4
        if number_of_places < 0:
            break
        budget -= float(citycostson[country][city]["cost"])
    return dict(city=city, country=country, days=days, places=places[:days * 4]), budget


def getNextCity(lat, lon, country, visited_cities, sameCountry=True):
    cityson = json.loads(open('cities.json').read())
    nearest_city = None
    nearest_measure = 320000
    country_changed = country
    if sameCountry:
        for city_temp in cityson[country]:
            if city_temp in visited_cities:
                continue
            city = cityson[country][city_temp]
            distance = vincenty((lat, lon), (city['lat'], city['lon']))
            if distance < nearest_measure:
                nearest_measure = distance
                nearest_city = city_temp
    if nearest_city is None:
        nearest_city = None
        nearest_measure = 320000
        for country_temp in cityson:
            if country == country_temp:
                continue
            for city_temp in cityson[country_temp]:
                if city_temp in visited_cities:
                    continue
                city = cityson[country_temp][city_temp]
                distance = vincenty((lat, lon), (city['lat'], city['lon']))
                if distance < nearest_measure:
                    nearest_measure = distance
                    nearest_city = city_temp
                    country_changed = country_temp

    # if nearest_city:
    #     visited_cities.append(nearest_city)
    return nearest_city, country_changed


def rome2rio(city_1, city_2, budget):
    url = 'http://free.rome2rio.com/api/1.2/json/Search?key=jaWnO4YP&oName=%s&dName=%s' % (city_1, city_2)
    response = requests.get(url)
    price = 32768
    route_o = False
    try:
        data = response.json()["routes"]
        for route in data:
<<<<<<< HEAD
            if not (route.has_key("indicativePrice") and route["indicativePrice"].has_key("price")) and not ("bus" in route["name"].lower() or "train" in route["name"].lower() or "cab" in route["name"].lower() or "taxi" in route["name"] or  "ferry" in route["name"]):
=======
            if not (route.has_key("indicativePrice") and route["indicativePrice"].has_key("price")):
>>>>>>> is smoother, rome2rio and get_rio return a lot of noise as they don't work with iata codes, need to find do data pre processing
                continue
            if float(route["indicativePrice"]["price"]) < price:
                price = float(route["indicativePrice"]["price"])
                route_o = route
        return route_o
    except:
        return False

#multiple appends of visited_cities
# budget 0 pe crash?
<<<<<<< HEAD
# add initial plane route
def go_nearby(starting_city, flew_to, price, visited_cities):
    iata = getNearestAirport(starting_city.latitude, starting_city.longitude)
    scity = Geocoder.geocode(str(iata['lat']) + "," +  str(iata['lon'])).city
=======
def go_nearby(starting_city, flew_to, price, visited_cities):
>>>>>>> is smoother, rome2rio and get_rio return a lot of noise as they don't work with iata codes, need to find do data pre processing
    if flew_to.city is None:
        flew_to.city = str(flew_to)
    if starting_city.city is None:
        starting_city.city = str(starting_city)

    visited_cities.append(flew_to.city)
    visited_cities.append(starting_city.city)
    present_city = flew_to
    visited_in_city = []
    if starting_city != flew_to:
        (di, price) = getDays(flew_to.city, flew_to.country, price)
        visited_in_city.append(di)
    prev_route = None
    while price > 0:
        city, curr_country = getNextCity(present_city.latitude, present_city.longitude, present_city.country, visited_cities)
        if city is None:
            return visited_in_city
        route = rome2rio(present_city.city, city, price)
        dest = Geocoder.geocode(city)
        # at = authenticate()
        if dest.city is None:
            dest.city = city
        airfare =0

        route_return = None
        if dest.country != starting_city.country:
            airfare, route_return = get_rio(dest.city, scity)
            airfare = float(airfare)
        else:
            route_return = rome2rio(starting_city.city, dest.city, 32768)
            airfare = float(route_return['indicativePrice']['price'])

        if airfare*1.2 < price:
            price -= float(route['indicativePrice']['price'])
            (di, price) = getDays(dest.city, dest.country, price)
            present_city = dest
            prev_route = route_return
            visited_in_city.append(route)
            visited_in_city.append(di)
            visited_cities.append(dest.city)
        else:
            visited_in_city.append(prev_route)
            return visited_in_city


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

def get_rio(source, destination):
    url = 'http://free.rome2rio.com/api/1.2/json/Search?key=jaWnO4YP&oName=%s&dName=%s' % (source, destination)
    response = requests.get(url)
    response = response.json()
    price = 32768
    route = None
    for x in response["routes"]:
        if (destination in x["name"]) and x.has_key("indicativePrice") and x["indicativePrice"].has_key("price"):
            indicativePrice  = x["indicativePrice"]["price"]
            if indicativePrice < price:
                price = indicativePrice
                route = x
    if price == 32768:
        for x in response["routes"]:
            if ("Fly" in x["name"]) and x.has_key("indicativePrice") and x["indicativePrice"].has_key("price"):
                indicativePrice  = x["indicativePrice"]["price"]
                if indicativePrice < price:
                    price = indicativePrice
                    route = x
    return price, route

def get_min_fare(source, destination, token):
    url = "https://api.test.sabre.com/v2/shop/flights/fares?origin=%s&destination=%s&departuredate=%s&lengthofstay=15"
    url = url % (source, destination, str(datetime.now().date()))
    print source
    print destination
    print token
    # print url
    res = requests.get(url, headers={ 'Authorization': 'Bearer ' + token})
    print res.status_code
    di = ast.literal_eval(res.text)

    # print di
    cost = di['FareInfo'][0]['LowestFare']['Fare']
    return cost



def pick_cities(origin, price):
    done_cities =[]
    count = 10
    while count!= 0:
        count -= 1
        origin_object = Geocoder.geocode(origin)
        cities = json.loads(open('cities.json','r').read())
        country = random.choice(cities.keys())
        city = random.choice(cities[country].keys())
        print city, country
        if country == origin_object.country or city in done_cities:
            continue
        done_cities.append(city)
        dest_city = Geocoder.geocode(city)
        if dest_city.city is None:
            dest_city.city = city
        dest_aircode = getNearestAirport(dest_city.latitude,dest_city.longitude)['iata']
        origin_aircode = getNearestAirport(origin_object.latitude, origin_object.longitude)
        try:
            print origin_aircode['lat'] +","+ origin_aircode['lon']
            fare, route = get_rio(Geocoder.geocode(origin_aircode['lat'] +","+ origin_aircode['lon']).city, dest_city.city)
        except:
            continue
        print "escaped that"
        if fare < 0.2 * price:
            return price - fare, city, route
    return price, False


def places_to_visit(location, price):
    """
    :param location: coordinates
    :param price: Total Money that the use can spend
    :return: flight Cost of the cheapest (top) destination the user could visit
    """
    url = "https://api.test.sabre.com/v1/lists/top/destinations?origin=%s&lookbackweeks=2&topdestinations=15&destinationtype=International"
    #location nahi aaya toh????
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
