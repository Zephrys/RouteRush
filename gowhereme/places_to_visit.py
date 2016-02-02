import requests
import ast
from key import sabre_api_key as sabre_key

def authenticate():
    url = "https://api.sabre.com" + "/v2/auth/token"

    payload = {
        'grant_type': "client_credentials",
    }

    headers = {
        'Authorization': "Basic " + sabre_key,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    r = requests.post(url,data=payload, headers=headers)

    return ast.literal_eval(r.text)


def places_to_visit(location, price):
    url = "https://api.sabre.com/v1/lists/top/destinations?origin=%s&lookbackweeks=2&topdestinations=5"

    #  get closest large airport :)

    air_code = "DEL"
    res = requests.get(url % air_code).json

    return res

def roam_nearby_places(place, price):




    t