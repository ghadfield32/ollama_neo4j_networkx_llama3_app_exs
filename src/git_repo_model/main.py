
# Import necessary modules for the main workflow
from modules.data_crawling import crawl_and_ingest
from modules.vector_store import create_vectorstore
from modules.decision_mechanism import decide_and_answer
from modules.fact_checker import final_fact_check
from modules.hyde_rag import contextual_retrieval  # Use the new contextual retrieval function
from modules.corrective_rag import corrective_rag  # Import corrective_rag function for code improvements
from modules.git_data_crawling import load_github_repo  # Import the GitHub repo loader
from modules.hyde_rag import contextual_retrieval

def run_rag_pipeline(data_source, repo_path=None, repo_url=None, question="What are the best practices for organizing a code repository?", debug=False):
    """
    Run the RAG pipeline by loading documents from either a local directory or GitHub repository,
    creating a vector store, generating recommendations, performing fact-checking, and presenting the final answer.
    
    Parameters:
    - data_source (str): "Local" or "Git"
    - repo_path (str, optional): Local directory path (required if data_source is "Local")
    - repo_url (str, optional): GitHub repository URL (required if data_source is "Git")
    - question (str): The question for which recommendations are generated
    - debug (bool): Enable debug outputs for step-by-step tracing
    """
    # Define the file types for filtering
    file_types = [".py", ".md", ".csv", ".ipynb", ".html", ".json", ".yaml", ".r", ".cpp", ".java", ".scala", ".sql"]

    # Step 1: Load documents based on the selected data source
    if data_source == "Local":
        if not repo_path:
            raise ValueError("Local directory path must be provided for Local source.")
        documents = crawl_and_ingest(repo_path, file_types, debug)
    elif data_source == "Git":
        if not repo_url:
            raise ValueError("GitHub repository URL must be provided for Git source.")
        documents = load_github_repo(repo_url, file_types, debug)
    else:
        raise ValueError("Invalid data source selected. Choose either 'Local' or 'Git'.")
    
    # Display loaded documents for debugging
    if debug:
        print(f"Total documents loaded: {len(documents)}")
    
    # Step 2: Create a vector store and a retriever
    vectorstore = create_vectorstore(documents, debug=debug)
    retriever = vectorstore.as_retriever()
    
    # Step 3: Retrieve relevant documents using contextual retrieval
    retrieved_docs = contextual_retrieval(question, retriever, debug)
    
    # Step 4: Generate recommendations using corrective RAG
    recommendations = corrective_rag(retrieved_docs, debug=debug)
    
    # Display initial recommendations
    if debug:
        for rec in recommendations:
            print(f"Initial recommendation for {rec.metadata.get('file_name', 'unknown')}:\n{rec.page_content}")
    
    # Step 5: Perform a final fact-check on the recommendations
    initial_answer = " ".join([rec.page_content for rec in recommendations])
    corrected_answer = final_fact_check(question, initial_answer, retriever, debug=debug)
    
    # Display the fact-checked answer for debugging
    if debug:
        print(f"Corrected answer after final fact-check:\n{corrected_answer}")
    
    # Step 6: Decide and return the best answer
    final_answer = decide_and_answer(question, retriever, debug=debug)
    return final_answer

def main():
    # Set the data source and parameters for testing
    data_source = "Git"  # Set to "Local" or "Git" as needed
    question = "Can you help me with how to make a streamlit app out of the data in the data section?"
    
    # Define paths based on data source
    if data_source == "Local":
        repo_path = "../../"  # Example local directory path
        repo_url = None
    elif data_source == "Git":
        repo_path = None
        repo_url = "https://github.com/ghadfield32/coach_analysis"  # Example GitHub URL
    else:
        print("Invalid data source selected. Please choose 'Local' or 'Git'.")
        return
    
    # Run the RAG pipeline and print the final answer
    try:
        final_answer = run_rag_pipeline(data_source, repo_path=repo_path, repo_url=repo_url, question=question, debug=True)
        print("\nFinal Answer:")
        print(final_answer)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
