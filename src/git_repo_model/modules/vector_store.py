from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
import os 

def create_vectorstore(documents, persist_directory='../../../data/chroma_dbs', debug=False):
    # Ensure the persistence directory exists
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)
        if debug:
            print(f"Created new persistence directory at {persist_directory}")

    embeddings = OllamaEmbeddings(model="llama3.2")
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    if debug:
        print(f"Vector store created at {persist_directory} with {len(documents)} documents.")
    return vectorstore


def create_pre_ingested_vectorstore(site_name, documents):
    # Create directory if it doesn't exist
    directory = f"../../data/vectorstores/{site_name.lower()}"
    os.makedirs(directory, exist_ok=True)
    
    # Create the vector store
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
    site_name = "local_repo_files"
    documents = [Document(page_content="This is a sample document for NFL data.")]
    create_pre_ingested_vectorstore(site_name, documents)

if __name__ == "__main__":
    main(debug=True)
