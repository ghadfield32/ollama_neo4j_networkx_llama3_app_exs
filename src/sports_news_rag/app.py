import streamlit as st
from modules.decision_mechanism import decide_and_answer, evaluate_confidence  # Import evaluate_confidence
from modules.vector_store import create_vectorstore
from modules.data_crawling import crawl_and_ingest
from modules.fact_checker import final_fact_check
from modules.hyde_rag import contextual_retrieval
from modules.corrective_rag import corrective_rag
from modules.self_rag import self_rag
from modules.web_search import tavily_search  # Import tavily_search
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama

# Set up the Streamlit app title and description (MUST be the first Streamlit command)
st.set_page_config(page_title="Advanced Sports News RAG Bot", layout="wide")

# Debug: Confirm the current working directory
current_working_dir = os.getcwd()
st.sidebar.write(f"Current Working Directory: {current_working_dir}")

# Load environment variables
dotenv_path = os.path.join(current_working_dir, '.env')
load_dotenv(dotenv_path)

# Define the missing function to generate an answer from context
def generate_answer_from_context(context, question, debug=False):
    """
    Generate an answer based on the provided context and user question.
    
    Parameters:
    - context (str): The text context retrieved from Tavily search.
    - question (str): The user's question to answer.
    - debug (bool): If True, enables debug output.
    
    Returns:
    - str: The generated answer based on the context.
    """
    llm = ChatOllama(model="llama3.2", temperature=0)  # Ensure the same LLM model is used
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    response = llm.invoke([{"role": "user", "content": prompt}]).content

    if debug:
        print(f"Generated answer from context: {response}")

    return response


# Confirm environment path and any loaded variables
if os.path.exists(dotenv_path):
    st.sidebar.write(f".env file found at: {dotenv_path}")
else:
    st.sidebar.write(f".env file not found at: {dotenv_path}")

st.title("Advanced Sports News RAG Bot")
st.write("Get the most up-to-date sports news using advanced RAG techniques. This bot combines information from various sources and fact-checks responses for reliability.")

# Adding the introduction tab
tabs = st.tabs(["Introduction", "Ask a Question"])

# Introduction tab content
with tabs[0]:
    st.header("Approaches Used in Advanced Versatile RAG Bot")
    st.write("""
    This project leverages a variety of Retrieval-Augmented Generation (RAG) strategies to create an interactive assistant capable of providing reliable, up-to-date information for any type of website, though it has been initially applied to sports news. Below, we detail the approaches utilized, how they contribute to the quality of answers, and the innovative combination of different RAG methodologies.
    """)

    st.subheader("Simple RAG")
    st.write("""
    Simple RAG forms the foundation of our bot by retrieving documents based on a user query and generating grounded answers with a large language model (LLM). It minimizes hallucination issues by anchoring the generated responses to relevant sources.
    """)

    st.subheader("Branched RAG")
    st.write("""
    Our Branched RAG approach performs multiple retrieval layers, refining searches based on intermediate results. This iterative process enhances answer specificity and is especially valuable for complex or multi-layered queries.
    """)

    st.subheader("Contextual Retrieval")
    st.write("""
    Contextual Retrieval replaces hypothetical document generation (HyDE) by enriching each document with additional context, making retrieval results more aligned with nuanced queries. By adding contextual nodes to documents, the bot achieves higher precision and recall in retrieving relevant data.
    """)

    st.subheader("Corrective RAG (CRAG)")
    st.write("""
    Corrective RAG (CRAG) iteratively checks and refines responses by comparing them to the context from retrieved documents. This ensures answers are accurate and well-supported, enhancing reliability and factual correctness.
    """)

    st.subheader("Self-RAG")
    st.write("""
    Self-RAG adds a layer of self-reflection where the model re-evaluates its initial answer to make improvements in clarity, conciseness, and accuracy. This self-assessment strengthens response quality by ensuring coherence and completeness.
    """)

    st.subheader("Agentic RAG")
    st.write("""
    Agentic RAG orchestrates multi-step queries, allowing the bot to act as an autonomous agent. By combining retrieval, verification, and synthesis processes, Agentic RAG enables intelligent navigation of information sources, crafting answers that involve interconnected insights.
    """)

    st.subheader("Tavily Web Search")
    st.write("""
    Tavily Web Search complements RAG by dynamically searching the web for up-to-date information, especially when pre-ingested documents do not fully address a query. This integration ensures the bot’s responses reflect the latest information available.
    """)

    st.subheader("Final Fact-Check")
    st.write("""
    As a final step, the bot performs a comprehensive fact-check using combined contexts from both pre-ingested documents and Tavily search results. This step verifies that the answer provided aligns with reliable, current information, enhancing trustworthiness.
    """)

    st.header("How These Approaches Work Together")
    st.write("""
    By integrating these RAG methods, our bot achieves high accuracy, adaptability, and domain versatility. Here’s how they work in tandem:

    - **Initial Retrieval**: Simple RAG retrieves documents relevant to the query.
    - **Refinement**: Branched RAG and Contextual Retrieval enhance document selection, providing more precise data.
    - **Verification**: Corrective RAG verifies factual accuracy, and Self-RAG refines answer quality.
    - **Dynamic Updates**: Tavily Search supplements with current web-based information when needed.
    - **Multi-step Processing**: Agentic RAG manages complex queries requiring multiple information sources.
    - **Final Fact-Check**: Ensures responses are reliable and up-to-date, combining all contexts effectively.

    These methods together create a robust, adaptive assistant capable of providing clear, reliable answers to dynamic questions.
    """)

    st.header("The Value of Combined RAG Approaches")
    st.write("""
    By integrating these techniques, our system is capable of:

    - **High accuracy**: Corrective checks ensure factual answers.
    - **Adaptability**: Contextual enhancement bridges knowledge gaps.
    - **Depth in retrieval**: Branched and Agentic RAGs enable nuanced understanding.
    - **Domain versatility**: Capable of handling various domains beyond sports.
    - **Real-time information**: Tavily Search provides the latest web updates.
    - **Context retention**: Maintains relevant context across user interactions for a more interactive experience.

    These combined approaches make the Versatile RAG Bot capable of not only providing reliable answers but also refining and adapting outputs intelligently across a range of queries.
    """)



