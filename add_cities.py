import json
from pygeocoder import Geocoder
import sys

def main():
	cities = json.loads(open('cities.json', 'r').read())
	if len(sys.argv) < 3:
		print 'Format:\t python add_cities.py City Country [daily_cost]'
		sys.exit()

	city = sys.argv[1];
	cntry = sys.argv[2];
	geocity = Geocoder.geocode('%s, %s' %(city, cntry))

	if len(sys.argv) == 4:
		data = {'lat': geocity.latitude, 'lon': geocity.longitude, 'cost': float(sys.argv[3])}
		if cities.has_key(cntry) and not city.has_key(city):
			cities[cntry][city] = {}
			cities[cntry][city] = data
		elif cities.has_key(city):
			print 'city already in data base'
			sys.exit()
		else:
			cities[cntry] = {}
			cities[cntry][city] = data
	else:
		if cities.has_key(cntry):
			country = cities[cntry]
			average = sum([float(country[x]['cost']) for x in country])/float(len(country))
			data = {'lat': geocity.latitude, 'lon': geocity.longitude, 'cost': average}
			cities[cntry][city] = data = {'lat': geocity.latitude, 'lon': geocity.longitude, 'cost': average}
		else:
			print 'Country not in data base to average cost from'
			sys.exit()

	output  = open('cities_new.json', 'w')
	output.write(json.dumps(cities))
	output.close()
	print 'file saved in cities_new.json'


if __name__ == '__main__':
	main()