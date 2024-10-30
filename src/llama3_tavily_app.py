
import streamlit as st
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)

# Set up API keys
tavily_token = os.getenv("TAVILY_API_KEY")

# Set up the local LLM model
local_llm = "llama3.2"
llm = ChatOllama(model=local_llm, temperature=0)

# Function to retrieve documents from NBA website and create retriever
@st.cache_resource
def setup_retriever():
    loader = WebBaseLoader("https://www.nba.com/")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    embeddings = OllamaEmbeddings(model=local_llm)
    vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)
    return vectorstore.as_retriever()

# Function to perform RAG-based responses
def rag_chain(question, retriever):
    retrieved_docs = retriever.invoke(question)
    formatted_context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    return llm.invoke([{"role": "user", "content": f"Question: {question}\n\nContext: {formatted_context}"}]).content

# Set up Tavily Search Retriever
tavily_retriever = TavilySearchAPIRetriever(k=3)

# Set up a search chain with Tavily integration
prompt_template = ChatPromptTemplate.from_template(
    """Answer the question based only on the context provided. Do not make up additional information.
    
    Context: {context}

    Question: {question}"""
)
search_chain = (
    {"context": tavily_retriever | (lambda docs: "\n\n".join([f"Source {i+1} (URL: {doc.metadata.get('source')}):\n{doc.page_content}" for i, doc in enumerate(docs)])), 
     "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

# Streamlit UI
st.title("Web-Integrated AI Assistant")
st.write("This assistant can respond to your queries using information retrieved from the web.")

# Input field for user question
user_question = st.text_input("Ask a question:", "Who was the number 1 pick in the 2024 NBA Draft?")

# Buttons to select RAG-based or Tavily-based responses
if st.button("RAG Response"):
    retriever = setup_retriever()
    response = rag_chain(user_question, retriever)
    st.subheader("RAG-based Response")
    st.write(response)

if st.button("Tavily Search Response"):
    search_response = search_chain.invoke(user_question)
    st.subheader("Tavily Search-based Response")
    st.write(search_response)
