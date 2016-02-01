import requests


def places_to_visit(location, price):
    url = "https://api.sabre.com/v1/lists/top/destinations?origin=%s&lookbackweeks=2&topdestinations=5"

    #  get closest large airport :)

    air_code = "DEL"
    res = requests.get(url % air_code).json

    return res

def roam_nearby_places(place, price):




    t