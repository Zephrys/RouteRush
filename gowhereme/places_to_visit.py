import requests
import ast
import json
import random
from datetime import datetime
from geopy.distance import vincenty

from key import *
from pygeocoder import Geocoder
from pymongo import MongoClient
from unidecode import unidecode

mongoclient = MongoClient('mongodb://localhost:27017/')
routerush = mongoclient.routerush

gplaces = routerush.gplaces
gphotos = routerush.gphotos
route_rome = routerush.rome2rio


def getPhoto(reference):
    url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=%s&key=%s" % (reference, goo_key())

    x = gphotos.find({'reference': reference})
    if x.count() != 0:
        print 'found in mongo!'
        return x[0]['url']

    response = requests.get(url).url
    x = gphotos.insert({'reference':reference, 'url': response})
    return response


def getDays(city,country, budget):
    city = city.split(",")[0]

    citycostson = json.loads(open('cities.json').read())

    citycostson = {k:{x.lower():y for x,y in v.items()} for k,v in citycostson.items()}
    x = gplaces.find({'city': city, 'country': country})
    if x.count()!=0:
        data = x[0]
        print 'get days mongo mein mila'
        status = 200
    else:
        location = Geocoder(goo_key()).geocode(city + "," + country)
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=%s&location=%s,%s&radius=30000'%(goo_key(),location.latitude,location.longitude)
        response = requests.get(url)
        status = response.status_code
        data = response.json()
        gplaces.insert({'city':city, 'country': country, 'results': response.json()['results']})
    photo = False
    allowed = ["point_of_interest", "establishment", "natural_feature", "museum", "amusement_park", "aquarium", "church", "hindu_temple", "mosque", "casino", "city_hall", "place_of_worship", "synagogue", "shopping_mall"]
    places = []

    if status  == 200:
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
                        if not photo:
                            photo = getPhoto(location["photos"][0]["photo_reference"])
                        location['image'] = photo
                        places.append(location)

    days = 0
    number_of_places = len(places)

    city = unidecode(city)
    while True:
        if (budget - float(citycostson[country][city.lower()]["cost"])) < 0:
            break
        days += 1
        number_of_places -= 4
        budget -= float(citycostson[country][city.lower()]["cost"])
        if number_of_places <= 0:
            break
    cost_per_day= citycostson[country][city.lower()]["cost"]
    output_object = []
    for day in xrange(0,days):
        output_object.append([])
        for place in places[day*4:(day*4)+4]:
            output_object[int(day)].append({'name': place['name'], 'photo': place['image']})
    f=[]
    for i in xrange(0,len(output_object)):
        f.append( "Day: %d "%(int(i)+1) + ", ".join([x['name'] for x in output_object[i]]))

    return f, budget, days, cost_per_day, photo


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
    response = {}
    a = route_rome.find({'city1': city_1, 'city2': city_2})

    if a.count() == 1:
        print "found in mongo 1"
        response = a[0]['response']
    else:
        print "hello"
        url = 'http://free.rome2rio.com/api/1.2/json/Search?key=%s&oName=%s&dName=%s' % (rio_key(), city_1, city_2)
        response = requests.get(url)
        response = response.json()
        route_rome.insert({'city1': city_1, 'city2': city_2, 'response': response})

    price = 32768
    route_o = False


    try:
        data = response["routes"]
        for route in data:
            if not (route.has_key("indicativePrice") and route["indicativePrice"].has_key("price")) and not ("bus" in route["name"].lower() or "train" in route["name"].lower() or "cab" in route["name"].lower() or "taxi" in route["name"] or  "ferry" in route["name"].lower()):
                continue
            if float(route["indicativePrice"]["price"]) < price:
                price = float(route["indicativePrice"]["price"])
                route_o = route
        return route_o
    except:
        return False

