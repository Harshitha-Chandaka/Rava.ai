import os
import time
import streamlit as st
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import WebBaseLoader
from langchain.schema import Document
from langchain_groq import ChatGroq

# Set API Key for Groq
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
llm = ChatGroq(model="llama3-8b-8192", temperature=0.2)

# Define Custom Sentence Transformer Embeddings Class
class CustomSentenceTransformer(Embeddings):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        super().__init__()
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list:
        return self.model.encode(text).tolist()

    def embed_documents(self, texts: list) -> list:
        return [self.model.encode(text).tolist() for text in texts]

embedder = CustomSentenceTransformer()

# Streamlit UI
st.title("Website-Specific Chatbot")
st.markdown("## Enter the URL of a website, and ask queries related to its content!")

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "scraped_websites" not in st.session_state:
    st.session_state.scraped_websites = {}

if "current_scrape_status" not in st.session_state:
    st.session_state.current_scrape_status = None

# Input: Website URL
url = st.text_input("Enter the website URL:")

if url:
    # Check if the website is already scraped
    if url in st.session_state.scraped_websites:
        langchain_docs = st.session_state.scraped_websites[url]["langchain_docs"]
        scrape_time = st.session_state.scraped_websites[url]["scrape_time"]
        st.success(f"Website already scraped! Scraped time: {scrape_time:.2f} seconds")
    else:
        st.info("Scraping website content...")
        scrape_start_time = time.time()
        try:
            # Load website content
            loader = WebBaseLoader(url)
            documents = loader.load()

            # Convert to LangChain documents
            langchain_docs = [
                Document(page_content=doc.page_content, metadata=doc.metadata)
                for doc in documents
            ]

            scrape_time = time.time() - scrape_start_time
            st.session_state.scraped_websites[url] = {
                "langchain_docs": langchain_docs,
                "scrape_time": scrape_time,
            }
            st.success(f"Website successfully scraped! Scraping Time: {scrape_time:.2f} seconds")
        except Exception as e:
            st.error(f"Error while scraping: {str(e)}")
            langchain_docs = []
else:
    langchain_docs = []

# Input: User Query
st.markdown("### Ask a query about the website:")
query = st.chat_input("Enter your query here:")

if query and langchain_docs:
    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(langchain_docs)

    if not split_docs:
        st.error("No valid content found in the scraped documents.")
    else:
        # Create FAISS vector store and retriever
        vector_store = FAISS.from_documents(split_docs, embedder)
        retriever = vector_store.as_retriever()
        retriever.search_kwargs = {"k": 5}

        # Retrieve relevant context
        relevant_docs = retriever.get_relevant_documents(query)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        input_size = len(context.split()) + len(query.split())
        if input_size > 30000:
            response = "Input size exceeds the allowed limit. Please refine the query or reduce website content."
        else:
            # Generate response
            try:
                prompt = (
                    f"Using the following context, answer the question in detail based strictly on the content from the website. "
                    f"Do not add any information beyond the content provided. Be as specific and relevant as possible:\n\n"
                    f"{context}\n\nQuestion: {query}\nAnswer:"
                )
                response_start_time = time.time()
                response = llm.predict(prompt)
                response_time = time.time() - response_start_time

                # Update chat history
                st.session_state.chat_history.append({"user": query, "bot": response})
                st.success(f"Response generated in {response_time:.2f} seconds.")
            except Exception as e:
                response = f"Error generating response: {str(e)}"

        # Display conversation
        st.markdown(f"**User Query:** {query}")
        st.markdown(f"**Chatbot Response:** {response}")
else:
    if not langchain_docs:
        st.error("Website content not available. Please enter a valid URL.")
