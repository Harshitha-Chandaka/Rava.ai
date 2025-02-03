import os
import time
import tempfile
import streamlit as st
from bs4 import BeautifulSoup
import requests
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_groq import ChatGroq

# Set API key for Groq
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# Streamlit app title and UI
st.title("## Streaming_Bot")
st.markdown("Select input and upload your content")

# Input selection
input_type = st.radio("Choose your input type:", ["PDF", "Website URL"])
groq_model = st.radio(
    "Select a Groq Model:",
    [
        "llama-3.1-70b-versatile", "llama-3.1-8b-instant",
        "lama-3.2-11b-vision-preview", "llama-3.2-1b-preview",
        "llama-3.2-3b-preview", "llama-3.3-70b-specdec", "llama-3.3-70b-versatile",
        "llama-guard-3-8b", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"
    ]
)

# Load the selected language model
llm = ChatGroq(model=groq_model, temperature=0.2)

# Initialize session state for website content
if "scraped_websites" not in st.session_state:
    st.session_state.scraped_websites = {}

documents = []
query = None

# Function to handle PDF processing
# def process_pdf(uploaded_pdf):
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
#             temp_pdf.write(uploaded_pdf.read())
#             temp_pdf_path = temp_pdf.name

#         # Load and process PDF content
#         loader = PyMuPDFLoader(temp_pdf_path)
#         loaded_documents = loader.load()
#         pdf_text = " ".join([doc.page_content for doc in loaded_documents])

#         # Split into chunks
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#         return text_splitter.split_documents([Document(page_content=pdf_text, metadata={"source": uploaded_pdf.name})])

#     except Exception as e:
#         st.error(f"Error processing PDF: {e}")
#         return []
#     finally:
#         if os.path.exists(temp_pdf_path):
#             os.remove(temp_pdf_path)


def process_pdf(uploaded_pdf):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_pdf.read())
            temp_pdf_path = temp_pdf.name

        # Load and process PDF content
        loader = PyMuPDFLoader(temp_pdf_path)
        loaded_documents = loader.load()

        # Split into chunks with metadata
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.split_documents(loaded_documents)
        return documents

    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return []
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

# Function to scrape and process website content
def process_website(url):
    try:
        if url in st.session_state.scraped_websites:
            return st.session_state.scraped_websites[url]["documents"], st.session_state.scraped_websites[url]["scrape_time"]

        # Scrape website content
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            st.error(f"Error: Received status code {response.status_code}")
            return [], 0

        soup = BeautifulSoup(response.text, "html.parser")
        content = " ".join([tag.get_text() for tag in soup.find_all(["p", "h1", "h2", "h3", "li", "ol", "ul", "td"])])

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.split_documents([Document(page_content=content, metadata={"source": url})])

        scrape_time = time.time() - scrape_start_time
        st.session_state.scraped_websites[url] = {"documents": documents, "scrape_time": scrape_time}
        return documents, scrape_time

    except Exception as e:
        st.error(f"Error scraping website: {e}")
        return [], 0


# Handle PDF input
if input_type == "PDF":
    uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_pdf:
        st.info("Processing your PDF...")
        documents = process_pdf(uploaded_pdf)
        st.success(f"PDF processed successfully! Found {len(documents)} chunks.")

# Handle Website URL input
elif input_type == "Website URL":
    url = st.text_input("Enter the website URL:")
    if url:
        st.info("Scraping website content...")
        scrape_start_time = time.time()
        documents, scrape_time = process_website(url)
        if documents:
            st.success(f"Website successfully scraped in {scrape_time:.2f} seconds. Found {len(documents)} chunks.")

# Query handling
if documents:
    query = st.text_input("Enter your query:")
    if query:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(documents, embeddings)
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})

        relevant_docs = retriever.invoke(query)
        st.write(relevant_docs)

        # Extract context and page numbers
        context = "\n\n".join(
            [f"(Page {doc.metadata.get('page', 'Unknown')}): {doc.page_content}" for doc in relevant_docs]
        )[:3000]

        unique_pages = sorted(set(doc.metadata.get('page', 'Unknown') for doc in relevant_docs if 'page' in doc.metadata))

        try:
            prompt = (
                f"Using the following context, answer the question in detail based strictly on the content provided. "
                f"Do not add any information beyond the content provided. Be as specific and relevant as possible:\n\n"
                f"{context}\n\nQuestion: {query}\nAnswer:"
            )
            response = llm.invoke(prompt).content
            st.markdown("### Chatbot Response:")
            st.success(response)

            # Display relevant pages
            st.markdown("### Relevant Pages:")
            st.markdown(", ".join(f"Page {page}" for page in unique_pages))

        except Exception as e:
            st.error(f"Error generating response: {e}")
