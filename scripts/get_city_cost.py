import requests
from bs4 import BeautifulSoup

url = "http://www.priceoftravel.com/world-cities-by-price-backpacker-index/"

def main():
    soup = BeautifulSoup(requests.get(url).text, "lxml")

    cities = {}

    cities_fetched = soup('div', {'id': 'bpi_row1'} )

    for city in cities_fetched:
        c_name = city('div', {'class': 'name'})[0].text

        # saves just the names of cities as of now
        c_name = c_name.split(',')[0]

        c_price = city('div', {'class': 'price'})[0].text[1:]

        #  save this in the db as required :-)
        print(c_name, c_price)

if __name__ == "__main__":
    main()