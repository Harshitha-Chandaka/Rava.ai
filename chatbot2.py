import streamlit as st
import json
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

model = SentenceTransformer('all-MiniLM-L6-v2')

with open('company_data.json', 'r') as file:
    company_data = json.load(file)

query_mapping = {
    "founder": "Co-Founder & CEO",
    "co-founder": "Co-Founder & CEO",
    "ceo": "Co-Founder & CEO",
    "employees": "Number of Employees",
    "headquarters": "Headquarters",
    "mission": "Mission/Aim",
    "services": "Services Offered",
    "free tools": "Free Tools",
    "work culture": "Work Culture",
    "about": "About Company"
}

def is_query_relevant(user_input, company_data):
    input_terms = set(user_input.lower().split())
    data_terms = set(" ".join(company_data.values()).lower().split())
    return bool(input_terms & data_terms)

for key, value in company_data.items():
    dense_data = {key: model.encode(value)}

def hybrid_search(user_input):
    user_input_lower = user_input.lower()
    
    # 1. Sparse Search
    for keyword, key in query_mapping.items():
        if keyword in user_input_lower:
            return company_data[key]
    
    # 2. Dense Search
    user_embedding = model.encode(user_input)
    best_match = None
    lowest_distance = float('inf')
    for key, embedding in dense_data.items():
        distance = cosine(user_embedding, embedding)
        if distance < lowest_distance:     #Comparing the distance between the vectors
            lowest_distance = distance
            best_match = key
    
    if not is_query_relevant(user_input, company_data):
        return "Sorry, I don't know."
    
    # Threshold for dense search similarity
    if lowest_distance < 0.2:  # 0 for perfectly similar and 1 for completely dissimilar
        return company_data[best_match]
    else:
        return "We don't have information on that :("

st.title("**Hello!! I'm your Rava.ai Chatbot**")
st.subheader("I'm here to clear your doubts about Rava.ai company...")

user_input = st.text_input("Enter your question..")
if st.button("Submit"):
    if user_input.strip(): #considers only non-whitespaces
        result = hybrid_search(user_input)
        st.write(f"**Chatbot:** {result}")
    else:
        st.warning("Please enter a valid question.")
