
import streamlit as st
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader
from langchain.schema import Document
import networkx as nx

from graph_rag import GraphRAG  # Import your GraphRAG class
from visualizer import Visualizer  # Import Visualizer for plotting


# Initialize global variables
graph_rag = None

# Function to process uploaded PDF
def process_pdf(file):
    pdf_reader = PdfReader(file)
    # Read content from all pages
    documents = [Document(page_content=page.extract_text()) for page in pdf_reader.pages]
    return documents

# Set up the main Streamlit UI
st.title("Knowledge Graph from PDF with LLM")

# PDF upload and processing
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Process the uploaded PDF
    documents = process_pdf(uploaded_file)
    st.write(f"Uploaded **{uploaded_file.name}** with **{len(documents)} pages** processed.")

    # Initialize GraphRAG with the processed documents
    with st.spinner("Processing the PDF and building the knowledge graph..."):
        graph_rag = GraphRAG(documents)
    st.success("PDF has been processed and the knowledge graph has been created.")

    # Visualization Section
    st.write("### Knowledge Graph Visualization")
    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(graph_rag.knowledge_graph.graph, k=1, iterations=50)
    nx.draw(graph_rag.knowledge_graph.graph, pos, with_labels=True, ax=ax,
            node_size=500, node_color="lightblue", edge_color="gray")
    st.pyplot(fig)

# Query section
if graph_rag is not None:
    st.write("### Query the Knowledge Graph")
    query = st.text_input("Enter your query", "What is the main cause of climate change?")

    if st.button("Submit Query"):
        with st.spinner("Processing your query..."):
            response, traversal_path, filtered_content = graph_rag.query(query)
            st.write("### Response to your query:")
            st.write(response)

            # Visualize traversal
            st.write("### Traversal Path Visualization")
            fig, ax = Visualizer.visualize_traversal(graph_rag.knowledge_graph.graph, traversal_path)
            st.pyplot(fig)

            # Show traversal logic
            st.write("### Traversal Logic and Filtered Content")
            for i, node in enumerate(traversal_path):
                st.write(f"**Step {i + 1} - Node {node}:**")
                content = filtered_content.get(node, 'No content available')
                st.write(content)
                st.write("---")
