from database_setup import setup_databases
from graph_construction import construct_graph, add_metadata_to_graph
from llm_analyzer import FlexibleDatabaseLLM
from visualization import visualize_graph
import networkx as nx
import json
import pandas as pd

def process_uploaded_metadata(file_path, db_name, debug=False):
    """
    Process metadata from uploaded files (JSON, CSV, or SQLAlchemy metadata).
    Supports SQLAlchemy, JSON, and CSV formats to dynamically build the schema.
    """
    graph = nx.DiGraph()
    
    if file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            metadata = json.load(f)
        graph = parse_json_metadata(metadata, db_name, graph, debug)
    
    elif file_path.endswith('.csv'):
        metadata = pd.read_csv(file_path)
        graph = parse_csv_metadata(metadata, db_name, graph, debug)

    elif isinstance(file_path, MetaData):  # For SQLAlchemy metadata
        add_metadata_to_graph(file_path, db_name, graph, debug)

    else:
        raise ValueError("Unsupported file format. Please upload JSON, CSV, or SQLAlchemy metadata.")
    
    return graph

def parse_json_metadata(json_data, db_name, graph, debug=False):
    """
    Parse JSON metadata to build nodes and edges in the graph.
    JSON should include table and column definitions.
    """
    for table, columns in json_data.items():
        table_node = f"{db_name}.{table}"
        graph.add_node(table_node, type="table", db=db_name, label=f"Table: {table} ({db_name})")
        
        for column in columns:
            column_node_id = f"{db_name}.{table}.{column['name']}"
            graph.add_node(column_node_id, type="column", db=db_name, label=f"Column: {column['name']} ({table})", data_type=column['type'])
            graph.add_edge(table_node, column_node_id, relationship="contains")

        if debug:
            print(f"JSON metadata for {db_name} added to graph.")
    
    return graph

def parse_csv_metadata(csv_data, db_name, graph, debug=False):
    """
    Parse CSV metadata to build nodes and edges in the graph.
    Assumes CSV has 'table', 'column', and 'type' columns.
    """
    for _, row in csv_data.iterrows():
        table_node = f"{db_name}.{row['table']}"
        graph.add_node(table_node, type="table", db=db_name, label=f"Table: {row['table']} ({db_name})")
        
        column_node_id = f"{db_name}.{row['table']}.{row['column']}"
        graph.add_node(column_node_id, type="column", db=db_name, label=f"Column: {row['column']} ({row['table']})", data_type=row['type'])
        graph.add_edge(table_node, column_node_id, relationship="contains")
    
    if debug:
        print(f"CSV metadata for {db_name} added to graph.")
    
    return graph

def main(file_path=None, file_type="sqlalchemy", db_name="uploaded_db", debug=False):
    """
    Main function to automate database optimization:
    - Allows input of various data formats (JSON, CSV, SQLAlchemy metadata)
    - Constructs the database schema graph
    - Visualizes it and performs schema analysis using LLM
    """
    # Step 1: Setup initial example databases if no file is provided
    if file_type == "sqlalchemy" and file_path is None:
        engine1, engine2, metadata1, metadata2 = setup_databases(debug=debug)
        graph = construct_graph(metadata1, metadata2, debug=debug)
    else:
        # Process uploaded metadata and create a new graph
        graph = process_uploaded_metadata(file_path, db_name, debug=debug)
    
    # Step 2: Visualize the graph
    visualize_graph(graph, debug=debug)
    
    # Step 3: LLM Analysis
    llm_analyzer = FlexibleDatabaseLLM(graph, debug=debug)
    prompt = "Identify any tables that appear to be duplicates or serve similar purposes."
    response = llm_analyzer.query_schema_with_prompt(prompt)
    print("\nLLM Analysis Result:")
    print(response)

if __name__ == "__main__":
    main(debug=True)
