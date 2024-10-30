from langchain_community.retrievers import TavilySearchAPIRetriever

tavily_retriever = TavilySearchAPIRetriever(k=3)

def tavily_search(question, debug=False):
    docs = tavily_retriever.invoke(question)
    context = "\n\n".join(f"Source {i+1} ({doc.metadata.get('source')}):\n{doc.page_content}" for i, doc in enumerate(docs))
    if debug:
        print(f"Web search context retrieved: {context[:500]}...")  # Display first 500 chars
    return context

def main(debug=False):
    question = "Tell me about file optimization?"
    context = tavily_search(question, debug)
    if debug:
        print(f"Retrieved context from Tavily search: {context}")

if __name__ == "__main__":
    main(debug=True)
