
from document_processor import DocumentProcessor
from knowledge_graph import KnowledgeGraph
from query_engine import QueryEngine
from visualizer import Visualizer
from langchain_ollama import ChatOllama, OllamaEmbeddings

class GraphRAG:
    def __init__(self, documents):
        """
        Initializes the GraphRAG system.
        """
        self.llm = ChatOllama(model="llama3.2", temperature=0)
        self.embedding_model = OllamaEmbeddings(model="llama3.2")
        self.document_processor = DocumentProcessor()  # Use the DocumentProcessor
        self.knowledge_graph = KnowledgeGraph()
        self.query_engine = None
        self.visualizer = Visualizer()
        self.process_documents(documents)

    def process_documents(self, documents):
        splits, vector_store = self.document_processor.process_documents(documents)
        self.knowledge_graph.build_graph(splits, self.llm, self.embedding_model)
        self.query_engine = QueryEngine(vector_store, self.knowledge_graph)


    def query(self, query: str):
        """
        Handles a query using the query engine.
        """
        response, traversal_path, filtered_content = self.query_engine.query(query)
        return response, traversal_path, filtered_content

