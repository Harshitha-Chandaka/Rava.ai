import os
import time
import streamlit as st 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate 
from langchain.chains import create_retrieval_chain
import tempfile

# load_dotenv()

# os.environ["GROQ_API_KEY"] = os.getenv["GROQ_API_KEY"]
# groq_api_key = os.getenv("GROQ_API_KEY")

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

st.title("PDF Q&A Chatbot")

# llm = ChatGroq(groq_api_key = groq_api_key, model_name = "llama3-8b-8192")
llm = ChatGroq(model="llama3-8b-8192", temperature=0.2)

prompt = ChatPromptTemplate.from_template(
    """Answer the questions based on the provided context only. If the question is irrelevant to the document, state: 
    'This question is irrelevant to the content of the document.' 
    Provide accurate and concise responses based on the document content.
    <context>
    {context}
    <context>
    Questions: {input}"""
)

def process_pdf(uploaded_file):
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete = False, suffix = ".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.read())
            temp_pdf_path = temp_pdf.name

    try:
        loader = PyMuPDFLoader(temp_pdf_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 100)
        split_documents = text_splitter.split_documents(documents)

        # embeddings = OpenAIEmbeddings()
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(split_documents, embeddings)

        return vector_store
    
    finally:
        os.remove(temp_pdf_path)

uploaded_file = st.file_uploader("Upload your pdf here ", type = ["pdf"])

if uploaded_file:
    st.info("Uploaded File is processing")
    vector_store = process_pdf(uploaded_file)
    st.success("file has been successfully processed and embedded!")

    user_query = st.text_input("Enter your query regarding the file")

    if user_query:
        retriever = vector_store.as_retriever(search_kwargs = {"k":5})
        document_chain = create_stuff_documents_chain(llm,prompt)
        retrieval_chain = create_retrieval_chain (retriever, document_chain)

        start_time = time.time()
        response = retrieval_chain.invoke({'input':user_query})
        response_time = time.time() - start_time
        st.write(f"tome taken to generate a response: {response_time:.2f} seconds")

        answer = response.get('answer', 'no answer generated')
        st.markdown("Chatbot Response")
        st.write(answer)

        if "irrelevant" in answer.lower():
            st.warning("This query is irrelevant to the content of the document.")
        else:
            with st.expander("Revalent Document Chunks"):
                for doc in response.get("context",[]):
                    st.write(doc.page_content)
                    st.write("-------------------------------")

else:
    st.info("Please upload any document to start interaction.")