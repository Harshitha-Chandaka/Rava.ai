import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets"
req = requests.get(url)
soup = BeautifulSoup(req.text, "lxml")
# data = soup.find_all(["h4","a","p"])
# data = soup.find_all(string = "Galaxy Tab 3")
# data = soup.find_all(string = re.compile("Galaxy"))
# print(data)
# print(len(data))

names = soup.find_all("a", class_ = "title")
product_name = []
for i in names:
    name = i.text
    product_name.append(name)

print(product_name)
print()

prices = soup.find_all("h4", class_ = 'price float-end card-title pull-right')
price_list = []
for i in prices:
    price = i.text
    price_list.append(price)
print(price_list)
print()

desc = soup.find_all("p", class_ = "description")
desc_list = []
for i in desc:
    des = i.text
    desc_list.append(des)
print(desc_list)
print()

reviews = soup.find_all("p", class_ = "review-count float-end")
rev_list = []
for i in reviews:
    rev = i.text
    rev_list.append(rev)
print(rev_list)

df = pd.DataFrame({"Product name":product_name, "Product price":price_list, "Product description":desc_list, "Product Reviews":rev_list })
# print(df)
df.to_csv("Product_details.csv")