from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import time
import json
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

from pprint import pprint

# from scripts.get_city import get_price_city
from places_to_visit import places_to_visit, go_nearby

from pygeocoder import Geocoder


def home(request):
    return render(request, "index.html", {})


def getPhoto(reference):
    url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=%s&key=%s" % (reference,
                                                                                                      api_key)
    response = requests.get(url).url
    return response


api_key = 'AIzaSyBYNhvCYTT7iIZNKavmTf9lplS57WQeCJw'

geolocator = Nominatim()


def getDays(city, budget):
    location = geolocator.geocode(city)

    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=%s&location=%s,%s&radius=3000'
    url = url % (api_key, location.latitude, location.longitude)

    response = requests.get(url)
    allowed = ["point_of_interest", "establishment", "natural_feature", "museum", "amusement_park", "aquarium",
               "church", "hindu_temple", "mosque", "casino", "city_hall", "place_of_worship", "synagogue",
               "shopping_mall"]
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
                if not Flag:
                    continue
                else:
                    places.append(location)

    days = len(places) / 4
    if len(places) % 4 > 2:
        days += 1

    return days, places


def getNearestAirport(lat, lon):
    airson = json.loads(open('airports.json').read())
    nearest_airport = None
    nearest_measure = 320000
    for airport in airson:
        if not airport.has_key('lat') and not airport.has_key('lon') or (airport.has_key('size') and airport['size'] != 'large'):
            continue
        distance = vincenty((lat, lon), (airport['lat'], airport['lon']))
        if distance < nearest_measure:
            nearest_measure = distance
            nearest_airport = airport

    return nearest_airport


def getNextCity(lat, lon, country, visited_cities, sameCountry=True):
    cityson = json.loads(open('city_geo.json').read())
    citycostson = json.loads(open('city_price.json').read())
    nearest_city = None
    nearest_measure = 320000
    country_changed = False
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
    return nearest_city, country_temp


def rome2rio(city_1, city_2, budget):
    url = 'http://free.rome2rio.com/api/1.2/json/Search?key=jaWnO4YP&oName=%s&dName=%s' % (city_1, city_2)
    response = requests.get(url)
    data = response.json()["routes"]
    for route in routes:
        if route["indicativePrice"]["price"] < budget:
            return route
    return False


def check(request):
    if request.method == "POST":
        price = request.POST['money']
        location = request.POST['location']

        print request.POST

        lat, longi = [float(x.encode('ascii', 'ignore').strip()) for x in location.split(',')]
        location = Geocoder.reverse_geocode(lat, longi)

        price, first_country = places_to_visit(location, price)

        list_places = []

        if first_country is not None:
            list_places.append(first_country)
            go_nearby(geolocator.geocode(first_country), price)
        else:
            go_nearby(location, price)

        return render(request, "index.html", {})
    else:
        return HttpResponseRedirect('/')
