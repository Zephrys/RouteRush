from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import requests
from django.http import HttpResponse, HttpResponseRedirect
import time
import json
from geopy.distance import vincenty
from django.contrib import messages
from pprint import pprint

# from scripts.get_city import get_price_city
from places_to_visit import places_to_visit, go_nearby, pick_cities

from pygeocoder import Geocoder


def home(request):
    return render(request, "index.html", {})

# no location ka scen

def check(request):
    if request.method == "POST":
        price = request.POST['money']
        location = request.POST['location']
        price = price.split(" ")
        try:
            if len(price) == 2:
                url = 'http://api.fixer.io/latest?symbols=%s&base=USD'%price[1].upper()
                response = requests.get(url)
                if response.status_code == 200:
                    response = response.json()
                    if not response.has_key('error'):
                        price = float(price[0]) / float(response['rates'][price[1].upper()])
                    else:
                        price= float(price[0])
                else:
                    price = float(price[0])
            else:
                try:
                    price = float(price[0])
                except:
                    price = 5000
        except:
            price = 5000

        print request.POST

        price, first_dest, route = pick_cities(location, float(price))
		# what if this city isn't in our list??/
        # lat, longi = [float(x.encode('ascii', 'ignore').strip()) for x in location.split(',')]
        # location = Geocoder.reverse_geocode(lat, longi)


        list_places = []

        # call getDays on the first destination here
        response = None
        if first_dest is not False:
            print 'this'
            print location
            location_flight = Geocoder.geocode(first_dest)[0]
            response = go_nearby(Geocoder.geocode(location)[0], location_flight, price, list_places)
        else:
            print 'here'
            location = Geocoder.geocode(location)[0]
            response = go_nearby(location, location, price, list_places)
        # sodhi ne yahan pe haga hua hai
        pprint( [route] + response)
        return render(request, "index.html", {})
    else:
        list_places = []
        list_places.append({
            'city': 'Delhi',
            'description': "Bakar jagah",
            'days': 4,
        })

        list_places.append({
            'city': 'Mumbai',
            'description': 'Beaches Buisness capital of India',
            'days': 3,
        })
        list_places.append({
            'city': 'Delhi',
            'description': "Bakar jagah",
            'days': 4,
        })

        list_places.append({
            'city': 'Mumbai',
            'description': 'Beaches Buisness capital of India',
            'days': 3,
        })
        return render(request, "check.html", {'places_list': list_places,
                                              'origin': 'Delhi',
                                              'dest': 'Mumbai'})
