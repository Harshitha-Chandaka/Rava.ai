import streamlit as st
import os
from langchain_groq import ChatGroq
import requests
from bs4 import BeautifulSoup
import time
import numpy as np
from sentence_transformers import SentenceTransformer, util

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
llm = ChatGroq(model="llama3-8b-8192", temperature=0.2)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def scrape_website(url):
    scrape_start_time = time.time()
    try:
        response = requests.get(url)
        if 200 <= response.status_code < 300:
            soup = BeautifulSoup(response.text, "lxml")

            # Extracting headings, paragraphs, and links
            headings = [heading.text.strip() for heading in soup.find_all(["h1", "h2", "h3"])]
            paragraphs = [paragraph.text.strip() for paragraph in soup.find_all("p")]
            links = [link["href"] for link in soup.find_all("a", href=True)]
            ordered_lists = [[li.text.strip() for li in ol.find_all("li")] for ol in soup.find_all("ol")]
            unordered_lists = [[li.text.strip() for li in ul.find_all("li")] for ul in soup.find_all("ul")]

            scrape_end_time = time.time()
            scrape_time = scrape_end_time - scrape_start_time

            return {"headings": headings, "paragraphs": paragraphs, "links": links, "ordered_lists": ordered_lists,
                "unordered_lists": unordered_lists,}, scrape_time
        else:
            st.error(f"Failed to fetch the website. Status code: {response.status_code}")
            return None, None
    except Exception as e:
        st.error(f"An error occurred while scraping the website: {str(e)}")
        return None, None

def token_count(text):
    return len(text.split())

def limit_context(content, max_tokens=8192):
    """Limit the context to fit within token constraints."""
    limited_content = []
    token_count = 0
    for item in content:
        item_tokens = len(item.split())
        if token_count + item_tokens > max_tokens:
            break
        limited_content.append(item)
        token_count += item_tokens
    return limited_content

def semantic_search(query, website_data, top_n=3):
    content = website_data["headings"] + website_data["paragraphs"]
    if not content:
        return ["No relevant content found."]
    
    # Encoding content and query
    embeddings = embedder.encode(content, convert_to_tensor=True)
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, embeddings).squeeze()

    top_n = min(top_n, len(content))
    top_indices = np.argsort(similarities.cpu().numpy())[-top_n:][::-1]
    results = [content[i] for i in top_indices]
    
    
    return limit_context(results, max_tokens=3000)

st.title("Website-Specific Chatbot")
st.markdown("## Enter the URL of a website, and ask queries related to its content!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "scraped_websites" not in st.session_state:
    st.session_state.scraped_websites = {}

if "current_scrape_status" not in st.session_state:
    st.session_state.current_scrape_status = None

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
            st.session_state.current_scrape_status = f"Website content successfully scraped! Time taken: {scrape_time:.2f} seconds."
        else:
            website_data = None

if st.session_state.current_scrape_status:
    st.success(st.session_state.current_scrape_status)

st.markdown("### Ask a query about the website:")
query = st.chat_input("Enter your query here:")

if query:
    if website_data:
        top_results = semantic_search(query, website_data, top_n=5)  # Fetch more content
        context = " ".join(top_results)

        st.write("Final Context Sent to LLM:", context)

        input_size = token_count(context + query)

        if input_size > 30000:
            response = "Input size exceeds the allowed limit. Please refine the query or reduce website content."
        else:
            try:
                start_time = time.time()
                response = llm.invoke(f"""
                    You are a chatbot trained to answer queries about the website based on the following content:\n
                    {context}\n
                    Query: {query}\n
                    Respond with detailed and complete information. If the query is unrelated to the website, say: 'Sorry, we don't know about that information.'
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
        st.markdown(f"**User:** {query}")
        st.markdown(f"**Bot:** {response}")
    else:
        st.error("Website content not available. Please enter a valid URL.")