from langchain_ollama import OllamaEmbeddings, ChatOllama

def self_rag(question, initial_answer, debug=False):
    """Refine an initial answer by performing self-reflection and improvements."""
    llm = ChatOllama(model="llama3.2", temperature=0)
    if debug:
        print(f"Initial answer before self-refinement: {initial_answer}")
    
    max_reflections = 2  # Number of self-reflection iterations
    for i in range(max_reflections):
        # Self-reflection step
        reflect_prompt = f"Answer: {initial_answer}\n\nReflect on the answer and identify any areas for improvement."
        reflection = llm.invoke([{"role": "user", "content": reflect_prompt}]).content

        if debug:
            print(f"Reflection result for iteration {i+1}: {reflection}")

        # If no improvements are needed, break out of the loop
        if "no improvements" in reflection.lower():
            if debug:
                print(f"No further improvements suggested after {i+1} iterations.")
            break
        else:
            # Improve the answer based on the reflection
            improve_prompt = f"Based on the reflection: {reflection}\n\nProvide an improved answer to the question: {question}"
            initial_answer = llm.invoke([{"role": "user", "content": improve_prompt}]).content

            if debug:
                print(f"Improved answer after iteration {i+1}: {initial_answer}")

    return initial_answer

def main(debug=False):
    # Sample usage for testing
    question = "What pick of the Draft was Bronny James Jr?"
    initial_answer = "Bronny James Jr. was selected 55th"
    refined_answer = self_rag(question, initial_answer, debug=debug)
    if debug:
        print(f"Final refined answer: {refined_answer}")

if __name__ == "__main__":
    main(debug=True)
