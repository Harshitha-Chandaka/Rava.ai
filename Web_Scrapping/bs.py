import requests
from bs4 import BeautifulSoup

# url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets"
url = "https://rava.ai/"
req = requests.get(url)

soup = BeautifulSoup(req.text,"html.parser")

# soup = BeautifulSoup(req.content, "html.parser")
print(soup.string)

# price = (soup.find("h4",{"class": "price float-end card-title pull-right"}))
# print(price.string)

# price  = soup.find_all("h4", class_ = "price float-end card-title pull-right")
# # print(price)
# # print('\n')
# print(len(price))
# for i in price:
#     print(i.text)