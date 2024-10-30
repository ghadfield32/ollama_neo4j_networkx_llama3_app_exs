
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage

def load_llm(model_name):
    """Loads the LLM model."""
    llm = ChatOllama(model=model_name, temperature=0)
    print(f"LLM model '{model_name}' loaded successfully.")
    return llm

def test_llm(llm, prompt):
    """Runs a test prompt and shows the output."""
    response = llm([HumanMessage(content=prompt)])
    print(f"Test Prompt: {prompt}\nLLM Response: {response.content}")
    return response.content

def main(model_name='tomasonjo/llama3-text2cypher-demo', debug=False):
    try:
        if debug:
            print("Debug mode enabled.")
        
        # Step 1: Load LLM
        llm = load_llm(model_name)
        
        # Step 2: Test LLM with a sample prompt
        test_prompt = "Why is the sky blue?"
        response = test_llm(llm, test_prompt)
        
        if debug:
            print("LLM Response Retrieved.")
        return response
    
    except Exception as e:
        print(f"An error occurred during LLM model loading: {e}")

# Example usage without argparse
if __name__ == '__main__':
    # You can call main with debug=True to see additional print statements for debugging
    main(debug=True)
