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
from pymongo import MongoClient

def home(request):
    return render(request, "index.html", {})


def check(request):
    if request.method == "POST":
        price = request.POST['money']
        location = request.POST['location']
        price = price.split(" ")

        try:
            if len(price) == 2 and price[1] != 'USD':
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
            location_flight = Geocoder.geocode(first_dest)[0]
            location = Geocoder.geocode(location)[0]
            response = go_nearby(location, location_flight, price, list_places, route)
            list_places = response
        else:

            location = Geocoder.geocode(location)[0]
            response = go_nearby(location, location, price, list_places)
            list_places = response

        mongoclient = MongoClient('mongodb://localhost:27017/')
        routerush = mongoclient.routerush

        geo = routerush.geo

        pprint(list_places)

        i = 0
        lat_sum = 0.0
        lon_sum = 0.0

        for i, place in enumerate(list_places[:-1]):

            city = place['city']
            a = geo.find({'city': city})
            place['count'] = i + 2

            if a.count() > 1:
                place['lat'] = a[0]['lat']
                place['lon'] = a[0]['lon']
            else:
                ob = Geocoder.geocode(city)
                geo.insert_one({'city': city, 'lat': ob.latitude, 'lon': ob.longitude })
                place['lat'] = ob.latitude
                place['lon'] = ob.longitude

            lat_sum += place['lat']
            lon_sum += place['lon']

        lat_av = lat_sum/i
        lon_av = lon_sum/i
        print lat_av
        print lon_av

        pprint(list_places)

        og = Geocoder.geocode(location.city)
        return render(request, "new_check.html", {'places_list': list_places[:-1],
                                              'origin': location.city,
                                              'origin_lat': og.latitude ,
                                              'origin_lon': og.longitude,
                                              'second_city': list_places[0]['city'],
                                              'last_city': list_places[-2]['city'],
                                              'return_fare': list_places[-1],
                                              'lat_av': lat_av,
                                              'lon_av': lon_av,
                                              })
    else:
        # HttpResponseRedirect('/')
        list_places = [{'city': u'Agra',
  'cost_per_day': u'28.54',
  'country': u'India',
  'days': [0, 1],
  'duration_of_stay': 2,
  'mode_of_transport': u'Rideshare',
  'photo': u'https://lh5.googleusercontent.com/-Q4xmN6WACjg/Vmw1b6RUplI/AAAAAAAAC40/X9VHtOrO3SU/s1600-w400/',
  'places': [u'Day: 2 Agra Fort\nItmad-ud-Daula\nMoti Masjid\nFET Agra College',
             u'Day: 1 Taj Mahal\nAgra Fort\nItmad-ud-Daula\nMoti Masjid'],
  'price_of_travel': 8,
  'return': False},
 {'city': u'Mumbai',
  'cost_per_day': u'29.27',
  'country': u'India',
  'days': [0, 1, 2],
  'duration_of_stay': 3,
  'mode_of_transport': u'Bus',
  'photo': u'https://lh4.googleusercontent.com/-YuaJDaJ_vCA/VchvaTrEwDI/AAAAAAAACJA/Fwp12M8V28w/s1600-w400/',
  'places': [u'Day: 2 Indian Institute of Technology Bombay\nEssel World\nGateway Of India Mumbai\nDadasaheb Phalke Chitranagri',
             u'Day: 1 Elephanta Caves\nIndian Institute of Technology Bombay\nEssel World\nGateway Of India Mumbai',
             u'Day: 3 Essel World\nGateway Of India Mumbai\nDadasaheb Phalke Chitranagri\nMani Bhavan Gandhi Sanghralaya'],
  'price_of_travel': 21,
  'return': False},
 {'city': u'Goa',
  'cost_per_day': u'32.86',
  'country': u'India',
  'days': [0],
  'duration_of_stay': 1,
  'mode_of_transport': u'Bus',
  'photo': u'https://lh4.googleusercontent.com/-Ycq7ODH0mGA/VRGAfX5VfII/AAAAAAAAHjc/5me00KzfmFs/s1600-w400/',
  'places': [u'Day: 1 Basilica of Bom Jesus\nSe Cathedral\nOld Goa Book Stall (Jivitacho Sondex)\nChurch of St Francis of Assisi'],
  'price_of_travel': 15,
  'return': False},
 {'city': u'Chennai',
  'cost_per_day': u'24.55',
  'country': u'India',
  'days': [0, 1],
  'duration_of_stay': 2,
  'mode_of_transport': u'Bus to Manila, fly',
  'photo': u'https://lh3.googleusercontent.com/-VRjO-lwnm6g/Vg3kdqXKBXI/AAAAAAAAAAc/8mN-cfBaU48/s1600-w400/',
  'places': [u'Day: 2 VGP Universal Kingdom\nArulmigu Parthasarathyswamy Temple\nKalakshetra Foundation\nMGM Dizzee World',
             u'Day: 1 Express Avenue\nVGP Universal Kingdom\nArulmigu Parthasarathyswamy Temple\nKalakshetra Foundation'],
  'price_of_travel': 233,
  'return': False},
 {'city': u'Bangkok',
  'cost_per_day': u'31.55',
  'country': u'Thailand',
  'days': [0, 1],
  'duration_of_stay': 2,
  'mode_of_transport': u'Fly to Bangkok Don Muang',
  'photo': u'https://lh3.googleusercontent.com/-PkGVkORnhCA/VnqmYM44iTI/AAAAAAADR78/5I-wcLoBscU/s1600-w400/',
  'places': [u'Day: 2 MBK Center\nThe Emerald Buddha Temple (Wat Phrakaew)\nSea Life Bangkok Ocean World\nSiam Center',
             u'Day: 1 Wat Pho\nMBK Center\nThe Emerald Buddha Temple (Wat Phrakaew)\nSea Life Bangkok Ocean World'],
  'price_of_travel': 153,
  'return': False},
 {'city': u'Kuala Lumpur',
  'cost_per_day': u'30.61',
  'country': u'Malaysia',
  'days': [0, 1],
  'duration_of_stay': 2,
  'mode_of_transport': u'Train',
  'photo': u'https://lh5.googleusercontent.com/-pmSGtLr3Odw/VmRRz7R5WsI/AAAAAAAGukc/oBE4fKVCwik/s1600-w400/',
  'places': [u'Day: 2 Aquaria KLCC\nNational Mosque of Malaysia\nMasjid Jamek Bandaraya Kuala Lumpur (Jamek Mosque)\nNational Planetarium',
             u'Day: 1 Batu Caves\nAquaria KLCC\nNational Mosque of Malaysia\nMasjid Jamek Bandaraya Kuala Lumpur (Jamek Mosque)'],
  'price_of_travel': 34,
  'return': False},
 {'mode_of_transport': u'Train, fly', 'price_of_travel': 229, 'return': True}]

        return (render(request, "check.html", {"places_list":list_places[:-1], 'origin': 'Mumbai',
                                              'second_city': list_places[0]['city'],
                                              'last_city': list_places[-2]['city'], 'return_fare':list_places[-2]}))
