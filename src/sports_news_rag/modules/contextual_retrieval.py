
import copy
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.schema import Document  # Import the Document class

def create_contextual_nodes(documents, debug=False):
    """
    Creates contextual nodes by enriching each document with additional context.
    
    Parameters:
    - documents (List[Document]): List of LangChain Document objects.
    - debug (bool): Flag for printing debug information.
    
    Returns:
    - List[Document]: List of contextually enriched Document objects.
    """
    # Initialize the LLM
    llm = ChatOllama(model="llama3.2", temperature=0)
    
    contextual_documents = []
    for doc in documents:
        # Generate contextual information using LLM
        context_prompt = (
            f"Given the following document, generate contextual information that would help better understand its content:\n\n{doc.page_content}\n\n"
            "Contextual information:"
        )
        context = llm.invoke([{"role": "user", "content": context_prompt}]).content
        
        # Append the context to the document's metadata
        enriched_doc = copy.deepcopy(doc)
        enriched_doc.metadata["context"] = context
        contextual_documents.append(enriched_doc)
        
        if debug:
            print(f"Generated context for document: {context}")

    return contextual_documents

def create_embedding_retriever(documents, persist_directory='../../data/chroma_dbs', debug=False):
    """
    Creates a Chroma vector store retriever using contextual nodes.
    
    Parameters:
    - documents (List[Document]): List of contextually enriched Document objects.
    - persist_directory (str): Directory to persist the Chroma database.
    - debug (bool): Flag for printing debug information.
    
    Returns:
    - Chroma: Chroma vector store retriever object.
    """
    # Create embeddings with Ollama
    embeddings = OllamaEmbeddings(model="llama3.2")
    
    # Create the Chroma vector store
    if debug:
        print(f"Creating vector store with {len(documents)} contextually enriched documents...")
        
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    if debug:
        print(f"Vector store created at {persist_directory}")
    
    return vectorstore

def main(debug=True):
    """
    Main function to test the contextual retrieval pipeline.
    """
    # Sample documents for testing
    sample_docs = [Document(page_content="The Boston Celtics won the NBA Finals in 2023.")]
    
    # Create contextual nodes
    contextual_docs = create_contextual_nodes(sample_docs, debug=debug)
    
    # Create and test the vector store
    vectorstore = create_embedding_retriever(contextual_docs, debug=debug)
    
    # Output a message indicating successful creation of contextual retriever
    if debug:
        print(f"Successfully created contextual retriever with {len(contextual_docs)} contextually enriched documents.")

if __name__ == "__main__":
    main(debug=True)