# Ask a Question tab content
with tabs[1]:
    # Sidebar configuration options
    st.sidebar.title("Configuration")
    enable_debug = st.sidebar.checkbox("Enable Debugging", value=False)
    include_fact_check = st.sidebar.checkbox("Include Final Fact-Check", value=True)
    use_pre_ingested_data = st.sidebar.checkbox("Use Pre-Ingested Data", value=True)

    # Dynamic Source Selection for Fact-Checking
    fact_check_sources = st.sidebar.text_input(
        "Enter Custom URLs for Fact-Checking (comma-separated)", 
        "https://www.nba.com, https://www.espn.com"
    )

    # Ensure the session state attributes are initialized
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "all_documents" not in st.session_state:
        st.session_state.all_documents = []

    # Load or ingest data
    if use_pre_ingested_data:
        st.sidebar.subheader("Pre-Ingested Data Loading")
        known_sites = ["NBA", "ESPN", "NFL"]
        selected_site = st.sidebar.selectbox("Select Pre-Ingested Site:", known_sites)
        
        if st.sidebar.button("Load Pre-Ingested Data"):
            with st.spinner(f"Loading pre-ingested data for {selected_site}..."):
                pre_ingested_vectorstore_path = os.path.join(current_working_dir, f"data/vectorstores/{selected_site.lower()}")

                # Ensure the embedding function is specified
                embeddings = OllamaEmbeddings(model="llama3.2")

                if os.path.exists(pre_ingested_vectorstore_path):
                    try:
                        # Include embedding function in Chroma initialization
                        st.session_state.vectorstore = Chroma(
                            persist_directory=pre_ingested_vectorstore_path,
                            embedding_function=embeddings
                        )
                        st.session_state.retriever = st.session_state.vectorstore.as_retriever()
                        st.sidebar.success(f"Loaded pre-ingested data for {selected_site}.")
                    except Exception as e:
                        st.sidebar.error(f"Error loading pre-ingested data for {selected_site}: {str(e)}")
                else:
                    st.sidebar.error(f"Pre-ingested data for {selected_site} not found at path: {pre_ingested_vectorstore_path}")
                    
    else:
        # Allow the user to input custom URLs
        custom_sports_sites = st.sidebar.text_input(
            "Enter custom URLs for crawling data (comma-separated)",
            "https://www.nba.com, https://www.espn.com"
        ).split(",")

        if st.sidebar.button("Ingest Data"):
            with st.spinner("Crawling and ingesting data..."):
                st.session_state.all_documents = []
                for site in custom_sports_sites:
                    site = site.strip()
                    if site:
                        documents = crawl_and_ingest(site, debug=enable_debug)
                        st.session_state.all_documents.extend(documents)
                st.sidebar.success(f"Data ingested from {len(custom_sports_sites)} sites.")

        if st.sidebar.button("Create Vector Store"):
            with st.spinner("Creating vector store from dynamically ingested data..."):
                if st.session_state.all_documents:
                    st.session_state.vectorstore = create_vectorstore(st.session_state.all_documents, debug=enable_debug)
                    st.session_state.retriever = st.session_state.vectorstore.as_retriever()
                    st.sidebar.success("Vector store created and retriever set up.")
                else:
                    st.sidebar.error("No documents available. Please ingest data first.")

    # User question input
    st.subheader("Ask a Sports-Related Question")
    user_question = st.text_input("Enter your question about sports news or events:", "What pick of the Draft was Bronny James Jr?")

    if st.button("Get Answer"):
        if not st.session_state.retriever:
            st.error("Please load or create the vector store first.")
        elif user_question:
            # Initialize progress bar
            progress_bar = st.progress(0)
            progress_status = st.empty()

            with st.spinner("Starting RAG process..."):
                # Step 1: Initial Retrieval and Hypothetical Document Generation
                progress_status.text("Step 1: Performing Initial Contextual Retrieval...")
                retrieved_docs = contextual_retrieval(user_question, st.session_state.retriever, debug=enable_debug)
                progress_bar.progress(0.25)
                
                if enable_debug:
                    st.write(f"Contextual Retrieval Output: {retrieved_docs[:2]}")  # Display first 2 for brevity

                # Step 2: Corrective RAG
                progress_status.text("Step 2: Generating Corrective RAG Answer...")
                rag_answer = corrective_rag(user_question, retrieved_docs, debug=enable_debug)
                progress_bar.progress(0.5)

                # Step 3: Self-Refinement on RAG Answer
                progress_status.text("Step 3: Refining RAG Answer with Self-RAG...")
                rag_refined_answer = self_rag(user_question, rag_answer, debug=enable_debug)
                rag_confidence = evaluate_confidence(rag_refined_answer, debug=enable_debug)
                progress_bar.progress(0.6)
                
                if enable_debug:
                    st.write(f"Refined RAG Answer: {rag_refined_answer}")
                    st.write(f"RAG Confidence Score: {rag_confidence}")

                # Step 4: External Tavily Search
                progress_status.text("Step 4: Performing Tavily Web Search...")
                tavily_context = tavily_search(user_question, debug=enable_debug)
                tavily_answer = generate_answer_from_context(tavily_context, user_question)
                progress_bar.progress(0.8)

                # Self-RAG on Tavily answer
                progress_status.text("Refining Tavily Answer with Self-RAG...")
                tavily_refined_answer = self_rag(user_question, tavily_answer, debug=enable_debug)
                tavily_confidence = evaluate_confidence(tavily_refined_answer, debug=enable_debug)
                progress_bar.progress(0.9)
                
                if enable_debug:
                    st.write(f"Tavily Answer: {tavily_refined_answer}")
                    st.write(f"Tavily Confidence Score: {tavily_confidence}")

                # Step 5: Decision Mechanism
                progress_status.text("Step 5: Making Final Decision...")
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
                        f"Based on these, provide the best possible answer to the question: {user_question}"
                    )
                    llm = ChatOllama(model="llama3.2", temperature=0)
                    final_answer = llm.invoke([{"role": "user", "content": combined_prompt}]).content
                    source = "Combined response"
                progress_bar.progress(1.0)
                
                if enable_debug:
                    st.write(f"Final Answer Selected from {source}: {final_answer}")

                # Optional fact-check with custom sources (sources parameter removed here)
                if include_fact_check:
                    progress_status.text("Performing final fact-check...")
                    final_answer = final_fact_check(user_question, final_answer, st.session_state.retriever, debug=enable_debug)
                    progress_bar.progress(1.0)

                # Display final answer
                st.subheader("Answer")
                st.write(final_answer)
        else:
            st.error("Please enter a question.")
