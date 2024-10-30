
# LLM Example Repository - Docker Environment and Retrieval-Augmented Generation (RAG) Apps

This repository showcases advanced examples using large language models (LLMs) and Retrieval-Augmented Generation (RAG) methods with a focus on efficient document retrieval, contextual enhancement, and automated knowledge improvement. The following README will guide you through setting up the Docker environment, configuring the necessary CUDA environment, running the app using Streamlit, and understanding the unique components of each app.

## Demo


https://github.com/user-attachments/assets/e6160f7a-9a5e-4748-99d4-5414599835a9



## Contents

1. [Environment Setup](#environment-setup)
2. [Running the Streamlit App](#running-the-streamlit-app)
3. [App Breakdown by Use Case](#app-breakdown-by-use-case)
4. [Video Walkthroughs](#video-walkthroughs)

---

### 1. Environment Setup

This repository includes a Docker environment for seamless deployment across systems. Follow these steps to set up the environment:

#### Prerequisites

- **CUDA**: Ensure CUDA is installed and compatible with the Docker setup for accelerated performance.
- **Docker**: Docker version 20.x or newer is recommended.
- **NVIDIA Docker**: To use GPU acceleration, install NVIDIA Docker and configure it according to your system’s requirements.

#### Docker Environment Configuration

To build the Docker environment, follow these commands:

```bash
# Clone the repository
git clone https://github.com/your-repo-name/llm-example-repo.git
cd llm-example-repo

# Build the Docker image
docker build -t llm-docker-env .

# Run the Docker container with GPU support
docker run --gpus all -p 8501:8501 -v $(pwd):/app llm-docker-env
```

The `Dockerfile` in this repository installs all necessary dependencies, including CUDA support for GPU acceleration, making it easy to deploy LLM-based apps within the Dockerized environment.

### 2. Running the Streamlit App

Once the Docker container is up, start the Streamlit app by running:

```bash
# In the Docker container, run Streamlit
streamlit run src/git_repo_model/app.py
```

Navigate to `http://localhost:8501` in your browser to access the application.

### 3. App Breakdown by Use Case

Each app in this repository demonstrates a specific use case for LLMs with RAG, and they use different models, vector stores, and retrieval strategies. Below is a breakdown of each app:

---

#### App 1: Local Optimizer RAG

- **Code Link**: [`notebooks/contextual_retreivel_rag/local_optimizer_rag/langchain_quickstart_ollama_llama_hyde_corrective.ipynb`](notebooks/contextual_retreivel_rag/local_optimizer_rag/langchain_quickstart_ollama_llama_hyde_corrective.ipynb)
- **App Link**: [`src/git_repo_model/app.py`](src/git_repo_model/app.py)
- **Model Used**: `llama3.2`
- **Storage**: Vector storage (Chroma)
- **RAG Techniques**: Contextual Retrieval, Corrective RAG, Self-RAG, and Web-Based Retrieval

##### Description of Retrieval Pipeline

This app utilizes a multi-stage RAG pipeline, which enhances response quality by focusing on each stage’s unique purpose. Here’s a step-by-step guide to the retrieval process:

1. **Data Crawling and Ingestion**:
   - **Modules**: `data_crawling.py` and `git_data_crawling.py`
   - **Purpose**: Gathers documents from a specified local directory or GitHub repository, processing files such as `.py`, `.md`, `.csv`, and `.ipynb`.
   - **Benefits**: A broad document base enables accurate and contextually rich responses for various queries.

2. **Creating a Vector Store**:
   - **Module**: `vector_store.py`
   - **Purpose**: Embeds documents using `llama3.2` model embeddings and stores them in a Chroma vector database.
   - **Benefits**: Embedding in a vector space allows for fast and accurate retrieval based on semantic similarity, critical for relevant answer generation.

3. **Contextual Retrieval**:
   - **Module**: `contextual_retrieval.py`
   - **Purpose**: Enhances the content of retrieved documents by generating additional context, allowing for improved retrieval precision.
   - **Benefits**: By creating a more nuanced retrieval basis, the app handles complex queries effectively.

4. **Corrective RAG (CRAG)**:
   - **Module**: `corrective_rag.py`
   - **Purpose**: Provides corrective adjustments to the initial answer, ensuring the response is accurate and consistent with retrieved documents.
   - **Benefits**: Iterative refinement leads to a more reliable output aligned with the document data.

5. **Self-RAG**:
   - **Module**: `self_rag.py`
   - **Purpose**: Self-assesses the initial answer, making modifications if needed to improve quality and accuracy.
   - **Benefits**: Self-refinement steps lead to more polished and coherent responses, especially useful for complex answers.

6. **Web-Based Retrieval (Tavily Search)**:
   - **Module**: `web_search.py`
   - **Purpose**: Integrates web search for supplementary data, particularly useful when queries require more context.
   - **Benefits**: Ensures that responses are enriched with current and broader knowledge, improving accuracy for general queries.

7. **Decision Mechanism**:
   - **Module**: `decision_mechanism.py`
   - **Purpose**: Evaluates answer confidence and selects the most reliable response, blending answers if necessary.
   - **Benefits**: Final confidence scoring ensures that answers are both trustworthy and contextually relevant.

Each of these stages plays a role in the app's performance, making it a powerful tool for handling various question types and generating high-quality answers.

---

### 4. Video Walkthroughs

For a guided visual walkthrough of each app, refer to the following video links:

- **App 1 - Local Optimizer RAG with LLaMA 3.2**  
  [Watch Video](custom_ollama_docker/videos/git_or_local_repository_local_rag_llama3_2.mp4)

This video will walk you through setting up and using the local optimizer RAG, including detailed demonstrations of vector storage, contextual retrieval, and corrective RAG techniques using the `llama3.2` model. It also covers specific configurations and shows the app in action, providing insights into each retrieval stage.

