from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
import concurrent.futures  # For parallel processing
import os

# Define the home directory for the project
HOME_DIR = "/workspaces/custom_ollama_docker"

def crawl_and_ingest(url, debug=False):
    """
    Crawls a given URL, splits the document, generates propositions, 
    runs quality checks, and returns processed documents.
    """
    if debug:
        print(f"Crawling data from: {url}")

    # Load documents from the web URL
    loader = WebBaseLoader(url)
    docs = loader.load()

    if debug:
        print(f"Loaded {len(docs)} documents from {url}")
        print(f"Document types loaded: {[type(doc) for doc in docs]}")

    # Split the documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    document_chunks = text_splitter.split_documents(docs)

    if debug:
        print(f"Number of document chunks generated: {len(document_chunks)}")

    # Process each chunk to generate high-quality propositions
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_chunk, chunk, debug) for chunk in document_chunks]
        processed_documents = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Flatten the processed_documents to remove any nested list structures
    proposition_documents = [doc for sublist in processed_documents for doc in (sublist if isinstance(sublist, list) else [sublist])]

    if debug:
        print(f"Total number of processed documents after flattening: {len(proposition_documents)}")
        print(f"Types of processed documents: {[type(doc) for doc in proposition_documents]}")

    return proposition_documents


def process_chunk(chunk, debug=False):
    """
    Generates and quality checks propositions for a given chunk.
    """
    propositions = generate_propositions(chunk.page_content, debug)
    high_quality_propositions = quality_check_propositions(propositions, debug)
    return [Document(page_content=prop) for prop in high_quality_propositions]

def generate_propositions(text, debug=False):
    """
    Generates propositions from the given text using an LLM.
    """
    llm = ChatOllama(model="llama3.2", temperature=0)
    max_length = 2000
    text = text[:max_length] if len(text) > max_length else text

    proposition_prompt = (
        f"Break down the following text into concise, complete, and meaningful factual statements:\n\n{text}\n\n"
        "Provide each proposition as a separate statement."
    )
    response = llm.invoke([{"role": "user", "content": proposition_prompt}]).content

    propositions = [prop.strip() for prop in response.split('\n') if prop.strip()]

    if debug:
        print(f"Generated propositions: {propositions}")

    return propositions

def quality_check_propositions(propositions, debug=False):
    """
    Checks the quality of the propositions for accuracy, clarity, completeness, and conciseness.
    """
    llm = ChatOllama(model="llama3.2", temperature=0)
    high_quality_propositions = []

    batch_size = 5
    for i in range(0, len(propositions), batch_size):
        batch = propositions[i:i + batch_size]
        quality_prompt = (
            f"Evaluate the following propositions for accuracy, clarity, completeness, and conciseness. "
            f"Score each aspect from 1 to 10 and provide an overall assessment. Reply with 'pass' if the proposition is acceptable:\n\n"
            f"{', '.join(batch)}"
        )
        response = llm.invoke([{"role": "user", "content": quality_prompt}]).content

        results = response.lower().split('\n')

        if debug:
            print(f"Batch being processed: {batch}")
            print(f"LLM Response: {response}")
            print(f"Number of results received: {len(results)}, Number of propositions in batch: {len(batch)}")

        min_length = min(len(results), len(batch))
        for j in range(min_length):
            if 'pass' in results[j]:
                high_quality_propositions.append(batch[j])

    return high_quality_propositions



def main(debug=False):
    # Sample sites for testing
    sports_sites = ["https://www.nba.com/", "https://www.espn.com/"]
    all_documents = []
    for site in sports_sites:
        documents = crawl_and_ingest(site, debug)
        all_documents.extend(documents)
    if debug:
        print(f"Total documents ingested: {len(all_documents)}")

if __name__ == "__main__":
    main(debug=True)
