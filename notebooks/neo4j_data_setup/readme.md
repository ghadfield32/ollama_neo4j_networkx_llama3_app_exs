# NBA Player Data Analysis with Neo4j and Streamlit

This repository is a tool for analyzing NBA player data, contracts, and team strategies using a Neo4j database and Streamlit interface. The application allows you to explore player statistics, assess trade value, and query the data using GraphQA, powered by Llama3.

---

## Table of Contents
1. [Repository Structure](#repository-structure)
2. [Setup](#setup)
3. [Usage](#usage)
4. [App Workflow](#app-workflow)
5. [Modules Overview](#modules-overview)

---

## Repository Structure

- `data_preprocessing.py`: Handles data loading and preprocessing for Neo4j.
- `neo4j_data_preprocess_ingest.py`: Manages Neo4j database connections, schema setup, and data ingestion.
- `neo4j_test_functions.py`: Contains test functions to retrieve data from Neo4j.
- `model_loading.py`: Loads and tests the LLM model.
- `graphqa_functions.py`: Sets up the GraphQA system with LangChain and Llama3.
- `utility_functions.py`: Shared utility functions for environment setup and Neo4j connection.
- `main.py`: Entry point to run and test the project.
- `streamlit_app.py`: The main Streamlit application for interactive analysis.

---

## Setup

### Prerequisites

1. **Neo4j**: Install and start a Neo4j instance. This can be done locally or through Docker.
2. **Python**: Requires Python 3.7 or higher.
3. **Environment Variables**: Create a `.env` file with the following variables:
   ```env
   NEO4J_URI=
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=

   ```

### Installation

1. Clone the repository and install dependencies.
   ```bash
   git clone https://github.com/ghadfield32/custom_ollama_docker
   cd custom_ollama_docker

   ```

2. Docker build and open in Dev container
   
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

   Ctrl+P > Rebuild and reopen in devcontainer

3. Ollama pull model

    terminal: ollama pull tomasonjo/llama3-text2cypher-demo 
    **use whatever model you want, this one is finetuned wtih text2cypher on huggingface

4. **Start Neo4j** and ensure it is accessible via the credentials in `.env`.
    - Add a .env file with these parameters at the root of the folder (custom_ollama_docker)
    # .env
    TAVILY_API_KEY=
    LANGSMITH_API_KEY=
    SQLITE_DB_PATH_1=../data/databases/db1.sqlite
    SQLITE_DB_PATH_2=../data/databases/db2.sqlite
    NEO4J_URI=
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=

    - goto https://neo4j.com/ and set up your neo4j aurodb connection and fill in the uri username and password

5. **Streamlit app** open app to see capabilities: load/clean data, ingest into neo4j, typical queries, and llamacypher model results
    ```bash
    streamlit run src/neo4j_model/streamlit_app.py
    ```
---



## Usage

1. **Prepare Data**: Start with `data_preprocessing.py` to load, clean, and preprocess NBA player data. The processed data will be saved for Neo4j ingestion.
2. **Ingest Data into Neo4j**: Run `neo4j_data_preprocess_ingest.py` to ingest the cleaned data into the Neo4j database, setting up the schema and constraints.
3. **Run the Streamlit App**:
   ```bash
   streamlit run src/neo4j_model/streamlit_app.py
   ```
4. **Interact with the App**: Use the sidebar options in the Streamlit app to select and perform various analyses, from data retrieval to advanced GraphQA.

---

## App Workflow

1. **Step 1: Data Loading and Cleaning**  
   This step handles loading raw NBA data, cleaning it, and saving it in a format ready for Neo4j ingestion.

2. **Step 2: Data Ingestion into Neo4j**  
   Ingest the cleaned data into Neo4j, where schema constraints and indexes are applied. This prepares the data for querying.

3. **Step 3: Test Neo4j Queries**  
   Select and run predefined Cypher queries (e.g., player statistics, contract details, team strategies). The queries can be customized to retrieve insights relevant to trade analysis.

4. **Step 4: GraphQA**  
   Uses Llama3 to transform natural language questions into Cypher queries. The tool then executes these queries in Neo4j and returns the results for in-depth analysis.

---

## Modules Overview

### 1. `data_preprocessing.py`
   - **Purpose**: Load raw NBA data, perform initial checks, handle missing values, and add suffixes to cumulative columns for clarity.  
   - **Key Functions**:
     - `load_data()`: Loads raw CSV data.
     - `clean_data()`: Cleans data, removing unnecessary columns and handling null values.
     - `map_team_ids()`: Maps team abbreviations to IDs.
     - `add_suffixes_to_columns()`: Renames columns for clarity.

### 2. `neo4j_data_preprocess_ingest.py`
   - **Purpose**: Connect to Neo4j, set up the schema, and ingest cleaned data.
   - **Key Functions**:
     - `create_constraint_if_not_exists()`: Ensures unique constraints for data integrity.
     - `insert_enhanced_data()`: Inserts nodes and relationships representing players, teams, and contracts.
     - `calculate_and_set_trade_value()`: Placeholder function for calculating a player's trade value.

### 3. `neo4j_test_functions.py`
   - **Purpose**: Test and retrieve data from Neo4j, focusing on critical queries for analysis.
   - **Key Functions**:
     - `get_player_statistics()`: Retrieves player stats by season.
     - `get_team_strategies()`: Returns team strategies and needs.
     - `get_top_players_by_vorp()`: Identifies players with the highest VORP for a given season.

### 4. `model_loading.py`
   - **Purpose**: Load and test the LLM for Cypher query generation.
   - **Key Functions**:
     - `load_llm()`: Loads the ChatOllama LLM.
     - `test_llm()`: Sends a test prompt and verifies LLM response.

### 5. `graphqa_functions.py`
   - **Purpose**: Integrates Neo4j with LangChain's GraphQA to answer natural language questions about the data.
   - **Key Functions**:
     - `agent_repl_loop()`: Manages REPL loop to refine generated Cypher queries.
     - `add_per_game_calculations()`: Adjusts Cypher queries for per-game metrics.

### 6. `streamlit_app.py`
   - **Purpose**: Main Streamlit interface. Provides a step-by-step UI to load data, query Neo4j, and use GraphQA.
   - **Workflow Steps**:
     - Data loading and cleaning.
     - Neo4j ingestion.
     - Query testing.
     - GraphQA with natural language queries.

