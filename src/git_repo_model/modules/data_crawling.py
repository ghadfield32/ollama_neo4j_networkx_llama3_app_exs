
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.schema import Document
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import NotebookLoader
import concurrent.futures
import pandas as pd

def crawl_and_ingest(directory_path, file_types=None, debug=False):
    """
    Crawls the specified directory for files with given extensions,
    processes the contents, and returns documents ready for RAG ingestion.

    Parameters:
    - directory_path: Path to the directory to crawl.
    - file_types: List of file extensions to include (e.g., [".py", ".md", ".csv"]). 
                  Default includes various code and data formats.
    - debug: Boolean flag to print debug information.
    """
    # Expanded default file types to include more programming languages and data formats
    if file_types is None:
        file_types = [".py", ".ipynb", ".txt", ".md", ".csv", ".js", ".html", 
                      ".css", ".json", ".yaml", ".yml", ".xml", ".r", ".cpp", 
                      ".java", ".scala", ".sql"]

    if debug:
        print(f"Starting to load files from directory: {directory_path} with file types: {file_types}")

    docs = []

    # Traverse the directory for specified file types
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)

            if any(file.endswith(ext) for ext in file_types):
                if debug:
                    print(f"Found file: {file_path}")

                if file.endswith(".csv"):  # CSV files
                    try:
                        df = pd.read_csv(file_path, on_bad_lines = 'skip')
                        if df.empty:
                            if debug:
                                print(f"CSV file is empty: {file_path}")
                            continue
                        content = df.to_string()  # Convert to string for ingestion
                        docs.append(Document(page_content=content, metadata={"file_name": file_path}))
                    except pd.errors.EmptyDataError:
                        if debug:
                            print(f"Empty CSV file skipped: {file_path}")

                elif file.endswith(".ipynb"):  # Jupyter Notebooks
                    try:
                        loader = NotebookLoader(file_path, include_outputs=False, max_output_length=0)
                        notebook_docs = loader.load()
                        docs.extend(notebook_docs)
                    except Exception as e:
                        if debug:
                            print(f"Error reading {file_path}: {e}")

                else:  # Text and other code files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    docs.append(Document(page_content=content, metadata={"file_name": file_path}))

    if debug:
        print(f"Total documents loaded: {len(docs)}")
    return docs


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
        print(f"Generated propositions: {propositions[:5]}...")  # Print first 5 propositions for brevity

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
    # Specify the local repo path and file types to include
    directory_path = "../../../"
    # Expanded file types to include various code and documentation formats
    file_types = [".py", ".md", ".csv", ".ipynb", ".html", ".json", ".yaml", ".r", ".cpp", ".java", ".scala", ".sql"]
    documents = crawl_and_ingest(directory_path, file_types, debug)
    if debug:
        print(f"Total documents processed for ingestion: {len(documents)}")


if __name__ == "__main__":
    main(debug=True)
