# Database Subject Matter Expert/Optimizer/Visualizer - Llama3.2 using Graph (Networkx) Storage

This repository provides a flexible framework to visualize database schemas, analyze structure, and identify redundancy or optimization opportunities using a Large Language Model (LLM)-based schema analysis tool. The application supports SQLAlchemy-compatible databases and metadata upload in JSON and CSV formats. Example databases load automatically, enabling rapid schema inspection, with support for loading external database metadata such as Oracle or Snowflake.

## Demo


https://github.com/user-attachments/assets/1237e57a-dff1-4db1-a353-b658712d0c34

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


## Models and Vector Stores

- **LLM Model**: This project uses the **LLaMA 3.2 model** accessed via the LangChain and Ollama integration.
- **Vector Store**: The schema uses NetworkX for graph-based analysis, storing database tables and columns as graph nodes.


## Running the Streamlit App

Run the Streamlit app from the root of the repository:
```bash
streamlit run src/database_optimizer_networkx_rag_llama3/streamlit_app.py
```

Once started, navigate to `http://localhost:8501` to view the app.

### Application Workflow

1. **Load Example Databases**: On startup, example databases are loaded by default, allowing immediate schema visualization and analysis. Tables include:
   - `employees`, `managers`, and `departments` in `example1.db`
   - `staff`, `supervisors`, and `office_locations` in `example2.db`
   
2. **Metadata Upload**: Upload database metadata in JSON or CSV format to override the example databases.
    - **JSON Format**: Should contain tables as keys and columns as values.
    - **CSV Format**: Requires columns for `table`, `column`, and `type`.

3. **Schema Graph Visualization**: The schema graph is visualized in the app, color-coded by database, allowing you to explore relationships between tables and columns.

4. **Schema Analysis with LLM**: Input custom prompts for the LLM to analyze schema structure and relationships. For example, enter prompts like:
   ```
   Identify any tables that appear to be duplicates or serve similar purposes.
   ```
   The LLM model then assesses the schema for redundancy, similar table purposes, or other relationships.

## Techniques and Modules

### 1. `database_setup.py`

Defines and sets up example databases in SQLite format with default tables and relationships. This module also ensures the existence of the path `/workspaces/custom_ollama_docker/data/graph_chroma_dbs/networkx` for storing these databases.

### 2. `graph_construction.py`

Builds a directed graph of the schema metadata using NetworkX. Each table and column is a graph node, and edges denote `contains` or `foreign_key` relationships. This structure enables easy traversal and analysis.

### 3. `llm_analyzer.py`

The `FlexibleDatabaseLLM` class uses **LangChain** with **LLaMA 3.2** (or specified LLM) to interpret schema structure. Users can define prompts to identify duplicates, foreign key relationships, or other optimizations. The model provides a summary based on graph-encoded metadata.

### 4. `visualization.py`

Visualizes the schema graph with **Matplotlib** and **NetworkX**, displaying nodes for tables and columns, with edges representing relationships. The visualization is displayed in Streamlit, providing an interactive way to view schema structures.

### 5. `main.py`

Serves as a backend orchestrator, managing setup, graph construction, visualization, and LLM analysis.

## Example Usage

Here’s an example command sequence to set up, visualize, and analyze the schema:

```python
# Start the Streamlit app
streamlit run src/database_optimizer_networkx_rag_llama3/streamlit_app.py

# Once loaded, view the default schema visualization
# Upload metadata in JSON or CSV format for new schemas
```

## Additional Information

For loading metadata from external databases like Oracle or Snowflake, use SQLAlchemy to retrieve metadata and export it in JSON or CSV format for upload to the app.

Example code:
```python
# Example for Oracle
from sqlalchemy import create_engine, MetaData
engine = create_engine('oracle://user:password@host:port/dbname')
metadata = MetaData()
metadata.reflect(bind=engine)
```

## Future Enhancements

Potential areas for enhancement:
- **Expanded Database Compatibility**: Additional metadata extraction for databases like PostgreSQL and MySQL.
- **Automated RAG Techniques**: Implement retrieval-augmented generation (RAG) to enhance LLM’s responses based on live metadata.
- **Enhanced Visualization Options**: Allow customization of graph layout, node, and edge styles for better schema interpretation.

