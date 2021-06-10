import requests
from bs4 import BeautifulSoup as bs

province = "Nhatrang"
url = "https://www.weather-forecast.com/locations/{0}/forecasts/latest".format(province)
r = requests.get(url)
print(r.content)











