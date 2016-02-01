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

def home(request):
    return render(request, "index.html", {})


api_key='AIzaSyBYNhvCYTT7iIZNKavmTf9lplS57WQeCJw'
def getDays(city,budget):
	geolocator = Nominatim()
	location = geolocator.geocode(city)
	url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=%s&location=%s,%s&radius=3000'%(api_key,location.latitude,location.longitude)
	response = requests.get(url)
	allowed = ["point_of_interest", "establishment", "natural_feature", "museum", "amusement_park", "aquarium", "church", "hindu_temple", "mosque", "casino", "city_hall", "place_of_worship", "synagogue", "shopping_mall"]
	places = []
	if response.status ==200:
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

	days = len(places)/4
	if len(places)%4 > 2:
		days = days + 1

	return days, places

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

def check(request):
	if request.method == 'POST':
		print request.POST
	return HttpResponseRedirect('/')
