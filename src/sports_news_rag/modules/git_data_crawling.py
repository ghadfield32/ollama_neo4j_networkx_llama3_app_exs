
import requests
from langchain.schema import Document

def extract_repo_info(repo_url):
    """
    Extracts the username and repository name from a GitHub URL.
    """
    parts = repo_url.rstrip('/').split('/')
    if len(parts) < 5:
        raise ValueError("Invalid GitHub repository URL. Must be in the format: https://github.com/username/repo")
    return parts[-2], parts[-1]

def fetch_repo_tree(username, repo_name, debug=False):
    """
    Fetches the main branch file tree from a GitHub repository.
    """
    api_url = f"https://api.github.com/repos/{username}/{repo_name}/git/trees/main?recursive=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    tree = response.json().get("tree", [])
    
    if debug:
        print(f"Fetched {len(tree)} items from GitHub API for {repo_name}")
    
    return tree

def load_file_content(username, repo_name, file_info, debug=False):
    """
    Loads the content of a single file from a GitHub repository.
    """
    file_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/{file_info['path']}"
    file_content = requests.get(file_url).text
    
    if debug:
        print(f"Loaded file: {file_info['path']}")
    
    return Document(page_content=file_content, metadata={"file_name": file_info["path"]})

def load_github_repo(repo_url, file_types=None, debug=False):
    """
    Load the main branch files from a GitHub repository and return them as documents.
    
    Parameters:
    - repo_url: URL of the GitHub repository.
    - file_types: List of file extensions to include (e.g., [".py", ".md", ".csv"]). 
                  Defaults to a broad selection of code and data formats.
    - debug: Boolean flag to print debug information.
    """
    username, repo_name = extract_repo_info(repo_url)
    tree = fetch_repo_tree(username, repo_name, debug)
    
    # Default file types if none are provided
    if file_types is None:
        file_types = [
            ".py", ".ipynb", ".txt", ".md", ".csv", ".js", ".html", 
            ".css", ".json", ".yaml", ".yml", ".xml", ".r", ".cpp", 
            ".java", ".scala", ".sql"
        ]
    
    documents = []
    for file_info in tree:
        if file_info["type"] == "blob" and any(file_info["path"].endswith(ext) for ext in file_types):
            document = load_file_content(username, repo_name, file_info, debug)
            documents.append(document)
    
    if debug:
        print(f"Total files loaded from GitHub repository '{repo_name}': {len(documents)}")
    
    return documents

def main():
    # Test URL - Replace this with any public GitHub repository URL
    test_repo_url = "https://github.com/ghadfield32/coach_analysis"  # Example URL
    
    # Enable debug to view process details
    debug = True
    
    # Specify file types to include, if desired
    file_types = [".py", ".md", ".csv", ".ipynb", ".html", ".json", ".yaml", ".r", ".cpp", ".java", ".scala", ".sql"]
    
    try:
        documents = load_github_repo(test_repo_url, file_types, debug)
        print("\nLoaded documents:")
        for doc in documents:
            print(f"File: {doc.metadata['file_name']} - Content preview: {doc.page_content[:100]}...")  # Show first 100 characters of each document
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
