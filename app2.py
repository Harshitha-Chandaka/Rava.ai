import os
import streamlit as st 
from langchain_groq import ChatGroq
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
llm  = ChatGroq(model="llama3-8b-8192", temperature=0.2)

st.title("Welcome to Content Genrative Model!!")
if 'result' not in st.session_state:
    st.session_state.result = None
if 'feedback' not in st.session_state:
    st.session_state.feedback = None

#st.text("Enter your prompt:")
prompt = st.text_input("Enter your prompt:", "")
#"Tell me a joke"

if st.button("Generate Response"):
    if prompt.strip():
        st.session_state.result = llm.invoke(prompt).content
        st.session_state.feedback = None
    else:
        st.warning("Please enter the valid prompt to generate a response")

if st.session_state.result:
    st.write("**Generated Response**")
    st.write(st.session_state.result)

    feedback = st.radio("Did you like this content?:",
                            ['Select an option', 'Liked', 'Disliked'],
                            index = 0,
                            key = 'feedback_radio'
                        )
    if feedback == 'Liked':
        st.success("Thank you for your feedback :)")
        st.session_state.feedback = "Liked"
    elif feedback:
        st.error("Sorry to hear that! We will try to improve :( ")
        st.session_state.feedback = "Disliked"
    elif feedback == 'Select an option':
        st.warning("Please select an option to provide feedback.")

    