#multiple appends of visited_cities
# budget 0 pe crash?
# add initial plane route
def go_nearby(starting_city, flew_to, price, visited_cities, initial_route=[]):
    iata = getNearestAirport(starting_city.latitude, starting_city.longitude)
    scity = Geocoder(goo_key()).geocode(str(iata['lat']) + "," +  str(iata['lon'])).city
    print iata
    print scity
    if flew_to.city is None:
        flew_to.city = str(flew_to)
    if starting_city.city is None:
        starting_city.city = str(starting_city)

    visited_cities.append(flew_to.city)
    visited_cities.append(starting_city.city)
    present_city = flew_to
    visited_in_city = []

    if starting_city != flew_to:

        (di, price,days, cost_per_day, photo) = getDays(flew_to.city, flew_to.country, price)
        visited_in_city.append({'days': range(days),'city': flew_to.city, 'country': flew_to.country,'duration_of_stay':days,'cost_per_day': cost_per_day,
                'mode_of_transport': initial_route['name'], 'price_of_travel': initial_route['indicativePrice']['price'], 'return':False,'places': di, 'photo':photo})
    prev_route = None

    while price > 0:

        city, curr_country = getNextCity(present_city.latitude, present_city.longitude, present_city.country, visited_cities)

        print city, curr_country

        if city is None:
            return visited_in_city

        route = rome2rio(present_city.city, city, price)

        if route is False:
            visited_cities.append(city)
            continue

        print 'Route Exists'
        dest = Geocoder(goo_key()).geocode(city + ',' + curr_country)

        if dest.city is None:
            dest.city = city

        airfare = 0

        route_return = None
        if dest.country != starting_city.country:
            airfare, route_return = get_rio(dest.city, scity)
            airfare = float(airfare)
        else:
            route_return = rome2rio(starting_city.city, dest.city, 32768)
            airfare = float(route_return['indicativePrice']['price'])

        if airfare*1.2 < price:
            price -= float(route['indicativePrice']['price'])
            (di, price,days, cost_per_day, photo) = getDays(dest.city, dest.country, price)
            present_city = dest
            prev_route = route_return
            visited_in_city.append({'days': range(days),'city': dest.city, 'country': dest.country,'duration_of_stay':days,'cost_per_day': cost_per_day,
                'mode_of_transport': route['name'], 'price_of_travel': route['indicativePrice']['price'], 'return':False, 'places': di, 'photo':photo})
            visited_cities.append(city)
        else:
            visited_in_city.append({'return': True, 'price_of_travel': prev_route['indicativePrice']['price'], 'mode_of_transport'
                : prev_route['name']})
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
    response = {}
    a = route_rome.find({'city1': source, 'city2': destination})
    if a.count() == 1:
        print "found in mongo"
        response = a[0]['response']
    else:
        print "finding for " + source + " and " + destination
        url = 'http://free.rome2rio.com/api/1.2/json/Search?key=%s&oName=%s&dName=%s' % (rio_key(), source, destination)
        response = requests.get(url)
        response = response.json()
        print response
        route_rome.insert({'city1': source, 'city2': destination, 'response': response})

    price = 32768
    route = None
    for x in response["routes"]:

        if (destination.lower() in x["name"].lower()) and x.has_key("indicativePrice") and x["indicativePrice"].has_key("price"):
            indicativePrice  = x["indicativePrice"]["price"]
            if indicativePrice < price:
                price = indicativePrice
                route = x
    if price == 32768:

        for x in response["routes"]:
            if ("Fly".lower() in x["name"].lower()) and x.has_key("indicativePrice") and x["indicativePrice"].has_key("price"):
                indicativePrice  = x["indicativePrice"]["price"]
                if indicativePrice < price:
                    price = indicativePrice
                    route = x


    return price, route

def get_min_fare(source, destination, token):
    url = "https://api.test.sabre.com/v2/shop/flights/fares?origin=%s&destination=%s&departuredate=%s&lengthofstay=15"
    url = url % (source, destination, str(datetime.now().date()))


    res = requests.get(url, headers={ 'Authorization': 'Bearer ' + token})

    di = ast.literal_eval(res.text)

    # print di
    cost = di['FareInfo'][0]['LowestFare']['Fare']
    return cost



def pick_cities(origin, price):
    done_cities =[]
    count = 10
    origin_object = Geocoder(goo_key()).geocode(origin)
    origin_aircode = getNearestAirport(origin_object.latitude, origin_object.longitude)
    cities = json.loads(open('cities.json','r').read())

    while count!= 0:
        country = random.choice(cities.keys())
        city = random.choice(cities[country].keys())

        print city

        if country == origin_object.country or city in done_cities:
            continue

        count -= 1

        done_cities.append(city)
        dest_city = Geocoder(goo_key()).geocode(city + "," + country)
        if dest_city.city is None:
            dest_city.city = city
        dest_aircode = getNearestAirport(dest_city.latitude,dest_city.longitude)['iata']
        try:
            print "finding fare from"
            origin_city = Geocoder(goo_key()).geocode(origin_aircode['lat'] +","+ origin_aircode['lon']).city
            print origin_city
            print dest_city.city
            fare, route = get_rio(origin_city, dest_city.city)
            print "found fare " + origin_city
        except:
            print origin_aircode
            print "fails for " + city
            continue

        print fare
        if fare < 0.3 * price:
            return price - fare, city, route
    return price, False, False


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
