# LLM and RAG Streamlit App Repository

This repository provides several advanced Streamlit applications that leverage Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) techniques, each tailored to unique tasks such as database optimization and real-time sports news retrieval. The setup is Dockerized for consistent cross-platform deployment, including GPU support.

## Contents

1. [Setup Steps](#setup-steps)
2. [App Overview and Launch Commands](#app-overview-and-launch-commands)
3. [Video Walkthroughs](#video-walkthroughs)

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
   - Alternatively, choose any model compatible with your specific task, such as `text2cypher`.

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

Here’s an overview of each app, its purpose, features, and how to launch it.

---

#### Database Optimizer App

- **Purpose**: This app visualizes and analyzes database schemas, helping detect redundancies and suggesting optimizations. It uses NetworkX for graph-based schema analysis combined with LLM-powered insights.
- **Launch Command**:
  ```bash
  streamlit run src/database_optimizer_networkx_rag_llama3/streamlit_app.py
  ```
- **Features**:
  - Schema visualization with nodes representing tables/columns and edges showing relationships.
  - LLM analysis to identify duplicate tables, foreign key relationships, and optimization opportunities.

---

#### Sports News Agentic Websearch Enabled Contextual Retrieval RAG Bot

- **Purpose**: This bot delivers real-time sports news using advanced RAG techniques, including contextual retrieval and agentic web search with Tavily integration.
- **Launch Command**:
  ```bash
  streamlit run src/sports_news_rag/app.py
  ```
- **Features**:
  - Real-time sports updates powered by Tavily web search and pre-ingested sports news.
  - Multi-layered RAG strategies like Contextual Retrieval, Self-RAG, and Corrective RAG for accurate responses.

---

#### NBA Neo4j Data Ingestion/Analysis App

- **Purpose**: This app ingests and analyzes NBA player data, contracts, and team strategies in a Neo4j database, enabling trade analysis and player/team statistics exploration with Cypher queries.
- **Launch Command**:
  ```bash
  streamlit run src/neo4j_model/streamlit_app.py
  ```
- **Features**:
  - Neo4j data ingestion, creating a structured database of players, teams, and contracts.
  - Natural language-based Cypher queries via GraphQA, enabling accessible data querying and insights on trade value, player performance, and team strategies.

---

#### Git or Local Tree RAG Demo

- **Purpose**: This demo showcases a Retrieval-Augmented Generation (RAG) setup that reads and analyzes local file structures or Git repositories, recommending improvements based on code structure and metadata.
- **Launch Command**:
  ```bash
  streamlit run src/git_repo_model/app.py
  ```
- **Features**:
  - Ingests documents from a specified local directory or GitHub repo.
  - Multi-stage RAG pipeline for contextual code analysis, with Corrective and Self-RAG stages to ensure reliable recommendations.

---

#### PDF Load into Graph RAG Demo

- **Purpose**: Demonstrates RAG using PDF documents, processing files into graph nodes and applying context-based retrieval for document exploration.
- **Launch Command**:
  ```bash
  streamlit run src/pdf_to_graph_rag/app.py
  ```
- **Features**:
  - Transforms PDF contents into graph structures, enabling semantic search and document relationship analysis.
  - Contextual and Corrective RAG strategies for refined information retrieval across document nodes.

---

### 3. Video Walkthroughs

For a step-by-step visual guide, refer to these walkthroughs:

- **[PDF Load into Graph Rag Demo](custom_ollama_docker/videos/pdf_networkx_rag_llama3.2.mp4)**
- **[Database Optimizer Graph Rag Demo](custom_ollama_docker/videos/database_optimizer_networkx_graph_llama3.mp4)**
- **[Sports News Agentic Websearch Enabled Contextual Retrieval RAG Demo](custom_ollama_docker/videos/Advanced_Sports_News_Websearch_RAG_Bot.mp4)**
- **[NBA Neo4j Data Ingestion/Analysis Cypher Finetuned Llama3 Model Demo](custom_ollama_docker/videos/Neo4j_llama3cypher_example.mp4)**
- **[Git or Local Tree Rag Demo](custom_ollama_docker/videos/git_or_local_repository_local_rag_llama3_2.mp4)**

---



# GPU enabled Ollama-Neo4j GPU enabled Docker Image Template 
https://github.com/ghadfield32/ollama-neo4j-docker

## Basic Structure for Docker Environment
project_root/
│
├── .devcontainer/
│   ├── Dockerfile
│   ├── devcontainer.json
│   ├── devcontainer.env
│   ├── environment.yml
│   ├── requirements.txt
│   ├── .dockerignore
│   ├── install_dependencies.sh
│   ├── install_quarto.sh
│   └── install_requirements.sh
├── scripts/
│   └── start_services.sh

│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   └── ...
│
├── src/
│   └── features
│   └── models
│   └── visualization
│
├── app/
│   └── ...
│
├── tests/
│   └── test1.py
│
├── README.md
├── .gitattributes
├── .gitignore
├── .env
│
└── docker-compose.yml

