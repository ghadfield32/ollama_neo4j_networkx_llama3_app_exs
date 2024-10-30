from modules.hyde_rag import contextual_retrieval
from modules.corrective_rag import corrective_rag
from modules.web_search import tavily_search
from modules.self_rag import self_rag  # Include the self_rag module for refinement
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.schema import Document
import streamlit as st

def evaluate_confidence(answer, debug=False):
    """Evaluate the confidence of an answer using a language model."""
    llm = ChatOllama(model="llama3.2", temperature=0)
    eval_prompt = (
        f"Evaluate the confidence level (on a scale of 1-10) of the following answer being correct, "
        f"fully supported by reliable sources, and free from contradictions or inaccuracies:\n\n{answer}\n\n"
        "Confidence Score:"
    )
    confidence_score = llm.invoke([{"role": "user", "content": eval_prompt}]).content
    try:
        score = int(confidence_score.strip())
    except ValueError:
        score = 5  # Default to medium confidence if the evaluation fails
    if debug:
        print(f"Confidence score evaluated: {score}")
    return score

def decide_and_answer(question, retriever, progress_bar=None, progress_status=None, debug=False):
    """Generate answers using RAG and Tavily, and decide the best answer with self-refinement."""
    progress_step = 0.25

    # Step 1: Use contextual retrieval to get documents and generate an initial RAG-based answer
    if progress_status:
        progress_status.text("Step 1/4: Running HyDE retrieval...")
    retrieved_docs = contextual_retrieval(question, retriever, debug)
    if progress_bar:
        progress_bar.progress(progress_step)

    # Step 2: Generate a corrective RAG-based answer
    if progress_status:
        progress_status.text("Step 2/4: Generating a corrective RAG answer...")
    rag_answer = corrective_rag(retrieved_docs, debug)
    rag_refined_answer = self_rag(question, rag_answer, debug)  # Refine RAG answer with self-rag
    rag_confidence = evaluate_confidence(rag_refined_answer, debug)
    progress_step += 0.25
    if progress_bar:
        progress_bar.progress(progress_step)

    # Step 3: Use Tavily search to generate an answer
    if progress_status:
        progress_status.text("Step 3/4: Running Tavily search for additional context...")
    tavily_context = tavily_search(question, debug)
    tavily_prompt = f"Context: {tavily_context}\n\nQuestion: {question}\n\nAnswer:"
    llm = ChatOllama(model="llama3.2", temperature=0)
    tavily_initial_answer = llm.invoke([{"role": "user", "content": tavily_prompt}]).content
    tavily_refined_answer = self_rag(question, tavily_initial_answer, debug)  # Refine Tavily answer with self-rag
    tavily_confidence = evaluate_confidence(tavily_refined_answer, debug)
    progress_step += 0.25
    if progress_bar:
        progress_bar.progress(progress_step)

    # Step 4: Decision mechanism to choose the final answer based on confidence scores
    if progress_status:
        progress_status.text("Step 4/4: Making the final decision...")
    if rag_confidence > tavily_confidence:
        final_answer = rag_refined_answer
        source = "RAG-based response"
    elif tavily_confidence > rag_confidence:
        final_answer = tavily_refined_answer
        source = "Tavily-based response"
    else:
        # Combine answers if confidence scores are similar
        combined_prompt = (
            f"Here are two potential answers to the question:\n\n"
            f"Answer 1 (RAG-based):\n{rag_refined_answer}\n\n"
            f"Answer 2 (Tavily-based):\n{tavily_refined_answer}\n\n"
            f"Based on these, provide the best possible answer to the question: {question}"
        )
        final_answer = llm.invoke([{"role": "user", "content": combined_prompt}]).content
        source = "Combined response"

    if debug:
        print(f"Selected final answer from: {source}")
    return final_answer

def main(debug=False):
    question = "What are the best methods to organize a large local file repository for efficiency?"
    sample_docs = [
        Document(page_content="This is a sample document on file organization best practices.", metadata={"file_name": "organization_best_practices.txt"})
    ]
    vectorstore = create_embedding_retriever(create_contextual_nodes(sample_docs, debug=debug), debug=debug)
    retriever = vectorstore.as_retriever()

    # Streamlit progress bar and status
    progress_bar = st.progress(0)
    progress_status = st.empty()

    final_answer = decide_and_answer(question, retriever, progress_bar, progress_status, debug)
    st.write(f"Final answer selected: {final_answer}")

if __name__ == "__main__":
    main(debug=True)

