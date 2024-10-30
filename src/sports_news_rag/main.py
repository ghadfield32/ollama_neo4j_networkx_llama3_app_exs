
from modules.data_crawling import crawl_and_ingest
from modules.vector_store import create_vectorstore
from modules.decision_mechanism import decide_and_answer
from modules.fact_checker import final_fact_check
from modules.hyde_rag import contextual_retrieval  # Use the new contextual retrieval function

def main(debug=False):
    # Define test sites, including new ones
    sports_sites = ["https://www.nba.com/", "https://www.espn.com/", "https://www.nfl.com/"]

    all_documents = []

    # Step 1: Crawl and ingest data from test sites
    for site in sports_sites:
        documents = crawl_and_ingest(site, debug)
        
        # Confirm each document type and content after ingestion
        if debug:
            print(f"Documents from {site}: {[type(doc) for doc in documents]}")
            print(f"Number of documents ingested from {site}: {len(documents)}")
            for doc in documents[:3]:  # Print first few documents as a sample
                print(f"Sample content from {site}: {doc.page_content[:500]}...")  # Show the first 500 chars for brevity
        
        all_documents.extend(documents)

    # Flatten list in case of nested lists
    all_documents = [doc for doc in all_documents if isinstance(doc, Document)]
    
    # Step 2: Create vector store from ingested documents
    if debug:
        print(f"Total documents after flattening: {len(all_documents)}")

    if all_documents:
        vectorstore = create_vectorstore(all_documents, debug=debug)
        retriever = vectorstore.as_retriever()

        # Step 3: Ask a sample question and check the answer generation
        question = "What pick of the Draft was Bronny James jr?"
        initial_answer = contextual_retrieval(question, retriever, debug)

        # Step 4: Fact-check and print the answer
        final_answer = final_fact_check(question, initial_answer, retriever, debug)
        print(f"Final answer for the question '{question}': {final_answer}")
    else:
        print("No documents were ingested, please check the crawl_and_ingest function for errors with the selected sites.")

if __name__ == "__main__":
    main(debug=True)

