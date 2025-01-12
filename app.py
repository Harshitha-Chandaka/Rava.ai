import os
import streamlit as st 
from langchain_groq import ChatGroq
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
llm  = ChatGroq(model="llama3-8b-8192", temperature=0.2)

query = st.text_input("enter the question")
if query: 
    result=llm.invoke(f"""
        You are good at narrating a story in different zoners like comic, moral stories, horror etc .\
        Provide information based on the query below, which is enclosed in triple backticks:
        ```{query}```
        """).content
    st.write(result)



# f"You know about the Rava.ai comany and  the founder of this company is Kiran Babu and Sudha Reddy. \
#     This rava.ai is a marketing co-pilot which is located in Madhapur, Hyderabad, designed to assist startups and small to medium-sized businesses in streamlining \
#     their marketing efforts. The platform offers tools for strategy planning, SEO optimization, content creation, social\
#     media management, and more, aiming to enhance personalization and efficiency in marketing campaigns. There is nearly \
#     11-20 employees are working here and Rava.ai's mission is to make AI accessible to businesses of all sizes, driving innovation and efficiency across industries.\
#     This comapany providing some ai free tools and provide AI powered solutions. You have to\
#     answer the queries of the several clients you have.\
#     query:'''{query}'''

    # f"""
    #     You are well known about some Indian songs and singers.
    #     Provide information based on the query below, which is enclosed in triple backticks:
    #     ```{query}```
    #     """