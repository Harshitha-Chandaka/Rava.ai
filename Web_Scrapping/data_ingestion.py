#Extracting text from document 
"""from langchain_community.document_loaders import TextLoader
loader = TextLoader("/workspaces/Rava.ai/Web_Scrapping/simple.txt")
text_documents = loader.load()
print(text_documents)
"""

#Extracting the text from the websites
from langchain_community.document_loaders import WebBaseLoader
import bs4
loader = WebBaseLoader(web_path = ("https://en.wikipedia.org/wiki/Football ")), bs_kwargs = dict(parse_only = bs4.SoupStrainer(
                        class_ = "mw-content-ltr mw-parser-output" ))'
text_documents = loader.load()
print(text_documents)
