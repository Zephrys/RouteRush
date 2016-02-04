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


def check(request):
    if request.method == "POST":
        price = request.POST['money']
        location = request.POST['location']
        price = price.split(" ")
        try:
            if len(price) == 2 and price[1] == 'USD':
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
        print 'started with%s' %(str(price))
        price, first_dest, route = pick_cities(location, float(price))
		# what if this city isn't in our list??/
        # lat, longi = [float(x.encode('ascii', 'ignore').strip()) for x in location.split(',')]
        # location = Geocoder.reverse_geocode(lat, longi)
        print 'after going to x I am left with %s' %(str(price))

        list_places = []

        # call getDays on the first destination here
        response = None
        if first_dest is not False:
            print 'this'
            print location
            location_flight = Geocoder.geocode(first_dest)[0]
            response = go_nearby(Geocoder.geocode(location)[0], location_flight, price, list_places, route)
            list_places = response
        else:
            print 'here'
            location = Geocoder.geocode(location)[0]
            response = go_nearby(location, location, price, list_places)
            list_places =response
        o = open('final.output','w')
        o.write(str(list_places))
        pprint(response)
        return render(request, "check.html", {'places_list': list_places,
                                              'origin': location.city,
                                              'dest': list_places[-1]['city']})
    else:
        list_places = []
        list_places.append({
            'city': 'Delhi',
            'duration_of_stay': 3,
            '0': {'name': 'something'},
            'country': 'India',
            '0': [{'photo': u'https://lh6.googleusercontent.com/-Uyl8qQ0L5mw/VktH878sSlI/AAAAAAAABpY/5VHc2w9Zdh0/s1600-w400/', 'name': u'Wortham Theater Center'}, {'photo': u'https://lh4.googleusercontent.com/-NUa0U5mwUbc/Uu23N4RoP2I/AAAAAAAAxeo/64DLuV18FqQ/s1600-w400/', 'name': u'Revention Music Center'}, {'photo': u'https://lh6.googleusercontent.com/-RF_IizdDM8Q/UgVbz4-zRLI/AAAAAAAAAIc/0Q6-nqitrGU/s1600-w300/', 'name': u'Warehouse Live'}, {'photo': u'https://lh6.googleusercontent.com/-eAFDaDGnu98/VNC_8hwwC2I/AAAAAAAAAAc/uvd8_KIFdPE/s1600-w400/', 'name': u'Alley Theatre'}],
            'description': "Bakar jagah",
            'days': range(4),
        })

        list_places.append({
            'city': 'Mumbai',
            'description': 'Beaches Buisness capital of India',

        })
        list_places.append({
            'city': 'Delhi',
            'description': "Bakar jagah",

        })

        list_places.append({
            'city': 'Mumbai',
            'description': 'Beaches Buisness capital of India',

        })
        return render(request, "check.html", {'places_list': list_places,
                                              'origin': 'Delhi',
                                              'dest': 'Mumbai'})
