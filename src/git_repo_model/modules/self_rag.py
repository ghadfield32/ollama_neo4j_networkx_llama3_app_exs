
from langchain_ollama import OllamaEmbeddings, ChatOllama

def self_rag(question, initial_answer, debug=False):
    llm = ChatOllama(model="llama3.2", temperature=0)
    if debug:
        print(f"Initial answer before self-refinement: {initial_answer}")
    
    max_reflections = 2
    for i in range(max_reflections):
        reflect_prompt = f"Answer: {initial_answer}\n\nReflect on the answer and identify areas for improvement."
        reflection = llm.invoke([{"role": "user", "content": reflect_prompt}]).content

        if debug:
            print(f"Reflection result for iteration {i+1}: {reflection}")

        if "no improvements" in reflection.lower():
            if debug:
                print(f"No further improvements suggested after {i+1} iterations.")
            break
        else:
            improve_prompt = f"Based on the reflection: {reflection}\n\nProvide an improved answer to the question: {question}"
            initial_answer = llm.invoke([{"role": "user", "content": improve_prompt}]).content

            if debug:
                print(f"Improved answer after iteration {i+1}: {initial_answer}")

    return initial_answer

def main(debug=False):
    question = "What are effective techniques for optimizing local file storage?"
    initial_answer = "Local file storage optimization requires strategies such as compression and proper file structure."
    refined_answer = self_rag(question, initial_answer, debug=debug)
    
    if debug:
        print(f"Final refined answer: {refined_answer}")

if __name__ == "__main__":
    main(debug=True)

