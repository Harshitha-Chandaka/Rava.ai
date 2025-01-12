import streamlit as st
import os
from langchain_groq import ChatGroq
import requests
from bs4 import BeautifulSoup
import time

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
llm  = ChatGroq(model="llama3-8b-8192", temperature=0.2)

def scrape_website(url):
    scrape_start_time = time.time() 
    try:
        response = requests.get(url)
        if 200 <= response.status_code < 300: 
            soup = BeautifulSoup(response.text, "lxml")

            # Extract headings
            headings = soup.find_all(["h1", "h2", "h3"])
            head_list = [heading.text.strip() for heading in headings]

            # Extract paragraphs
            paragraphs = soup.find_all("p")
            para_list = [paragraph.text.strip() for paragraph in paragraphs]

            # Extract links
            links = soup.find_all("a", href=True)
            link_list = [link["href"] for link in links]

            scrape_end_time = time.time()
            scrape_time = scrape_end_time - scrape_start_time

            return {"headings": head_list, "paragraphs": para_list, "links": link_list},scrape_time
        else:
            st.error(f"Failed to fetch the website. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred while scraping the website: {str(e)}")
        return None


#Adding the history to this chatbot
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "scraped_websites" not in st.session_state:
    st.session_state.scraped_websites = {}

if "current_scrape_status" not in st.session_state:
    st.session_state.current_scrape_status = None

def token_count(text):
    return len(text.split()) #counting number of tockens in this text


st.title("Website-Specific Chatbot")
st.markdown("## Enter the URL of a website, and ask queries related to its content!")

url = st.text_input("Enter the website URL:")

if url:
    if url in st.session_state.scraped_websites:
        website_data = st.session_state.scraped_websites[url]["data"]
        scrape_time = st.session_state.scraped_websites[url]["scrape_time"]
        if st.session_state.current_scrape_status is None or "successfully scraped" in st.session_state.current_scrape_status:
            st.session_state.current_scrape_status = f"The website has already been scraped. Scrape time: {scrape_time:.2f} seconds."
    else:
        st.info("Scraping website content...")
        website_data, scrape_time = scrape_website(url)

        if website_data:
            st.session_state.scraped_websites[url] = {"data": website_data, "scrape_time": scrape_time}
            st.session_state.current_scrape_status = f"Website content successfully scraped! Time taken: {scrape_time:.2f} seconds"
        else:
            website_data = None

if st.session_state.current_scrape_status:
    st.success(st.session_state.current_scrape_status)


st.markdown("### Ask a query about the website:")
query = st.chat_input("Enter your query here:")


# if query and website_data:
if query:
    max_headings = 50
    max_paragraphs= 30
    max_links = 30

        # limited_headings = st.session_state.website_data['headings'][:max_headings]
        # limited_paragraphs = st.session_state.website_data["paragraphs"][:max_paragraphs]
        # limited_links = st.session_state.website_data["links"][:max_links]

    limited_headings = website_data['headings'][:max_headings]
    limited_paragraphs = website_data["paragraphs"][:max_paragraphs]
    limited_links = website_data["links"][:max_links]

    context = (
        f"Headings: {limited_headings}\n"
        f"Paragraphs: {limited_paragraphs}\n"
        f"Links: {limited_links}\n"
    )
    input_size = token_count(context + query)

    if input_size > 30000:
        response = "Input size exceeds the allowed limit. Please refine the query or reduce website content."

    else:
        start_time = time.time()

        try:
            response = llm.invoke(f"""
                You are a chatbot trained to answer queries about the website based on the following content:\n
                {context}\n
                Query: {query}\n
                If the query is unrelated to the website, respond with 'Sorry, we don't know about that information.'
            """).content
        except Exception as e:
            if "rate_limit_exceeded" in str(e):
                response = "Rate limit reached. Please wait for some time before trying again."
            else:
                response = f"An error occurred: {str(e)}"

        end_time = time.time()
        response_time = end_time - start_time
        st.write(f"Time taken to generate the response: {response_time:.2f} seconds")

    st.session_state.chat_history.append({"user": query, "bot": response})

    st.write(f"**User:** {query}")
    st.write(f"**Bot:** {response}")



