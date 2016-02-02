from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import time
import json
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


def check(request):
    if request.method == "POST":
        price = request.POST['money']
        location = request.POST['location']

        print request.POST

        price, first_dest = places_to_visit(location, float(price))

        # lat, longi = [float(x.encode('ascii', 'ignore').strip()) for x in location.split(',')]
        # location = Geocoder.reverse_geocode(lat, longi)


        list_places = []

        # call getDays on the first destination here

        if first_dest is not None:
            list_places.append(first_dest)
            go_nearby(Geocoder.geocode(first_dest), price, list_places)
        else:
            go_nearby(location, price, list_places)

        return render(request, "index.html", {})
    else:
        return HttpResponseRedirect('/')