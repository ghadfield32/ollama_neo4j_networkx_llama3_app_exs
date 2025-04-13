Running the Example

    Install dependencies:
    Run pip install -r requirements.txt.

    Start the MCP server:
    In a terminal, run the server (for example, by running python server.py). This will start the MCP server with Server-Sent Events (SSE).

    Run the Agent:
    In another terminal, run python main.py and enter your query when prompted.

This complete example ties together the article’s concepts:

    Initialization with LangGraph and MCP.

    Dynamic tool execution via an asynchronous tool executor.

    Routing and state management to determine if further tool calls are needed.

    Integration of various tools (image generation, code execution, data visualization) in one coherent multi–agent chatbot.