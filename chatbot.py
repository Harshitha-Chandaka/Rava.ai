import streamlit as st
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


def chatbot_response(user_input):
    user_input = user_input.lower()
    for keyword, key in query_mapping.items():
        if keyword in user_input:
            return company_data[key]
    return "We don't have information on that :("

st.title("**Hello!! I'm your Rava.ai Chatbot **")
st.subheader("I'm here to clear your doubts about Rava.ai company....")

user_input = st.text_input("Enter your question..")
if st.button("submit"):
    if user_input.strip():
        result = chatbot_response(user_input)
        st.write(f"**Chatbot:** {result}") 
    else:
        st.warning("Please enter a valid question")