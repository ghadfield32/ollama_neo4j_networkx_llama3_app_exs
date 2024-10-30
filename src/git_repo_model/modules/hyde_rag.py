
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.schema import Document

def contextual_retrieval(question, retriever, debug=False):
    llm = ChatOllama(model="llama3.2", temperature=0)
    hypo_prompt = f"Answer the question with background knowledge:\n\n{question}\n\nAnswer:"
    hypo_answer = llm.invoke([{"role": "user", "content": hypo_prompt}]).content

    if debug:
        print(f"Hypothetical answer generated: {hypo_answer}")

    retrieved_docs = retriever.invoke(hypo_answer)
    
    if debug:
        print(f"Number of documents retrieved: {len(retrieved_docs)}")
        
    return retrieved_docs

def main(debug=False):
    question = "What are the best practices for optimizing local file storage?"
    
    # Example documents on file storage and optimization
    sample_docs = [
        Document(page_content="Methods to optimize file storage efficiency.", metadata={"file_name": "file_optimization_guide.txt"})
    ]
    
    # Create contextual nodes and retriever
    contextual_docs = create_contextual_nodes(sample_docs, debug=debug)
    vectorstore = create_embedding_retriever(contextual_docs, debug=debug)
    retriever = vectorstore.as_retriever()
    
    # Test the contextual retrieval
    contextual_retrieval(question, retriever, debug)

if __name__ == "__main__":
    main(debug=True)

