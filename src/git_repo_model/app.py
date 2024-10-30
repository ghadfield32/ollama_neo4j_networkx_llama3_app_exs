
import streamlit as st
from modules.decision_mechanism import decide_and_answer
from modules.vector_store import create_vectorstore
from modules.data_crawling import crawl_and_ingest
from modules.git_data_crawling import load_github_repo
from fact_checker import final_fact_check
from modules.hyde_rag import contextual_retrieval  # Ensure we're importing contextual retrieval
from modules.corrective_rag import corrective_rag

def display_rag_guide():
    """Display an in-depth guide to RAG methods and their use in the pipeline."""
    st.markdown("## RAG Methods Explained")
    st.markdown("""
    **RAG (Retrieval-Augmented Generation)** is a powerful method for answering complex questions by retrieving relevant documents and generating responses. This app uses multiple RAG approaches, each carefully selected to enhance specific stages of the answer generation pipeline. Below is an overview of each step and the methods used:

    ### 1. Data Crawling and Ingestion
    - **Module**: `data_crawling.py` and `git_data_crawling.py`
    - **Purpose**: This stage gathers documents from either a local directory or a GitHub repository. We support various file types (.py, .md, .csv, .ipynb, etc.) to capture a wide array of content. The documents are then processed and loaded into a format that’s ready for retrieval.
    - **Why**: Comprehensive document crawling ensures a robust information base, allowing us to answer diverse questions based on specific data within your repository.

    ### 2. Creating a Vector Store
    - **Module**: `vector_store.py`
    - **Purpose**: After gathering documents, they are embedded into a vector space using embeddings from Ollama’s `llama3.2` model. These embeddings are stored in a vector database (Chroma) for fast retrieval based on semantic similarity.
    - **Why**: Embedding documents in a vector space makes it easier to identify the most relevant documents for a given question, enabling faster and more accurate retrieval.

    ### 3. Contextual Retrieval
    - **Module**: `contextual_retrieval.py`
    - **Purpose**: Here, we enrich the content of each document by generating additional context, which provides a more nuanced basis for retrieval. Contextual Retrieval retrieves documents relevant to the question while enhancing them with extra contextual information to improve the accuracy of the generated answer.
    - **Why**: Enriching each document with context allows the model to better understand and extract specific details relevant to the query. This approach improves retrieval precision, especially for complex queries.

    ### 4. Corrective RAG (CRAG)
    - **Module**: `corrective_rag.py`
    - **Purpose**: This stage uses the retrieved documents to make specific recommendations or corrections based on their content. Corrective RAG reviews the initial answer for accuracy and coherence, then refines it by validating details against the retrieved documents.
    - **Why**: By iteratively refining the initial response, CRAG ensures that the answer aligns well with the available data, creating a more accurate and trustworthy output.

    ### 5. Self-RAG
    - **Module**: `self_rag.py`
    - **Purpose**: Self-RAG applies reflection on the initial response, critiquing and refining the answer. If the answer is found to need improvements, Self-RAG modifies the response accordingly, repeating this process for up to two reflections.
    - **Why**: Self-refinement makes the response more robust and precise. By allowing the model to evaluate and adjust its output, Self-RAG helps in creating answers that are both accurate and concise.

    ### 6. Web-Based Retrieval (Tavily Search)
    - **Module**: `web_search.py`
    - **Purpose**: When additional context is required, Tavily Search retrieves relevant information from the web. This step is integrated to provide external context that might complement the repository data, especially if the query requires a broader view.
    - **Why**: Incorporating web-based retrieval ensures that the app can supplement internal data with up-to-date information from the web, enhancing response quality for more general or complex questions.

    ### 7. Decision Mechanism
    - **Module**: `decision_mechanism.py`
    - **Purpose**: In this stage, confidence scores for each generated answer are evaluated, and the most reliable answer is selected. If the confidence scores are similar, the system combines elements from both answers for a balanced response.
    - **Why**: A final decision mechanism selects the most appropriate response, ensuring the chosen answer is both relevant and trustworthy.

    Each of these methods contributes uniquely to building answers with increased accuracy and adaptability, making this pipeline well-suited for navigating complex datasets and generating informed answers.
    """)


def run_rag_pipeline(data_source, repo_path=None, repo_url=None, question="What are the best practices for organizing a code repository?", file_types=None, debug=False):
    st.write("### Starting RAG pipeline...")
    st.write(f"Data Source: {data_source}")
    st.write(f"Question: {question}")
    st.write(f"File Types: {file_types}")

    progress_bar = st.progress(0)

    # Step 1: Load documents based on the selected data source
    st.write("#### Step 1: Loading Documents...")
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
    
    st.write(f"Loaded {len(documents)} documents.")
    progress_bar.progress(0.2)

    # Step 2: Create a vector store and a retriever
    st.write("#### Step 2: Creating Vector Store and Retriever...")
    vectorstore = create_vectorstore(documents, debug=debug)
    retriever = vectorstore.as_retriever()

    st.write("Vector store created successfully.")
    progress_bar.progress(0.4)

    # Step 3: Retrieve relevant documents using contextual retrieval
    st.write("#### Step 3: Retrieving Relevant Documents (Contextual Retrieval)...")
    retrieved_docs = contextual_retrieval(question, retriever, debug)
    st.write(f"Retrieved {len(retrieved_docs)} relevant documents.")
    progress_bar.progress(0.6)

    # Step 4: Generate recommendations using corrective RAG
    st.write("#### Step 4: Generating Recommendations (Corrective RAG)...")
    recommendations = corrective_rag(retrieved_docs, debug=debug)
    st.write(f"Generated {len(recommendations)} recommendations.")
    progress_bar.progress(0.8)

    # Step 5: Perform a final fact-check on the recommendations
    st.write("#### Step 5: Performing Final Fact-Check...")
    initial_answer = " ".join([rec.page_content for rec in recommendations])
    corrected_answer = final_fact_check(question, initial_answer, retriever, debug=debug)
    st.write("Fact-check completed.")
    progress_bar.progress(0.9)

    # Step 6: Decide and return the best answer
    st.write("#### Step 6: Finalizing the Best Answer...")
    final_answer = decide_and_answer(question, retriever, debug=debug)
    st.write("Pipeline completed.")
    progress_bar.progress(1.0)

    return final_answer

def main():
    st.title("GitHub and Local Repository RAG Explorer")
    
    # Option to display the RAG methods guide
    if st.checkbox("Show RAG Methods Guide"):
        display_rag_guide()

    data_source = st.radio("Select Data Source:", ["Local", "Git"])
    question = st.text_input("Enter your question:", "What are the best practices for organizing a code repository?")
    debug = st.checkbox("Enable Debug Mode", value=False)

    # File type filter selection
    available_file_types = [".py", ".md", ".csv", ".ipynb", ".html", ".json", ".yaml", ".r", ".cpp", ".java", ".scala", ".sql"]
    file_types = st.multiselect("Select file types to include:", available_file_types, default=available_file_types)

    if data_source == "Local":
        repo_path = st.text_input("Enter Local Directory Path:")
        repo_url = None
    elif data_source == "Git":
        repo_path = None
        repo_url = st.text_input("Enter GitHub Repository URL:")

    if st.button("Run RAG Pipeline"):
        try:
            final_answer = run_rag_pipeline(data_source, repo_path=repo_path, repo_url=repo_url, question=question, file_types=file_types, debug=debug)
            st.write("### Final Answer:")
            st.write(final_answer)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

