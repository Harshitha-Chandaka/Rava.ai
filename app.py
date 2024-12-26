import os
import streamlit as st 
from langchain_groq import ChatGroq
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
llm  = ChatGroq(model="llama3-8b-8192", temperature=0.2)
# prompt ="Tell me a joke"
fruit = "Mango"
result = llm.invoke(f"You are an experienced comedian. You will be given a fruit, on which you have to make a joke.\n\nFruit: {fruit}").content
st.write(result)