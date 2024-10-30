
# streamlit_app.py

import streamlit as st
from modules.database_setup import setup_databases
from modules.graph_construction import construct_graph, add_metadata_to_graph
from modules.llm_analyzer import FlexibleDatabaseLLM
from modules.visualization import visualize_graph
import networkx as nx
import json
import pandas as pd
import os

# Title
st.title("Database Schema Optimizer and Visualizer")

# Sidebar options
st.sidebar.header("Options")
db_name = st.sidebar.text_input("Enter Database Name:", "uploaded_db")
debug = st.sidebar.checkbox("Enable Debug Mode", value=False)

# Initialize the example databases and load them
def load_example_graph():
    engine1, engine2, metadata1, metadata2 = setup_databases(debug=debug)
    graph = construct_graph(metadata1, metadata2, debug=debug)
    return graph

# Placeholder for Graph, initially with example databases loaded
graph = load_example_graph()

# Display Example Databases Information
st.sidebar.header("Example Databases Loaded")
st.sidebar.write("The example databases are loaded by default. Upload new metadata to overwrite.")

# Metadata Upload Section
st.sidebar.header("Upload Your Database Metadata")
file_upload = st.sidebar.file_uploader("Upload Metadata (JSON, CSV)", type=["json", "csv"])

# Load and process uploaded metadata if present
def parse_json_metadata(json_data, db_name, graph, debug=False):
    """Parse JSON metadata to add nodes and edges to the graph."""
    for table, columns in json_data.items():
        table_node = f"{db_name}.{table}"
        graph.add_node(table_node, type="table", db=db_name, label=f"Table: {table} ({db_name})")
        for column in columns:
            column_node_id = f"{db_name}.{table}.{column['name']}"
            graph.add_node(column_node_id, type="column", db=db_name, label=f"Column: {column['name']} ({table})", data_type=column['type'])
            graph.add_edge(table_node, column_node_id, relationship="contains")
    if debug:
        st.sidebar.write(f"JSON metadata for {db_name} processed.")
    return graph

def parse_csv_metadata(csv_data, db_name, graph, debug=False):
    """Parse CSV metadata to add nodes and edges to the graph."""
    for _, row in csv_data.iterrows():
        table_node = f"{db_name}.{row['table']}"
        graph.add_node(table_node, type="table", db=db_name, label=f"Table: {row['table']} ({db_name})")
        column_node_id = f"{db_name}.{row['table']}.{row['column']}"
        graph.add_node(column_node_id, type="column", db=db_name, label=f"Column: {row['column']} ({row['table']})", data_type=row['type'])
        graph.add_edge(table_node, column_node_id, relationship="contains")
    if debug:
        st.sidebar.write(f"CSV metadata for {db_name} processed.")
    return graph

# Process uploaded metadata and replace graph if uploaded
if file_upload:
    file_type = file_upload.name.split(".")[-1]
    graph = nx.DiGraph()  # Reset graph for new metadata
    if file_type == "json":
        metadata = json.load(file_upload)
        graph = parse_json_metadata(metadata, db_name, graph, debug=debug)
        st.sidebar.success("JSON Metadata Processed Successfully.")
    elif file_type == "csv":
        metadata = pd.read_csv(file_upload)
        graph = parse_csv_metadata(metadata, db_name, graph, debug=debug)
        st.sidebar.success("CSV Metadata Processed Successfully.")
else:
    st.sidebar.info("Default example databases are loaded.")

# Instructions for connecting to external databases
st.sidebar.header("Instructions for External Databases")
st.sidebar.write("To use other databases (e.g., Oracle, Snowflake), extract metadata and save as JSON or CSV for upload.")

st.sidebar.code("""
# Example: Extracting Oracle metadata
from sqlalchemy import create_engine, MetaData
engine = create_engine('oracle://user:password@host:port/dbname')
metadata = MetaData()
metadata.reflect(bind=engine)
""", language="python")

# Graph Visualization
st.subheader("Schema Graph Visualization")
fig = visualize_graph(graph, debug=debug)
st.pyplot(fig)  # Display graph in Streamlit

# LLM Schema Analysis
st.sidebar.header("Schema Analysis with LLM")
custom_prompt = st.sidebar.text_area("Enter Analysis Prompt", "Identify any tables that appear to be duplicates or serve similar purposes.")
if st.sidebar.button("Run Analysis"):
    llm_analyzer = FlexibleDatabaseLLM(graph, debug=debug)
    response = llm_analyzer.query_schema_with_prompt(custom_prompt)
    st.subheader("LLM Analysis Result")
    st.write(response)
