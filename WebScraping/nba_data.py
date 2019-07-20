import time
import requests
import urllib.request
from bs4 import BeautifulSoup

def get_bio(soup):
    


dipo_url = https://www.basketball-reference.com/players/o/oladivi01.html
dipo_response = requests.get(dipo_url)
dipo_soup = BeautifulSoup(dipo_response.text, "html.parser")
