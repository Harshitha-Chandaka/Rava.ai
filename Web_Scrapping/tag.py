import requests
from bs4 import BeautifulSoup

url = "https://webscraper.io/test-sites/e-commerce/allinone"
req = requests.get(url)
soup = BeautifulSoup(req.text, 'lxml')
# tag = soup.find('dev')
# tag = soup.find('header')  
# if tag:
#     atb = tag.attrs
#     print(atb['role'])  
# else:
#     print("Tag not found.")

# tag = soup.div.p.string  #For paragraph 
# print(tag.string)
# print(tag)

tag = soup.header.div.a.button.span.string # header tages 
print(tag)