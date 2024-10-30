from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.schema import Document  # Import the Document class

def corrective_rag(question, retrieved_docs, debug=False):
    # Convert the list of dicts to Document objects if necessary
    if not all(isinstance(doc, Document) for doc in retrieved_docs):
        retrieved_docs = [Document(page_content=doc["page_content"]) for doc in retrieved_docs]

    llm = ChatOllama(model="llama3.2", temperature=0)
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    initial_prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    initial_answer = llm.invoke([{"role": "user", "content": initial_prompt}]).content

    if debug:
        print(f"Initial answer generated: {initial_answer}")

    max_iterations = 2
    for i in range(max_iterations):
        verify_prompt = f"Context: {context}\n\nAnswer: {initial_answer}\n\nIs the answer fully supported by the context? Identify any inaccuracies."
        verification = llm.invoke([{"role": "user", "content": verify_prompt}]).content

        if "no inaccuracies" in verification.lower():
            if debug:
                print(f"No inaccuracies found. Answer is verified on iteration {i + 1}.")
            break
        else:
            refine_prompt = f"Context: {context}\n\nThe initial answer may have inaccuracies: {verification}\n\nQuestion: {question}\n\nProvide a corrected answer:"
            initial_answer = llm.invoke([{"role": "user", "content": refine_prompt}]).content

    return initial_answer

def main(debug=False):
    # Sample usage for testing
    question = "Who won the NBA Finals in 2023?"
    # Use a list of Document objects instead of dictionaries for the retrieved documents
    retrieved_docs = [Document(page_content="The Boston Celtics won the NBA Finals in 2024.")]
    answer = corrective_rag(question, retrieved_docs, debug=debug)
    if debug:
        print(f"Final corrected answer: {answer}")

if __name__ == "__main__":
    main(debug=True)
