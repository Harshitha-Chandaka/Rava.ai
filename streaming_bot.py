import streamlit as st 
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

groq_api_key = st.secrets["GROQ_API_KEY"]
llm = ChatGroq(model="llama3-8b-8192", temperature=0.7)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title = "Streaming Bot")
st.title("Streaming Bot")

# groq_api_key = os.getenv("GROQ_API_KEY")
# if not groq_api_key:
    # raise ValueError("GROQ_API_KEY is not set in your environment variables.")

#Response from the LLM
def generate_response(user_input, chat_history):
    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model="llama3-8b-8192", temperature=0.7, api_key=groq_api_key)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "chat_history": chat_history,
        "user_question": user_input

    })

#Converation
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)

#INput from the user
user_input = st.chat_input("Your Query..")

if user_input is not None and user_input != '':
    st.session_state.chat_history.append(HumanMessage(user_input))

    with st.chat_message("Human"):
        st.markdown(user_input)

    with st.chat_message("AI"):
        ai_response = generate_response(user_input, st.session_state.chat_history)
        st.markdown(ai_response)
    st.session_state.chat_history.append(AIMessage(ai_response))
