
from langchain_ollama import OllamaEmbeddings, ChatOllama
from modules.contextual_retrieval import create_contextual_nodes, create_embedding_retriever
from langchain.schema import Document

def contextual_retrieval(question, retriever, debug=False):
    """
    Performs contextual retrieval based on a given question and contextually enriched documents.
    
    Parameters:
    - question (str): The query or question to retrieve documents for.
    - retriever: The retriever object created from the contextual vector store.
    - debug (bool): Flag for printing debug information.
    
    Returns:
    - List[Document]: List of retrieved documents based on the contextual retriever.
    """
    # Generate a hypothetical answer to enrich the retrieval process
    llm = ChatOllama(model="llama3.2", temperature=0)
    hypo_prompt = f"Generate a detailed answer to the following question:\n\n{question}\n\nAnswer:"
    hypo_answer = llm.invoke([{"role": "user", "content": hypo_prompt}]).content

    if debug:
        print(f"Hypothetical answer generated: {hypo_answer}")

    # Retrieve documents using the contextual retriever
    retrieved_docs = retriever.invoke(hypo_answer)
    
    if debug:
        print(f"Number of documents retrieved based on hypothetical answer: {len(retrieved_docs)}")
        
    return retrieved_docs

def main(debug=False):
    """
    Main function to test the contextual retrieval.
    """
    question = "What are the recent updates in the NBA?"
    
    # Create a sample document
    sample_docs = [Document(page_content="The Boston Celtics won the NBA Finals in 2023.")]
    
    # Create contextual nodes and retriever
    contextual_docs = create_contextual_nodes(sample_docs, debug=debug)
    vectorstore = create_embedding_retriever(contextual_docs, debug=debug)
    retriever = vectorstore.as_retriever()
    
    # Test the contextual retrieval
    contextual_retrieval(question, retriever, debug)

if __name__ == "__main__":
    main(debug=True)
