import networkx as nx

def add_metadata_to_graph(metadata, db_name, graph, debug=False):
    for table_name, table in metadata.tables.items():
        table_node = f"{db_name}.{table_name}"
        graph.add_node(table_node, type="table", db=db_name, label=f"Table: {table_name} ({db_name})")

        for column in table.columns:
            column_node_id = f"{db_name}.{table_name}.{column.name}"
            graph.add_node(column_node_id, type="column", db=db_name, label=f"Column: {column.name} ({table_name})", data_type=str(column.type))
            graph.add_edge(table_node, column_node_id, relationship="contains")

        for fk in table.foreign_keys:
            parent_column = f"{db_name}.{fk.parent.table.name}.{fk.parent.name}"
            referenced_column = f"{db_name}.{fk.column.table.name}.{fk.column.name}"
            graph.add_edge(parent_column, referenced_column, relationship="foreign_key")

    if debug:
        print(f"Metadata for {db_name} added to graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges.")

def construct_graph(metadata1, metadata2, debug=False):
    graph = nx.DiGraph()
    add_metadata_to_graph(metadata1, "example1", graph, debug)
    add_metadata_to_graph(metadata2, "example2", graph, debug)
    return graph

def main(debug=False):

    _, _, metadata1, metadata2 = setup_databases(debug)
    graph = construct_graph(metadata1, metadata2, debug=debug)
    if debug:
        print("Graph construction completed.")
    return graph

if __name__ == "__main__":
    main(debug=True)
