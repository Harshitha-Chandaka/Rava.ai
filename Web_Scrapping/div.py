import re
import requests
from bs4 import BeautifulSoup

url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets"
req = requests.get(url)
soup = BeautifulSoup(req.text, "lxml")

boxes = soup.find_all("div", class_ = "col-md-4 col-xl-4 col-lg-4")
print(len(boxes))

box = soup.find_all("div", class_ = "col-md-4 col-xl-4 col-lg-4")[3]
print(len(boxes)) 
name = box.find("a").text
print(name)

desc = box.find("p", class_ = "description")
print(desc.text)