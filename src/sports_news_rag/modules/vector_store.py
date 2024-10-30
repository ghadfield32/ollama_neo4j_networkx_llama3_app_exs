from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.schema import Document  # Import the Document class
import os

# Define the home directory for the project
HOME_DIR = "/workspaces/custom_ollama_docker"
DATA_DIR = os.path.join(HOME_DIR, "data", "vectorstores")

def create_vectorstore(documents, site_name="nba", debug=False):
    # Specify embedding function
    embeddings = OllamaEmbeddings(model="llama3.2")
    persist_directory = os.path.join(DATA_DIR, site_name)
    os.makedirs(persist_directory, exist_ok=True)
    if debug:
        print(f"Creating vector store with {len(documents)} documents at {persist_directory}...")

    # Create Chroma vector store with embeddings
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return vectorstore

def create_pre_ingested_vectorstore(site_name, documents):
    directory = f"../../../data/vectorstores/{site_name.lower()}"
    os.makedirs(directory, exist_ok=True)

    # Initialize the embedding function
    embeddings = OllamaEmbeddings(model="llama3.2")
    vectorstore = Chroma.from_documents(documents, embedding=embeddings, persist_directory=directory)
    print(f"Vector store for {site_name} created and saved at {directory}")

def main(debug=False):
    # Use a list of high-quality Document objects instead of dictionaries
    sample_docs = [Document(page_content="This is a high-quality sample document for testing.")]
    vectorstore = create_vectorstore(sample_docs, debug=debug)
    if debug:
        print("Vector store successfully created.")
        
    # Example usage:
    site_name = "ESPN"
    documents = [Document(page_content="This is a sample document for NFL data.")]
    create_pre_ingested_vectorstore(site_name, documents)

if __name__ == "__main__":
    main(debug=True)
