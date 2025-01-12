import requests
from bs4 import BeautifulSoup
import pandas as pd

# url = "https://www.indiabix.com/verbal-ability/change-of-voice/"
url = "https://www.geeksforgeeks.org/page/1/"
req = requests.get(url)
soup = BeautifulSoup(req.text, "lxml")
titles = soup.find_all("div", attrs = {"class", "head"})
print(titles)