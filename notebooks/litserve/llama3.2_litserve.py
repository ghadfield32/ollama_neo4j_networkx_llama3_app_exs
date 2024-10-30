from langchain_ollama import OllamaEmbeddings, ChatOllama
import litserve as ls

class MultipleModelAPI(ls.LitAPI):
    def setup(self, device):
        # Load both models: Llama 3.2 for text generation and Ollama Embeddings for embeddings
        self.llm = ChatOllama(model="llama3.2", temperature=0.7)  # For text generation
        self.embed_model = OllamaEmbeddings(model="llama3.2")     # For embeddings

    def decode_request(self, request):
        # Determine the endpoint model and prompt from the request
        model_name = request.get("model_name", "").lower()
        prompt = request.get("prompt", "")
        return model_name, prompt

    def predict(self, x):
        model_name, prompt = x
        if model_name == "llm":
            # Text generation request
            print(f"Text generation request: {prompt}")
            try:
                response = self.llm.invoke([{"role": "user", "content": prompt}]).content
                return {"text": response}
            except Exception as e:
                print(f"Error during text generation: {e}")
                return {"error": f"Text generation error: {str(e)}"}

        elif model_name == "embed":
            # Embedding generation request
            print(f"Embedding request input: {prompt} (type: {type(prompt)})")
            try:
                print(f"Calling embed_query with input: {prompt} (type: {type(prompt)})")
                embedding_result = self.embed_model.embed_query(prompt)  # Fetch full embedding array
                print(f"Embedding result: {embedding_result} (type: {type(embedding_result)})")
                
                # Return the full embedding array
                return {"embedding": embedding_result}
            except Exception as e:
                print(f"Error while generating embedding: {e}")
                return {"error": f"Embedding error: {str(e)}"}


        else:
            return {"error": "Invalid model_name provided. Use 'llm' for generation or 'embed' for embeddings."}

    def encode_response(self, output):
        # Format the output with either text or embedding based on the response
        return {"text": output.get("text"), "embedding": output.get("embedding")}

if __name__ == "__main__":
    api = MultipleModelAPI()
    server = ls.LitServer(api)
    server.run(port=8080)
