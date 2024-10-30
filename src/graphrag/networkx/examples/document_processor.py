
import nltk
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings  # Updated import
from langchain_community.vectorstores import Chroma  # Updated import

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

class DocumentProcessor:
    def __init__(self):
        """
        Initializes the DocumentProcessor with a text splitter and embeddings.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.embeddings = OllamaEmbeddings(model="llama3.2")

    def process_documents(self, documents):
        splits = self.text_splitter.split_documents(documents)
        vector_store = Chroma.from_documents(
            splits,
            self.embeddings,
            persist_directory="../../../data/graph_chroma_dbs"
        )
        return splits, vector_store
