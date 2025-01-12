import os
import streamlit as st 
from langchain_groq import ChatGroq
from langchain import PromptTemplate
from langchain.chains import LLMChain  

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
llm  = ChatGroq(model="llama3-8b-8192", temperature=0.2)

st.title("Chatbot")
query = st.text_input("enter the question")
first_inputprompt = PromptTemplate(
    input_variables = ['name'],
    template = "Tell me everything about the products mentioned in the backticks ```{name}```"
)
chain = LLMChain(llm = llm, prompt = first_inputprompt, verbose= True )

if query:
    st.write(chain.run(query))