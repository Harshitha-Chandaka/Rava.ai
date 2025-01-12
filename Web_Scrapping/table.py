import requests
from bs4 import BeautifulSoup

url = "https://ticker.finology.in/"
req = requests.get(url)
soup = BeautifulSoup("req.text", "lxml")

table = soup.find_all("table", class_ = "table table-sm table-hover screenertable")
print(table)

headers = table.find_all("th")
print(headers)
