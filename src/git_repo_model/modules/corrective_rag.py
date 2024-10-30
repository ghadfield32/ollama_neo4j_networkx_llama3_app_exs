
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.schema import Document

def corrective_rag(retrieved_docs, debug=False):
    """
    Analyze and make recommendations based on retrieved file chunks.
    """
    llm = ChatOllama(model="llama3.2", temperature=0)
    recommendations = []

    for doc in retrieved_docs:
        prompt = (
            f"Based on the following content:\n\n{doc.page_content}\n\n"
            "Suggest improvements for file structure, storage efficiency, and best practices."
        )
        recommendation = llm.invoke([{"role": "user", "content": prompt}]).content
        recommendations.append(Document(page_content=recommendation, metadata=doc.metadata))

        if debug:
            print(f"Recommendation for {doc.metadata.get('file_name', 'unknown')}: {recommendation}")

    return recommendations

def main(debug=False):
    # Sample document on file structure
    retrieved_docs = [
        Document(page_content="This document covers tips on file organization.", metadata={"file_name": "file_organization_guide.txt"})
    ]
    recommendations = corrective_rag(retrieved_docs, debug=debug)
    
    if debug:
        for recommendation in recommendations:
            print(f"Final recommendation for {recommendation.metadata.get('file_name', 'unknown')}: {recommendation.page_content}")

if __name__ == "__main__":
    main(debug=True)


