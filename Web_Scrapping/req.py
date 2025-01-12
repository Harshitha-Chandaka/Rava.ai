import requests
from bs4 import BeautifulSoup

url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets"
req = requests.get(url)
print(req.status_code)
# print(req.text, "lxml")
# print(req.content, "html_parser")