# LLM and RAG Streamlit App Repository

This repository provides several advanced Streamlit applications that leverage Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) techniques, each tailored to unique tasks, such as database optimization and real-time sports news retrieval. The setup is Dockerized for consistent cross-platform deployment, including GPU support.

## Contents

1. [Setup Steps](#setup-steps)
2. [App Overview and Launch Commands](#app-overview-and-launch-commands)
3. [Ollama and LangChain Integration](#ollama-and-langchain-integration)
4. [Video Walkthroughs](#video-walkthroughs)

---

### 1. Setup Steps

Follow these steps to set up the Docker environment, models, and necessary configurations.

#### Step-by-Step Instructions

1. **Clone the Repository and Install Dependencies**:
   ```bash
   git clone https://github.com/ghadfield32/custom_ollama_docker
   cd custom_ollama_docker
   ```

2. **Docker Build and Open in Dev Container**:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

   In Visual Studio Code (VSCode):
   - Press `Ctrl+P`, type `Rebuild and Reopen in Container`, and select the command to enter the development environment.

3. **Ollama Model Pull**:
   - Pull the required model in the terminal:
     ```bash
     ollama pull tomasonjo/llama3-text2cypher-demo
     ```
     or 
     ```bash
     ollama pull llama3.2
     ```
   - I chose llama3-text2cypher-demo because it was finetuned in `text2cypher` for neo4j tasks
   - I chose llama3.2 for everything else because it was the latest and greatest lately

4. **Start Neo4j**:
   - Ensure Neo4j is accessible with the following `.env` configuration at the repository root:

     ```plaintext
     # .env
     TAVILY_API_KEY=
     LANGSMITH_API_KEY=
     SQLITE_DB_PATH_1=../data/databases/db1.sqlite
     SQLITE_DB_PATH_2=../data/databases/db2.sqlite
     NEO4J_URI=neo4j://localhost:7687
     NEO4J_USERNAME=neo4j
     NEO4J_PASSWORD=your_password
     ```

   - For cloud-based Neo4j, sign up at [neo4j.com](https://neo4j.com) and update the credentials in the `.env` file.

5. **Run Streamlit Apps**:
   - Use the specific Streamlit commands listed below to explore the features of each application.

---

### 2. App Overview and Launch Commands

Each application has a unique purpose. Here’s an overview of each, along with the command to launch it.

- **Database Optimizer App**: Analyzes and visualizes database schemas, using NetworkX and LLMs to identify redundancies and optimize schema design.
  ```bash
  streamlit run src/database_optimizer_networkx_rag_llama3/streamlit_app.py
  ```
  

https://github.com/user-attachments/assets/dfe07211-3b29-4c64-8ec9-20d0f772d717


- **Sports News Agentic Websearch Enabled Contextual Retrieval RAG Bot**: Provides real-time sports news using advanced RAG techniques, including web search with Tavily.
  ```bash
  streamlit run src/sports_news_rag/app.py
  ```


https://github.com/user-attachments/assets/f1c2414b-3c01-4bd9-92c3-7dca01d9b1bc



- **NBA Neo4j Data Ingestion/Analysis App**: Ingests and analyzes NBA player data, contracts, and strategies in a Neo4j database, with GraphQA-based querying.
  ```bash
  streamlit run src/neo4j_model/streamlit_app.py
  ```
![database_schema](https://github.com/user-attachments/assets/0b04a827-72e4-4732-be65-0bd8548969f3)


https://github.com/user-attachments/assets/4e56b6f7-8ae7-4cbd-9f96-b5e3cd1614ad


- **Git or Local Tree RAG Demo**: Ingests local directories or GitHub repositories for RAG-based code structure analysis.
  ```bash
  streamlit run src/git_repo_model/app.py
  ```


https://github.com/user-attachments/assets/e20e2d6d-46a2-4a19-b976-aaa42ed5a52c


- **PDF Load into Graph RAG Demo**: Uses graph nodes for PDF document content, enabling semantic search and document exploration.
  ```bash
  streamlit run src/graphrag/networkx/examples/app.py
  ```


https://github.com/user-attachments/assets/5884a2d7-aac3-4b51-9640-2d9ccc729769


---

### 3. Ollama and LangChain Integration

This repository leverages **Ollama** and **LangChain** for handling large language model (LLM) workflows with advanced Retrieval-Augmented Generation (RAG). Below are options for maintaining and serving these models locally, through Docker, or via cloud deployments.

#### Local Maintenance and Serving with Docker

This Docker setup offers a convenient way to maintain Ollama models (like `Llama 3.2`) locally while making them accessible globally if hosted on a server. By leveraging the Docker image’s built-in configurations, Ollama and LangChain can handle complex retrieval pipelines efficiently within a controlled environment. Docker's built-in GPU compatibility (with CUDA/NVIDIA Docker) ensures that you can serve models with enhanced performance for heavy computational tasks.

1. **Serve the Model Locally**:
   - With the Docker container running, models can be accessed and tested locally through Streamlit apps or scripts within the dev environment.
2. **Serve on a Server (Global Access)**:
   - By deploying the Docker container on a cloud or local server, you can make the model accessible globally. Configuring your Docker network settings or utilizing a cloud provider’s network options (e.g., AWS or GCP load balancers) allows secure remote access to model inference.

#### Cloud-Based Options: Hugging Face Spaces

For a cloud-deployed model accessible from anywhere without server maintenance, you may consider **Hugging Face Spaces**. Hugging Face offers Spaces for hosting models and applications, making it a user-friendly option for deploying LLMs, albeit at a cost for higher usage and storage. This deployment model suits applications where maintenance-free, scalable hosting is essential.

1. **Upload and Deploy**:
   - Prepare the Streamlit app and model artifacts, then upload them to a Hugging Face Space for deployment.
2. **Advantages and Considerations**:
   - Pros: Minimal setup, global accessibility, and easy scaling.
   - Cons: Usage fees and limited control over back-end infrastructure.

#### Example Serving Option: Litserve in Notebooks

Within `notebooks/litserve`, a **Litserve** example is set up for deploying models like `Llama 3.2`. This option provides a direct, simple way to serve the model with a lightweight API. Litserve runs on CPU, enabling you to offer model inferences with minimal configuration and on-demand scalability.

1. **Litserve Setup**:
   - Run the Litserve script from `notebooks/litserve`, which serves the model and makes it accessible as an API endpoint for querying and retrieval.
2. **Usage Scenario**:
   - Litserve is ideal for smaller projects requiring on-demand LLM inference without the complexity of a full Docker or cloud setup. This option can also be useful for local testing or serving specific LLMs without additional infrastructure.

**Note**: Each serving method is designed to provide flexibility based on your requirements for accessibility, scalability, and maintenance. This repository’s Docker setup enables seamless local and global deployments, while Hugging Face and Litserve provide alternative methods with varying degrees of complexity and control.

---

### 4. Mp4 Demos of Apps

For a step-by-step visual guide, refer to these walkthroughs:

- **[PDF Load into Graph Rag Demo](custom_ollama_docker/videos/pdf_networkx_rag_llama3.2.mp4)**
- **[Database Optimizer Graph Rag Demo](custom_ollama_docker/videos/database_optimizer_networkx_graph_llama3.mp4)**
- **[Sports News Agentic Websearch Enabled Contextual Retrieval RAG Demo](custom_ollama_docker/videos/Advanced_Sports_News_Websearch_RAG_Bot.mp4)**
- **[NBA Neo4j Data Ingestion/Analysis Cypher Finetuned Llama3 Model Demo](custom_ollama_docker/videos/Neo4j_llama3cypher_example.mp4)**
- **[Git or Local Tree Rag Demo](custom_ollama_docker/videos/git_or_local_repository_local_rag_llama3_2.mp4)**

---
