# Sports News RAG Bot

This repository provides an advanced Retrieval-Augmented Generation (RAG) bot for sports news. It combines various RAG methods with contextual and corrective refinements, enabling users to receive accurate, real-time information on sports events. The bot is implemented in a Dockerized environment to ensure consistency and easy setup across systems.

## Demo


https://github.com/user-attachments/assets/e13404a5-0b72-4125-bb2d-02695706afc0


## Table of Contents
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Features](#features)
- [Technical Overview](#technical-overview)

---

## Getting Started

1. **Clone the Repository**:
    Clone this repository to your local environment:
    ```bash
    git clone https://github.com/ghadfield32/custom_ollama_docker
    
    ```

2. **Navigate to the Repository Root**:
    ```bash
    cd custom_ollama_docker
    ```

3. **Build the Docker Environment**:
    Use Docker to set up a consistent environment with all necessary dependencies. Run the following command:
    ```bash
    docker-compose build --no-cache
    docker-compose up -d
    ```



4. **Open in Development Container**:
    After building, open the project in a dev container to start working with the complete environment.
    ``` vscode keyboard shortcut
    Ctrl+P > Rebuild and Reopen in Container (devcontainer command)
    ```
    
---

## Running the Application

Once inside the development container, follow these steps:

1. **Start the Streamlit Application**:
    To launch the app, use the following command:
    ```bash
    streamlit run src/sports_news_rag/app.py
    ```

2. **Access the Application**:
    The app should open automatically in your default browser. If not, access it through the link displayed in the terminal (usually `http://localhost:8501`).

---

## Features

The Sports News RAG Bot provides an extensive feature set aimed at delivering accurate and up-to-date sports news. Below is a summary of each major feature.

### 1. **Question-Answering Interface**
   - The app’s main feature is its interactive question-answering interface, which allows users to ask sports-related questions. The bot then uses various RAG techniques to retrieve, refine, and verify the answer.
   - The interface allows users to customize options such as enabling debugging and specifying external URLs for additional fact-checking.

### 2. **Pre-Ingested Data Loading**
   - Users can load pre-ingested data for popular sports sites like NBA, ESPN, and NFL directly through the app's sidebar.
   - This option provides a faster retrieval experience and ensures the assistant has access to detailed, reliable sports data from these sites.

### 3. **Custom Data Crawling and Ingestion**
   - Users can specify custom sports-related URLs for crawling and ingestion.
   - The app uses its data crawling pipeline to ingest content from these custom sites, making the assistant adaptable to new information sources.

### 4. **Dynamic Vector Store Creation**
   - After crawling and ingestion, users can create a vector store with the ingested documents. This step enables efficient document retrieval based on vector embeddings, significantly speeding up the response time.

### 5. **Real-Time Tavily Web Search Integration**
   - Tavily Search provides a dynamic web search to supplement pre-ingested and custom data. It enables real-time access to the latest sports updates when needed, ensuring responses are comprehensive and timely.

### 6. **Multiple RAG Techniques**:
   - The bot employs various RAG strategies to maximize accuracy, including:
       - **Simple RAG**: Standard retrieval and answer generation for reliable responses.
       - **Branched RAG**: Iterative retrieval steps for high-quality answers.
       - **Contextual Retrieval**: Context-enriched documents for improved relevance.
       - **Corrective RAG (CRAG)**: Ensures accuracy by refining the generated answer.
       - **Self-RAG**: Adds an additional layer of answer refinement through self-reflection.
       - **Agentic RAG**: Manages complex queries by executing multiple steps to assemble an answer.

### 7. **Final Fact-Check with Combined Sources**
   - As a final step, the app performs a comprehensive fact-check of the generated answer using both pre-ingested data and the Tavily search context.
   - This feature ensures high reliability and accuracy, making it suitable for real-time information needs.

### 8. **Debugging Mode**
   - When enabled, this mode displays internal processing details, such as document retrieval, RAG confidence scores, and intermediate results from various RAG steps.
   - Debugging mode is useful for development, troubleshooting, and gaining insights into how the bot generates answers.

---

## Technical Overview

The app leverages a variety of modules and RAG techniques to maximize the accuracy and relevance of responses. Below is a quick overview of the main modules:

- **Data Crawling Module** (`data_crawling.py`): Crawls websites and preprocesses documents for ingestion, chunking, and quality checks.
- **Vector Store Module** (`vector_store.py`): Creates a vector store for efficient document retrieval using embeddings.
- **Contextual Retrieval Module** (`contextual_retrieval.py`): Adds contextual nodes to documents for better-aligned retrieval with nuanced queries.
- **HyDE RAG Module** (`hyde_rag.py`): Replaces hypothetical document generation with enhanced contextual retrieval.
- **Corrective RAG Module** (`corrective_rag.py`): Iteratively refines responses to ensure they’re factually supported by retrieved documents.
- **Self-RAG Module** (`self_rag.py`): Self-reflects on generated answers to improve clarity and accuracy.
- **Web Search Module** (`web_search.py`): Leverages Tavily to search for additional context when pre-ingested data is insufficient.
- **Decision Mechanism Module** (`decision_mechanism.py`): Manages response generation and selects the best answer based on confidence scores.
- **Fact Checker Module** (`fact_checker.py`): Combines all contexts to perform a final fact-check of the answer, enhancing reliability.

---

## Support

For issues or feature requests, please use the repository's Issues section.

Happy querying with the Sports News RAG Bot!
