
# agent.py
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from nodes import create_chatbot
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from code_act_agent import create_code_act_agent

async def verify_mcp_connection(url):
    """
    Explicitly verify the MCP connection and available tools.
    """
    try:
        async with MultiServerMCPClient({"server": {"url": url, "transport": "sse", "timeout": 10}}) as client:
            tools = client.get_tools()
            print(f"[MCP CONNECTION] Verified connection to {url}. Available tools: {[tool.name for tool in tools]}")
            return True
    except Exception as e:
        print(f"[MCP ERROR] Could not connect to MCP server at {url}: {e}")
        return False

async def create_agent(docs_info=None):
    server_url = "http://localhost:8000/sse"
    
    # Explicit MCP connection verification
    if not await verify_mcp_connection(server_url):
        raise ConnectionError(f"Cannot connect to MCP at {server_url}")

    async with MultiServerMCPClient({
        "server": {
            "url": server_url,
            "transport": "sse",
            "timeout": 30
        }
    }) as client:
        tools = client.get_tools()
        print(f"[MCP] Connected to {server_url}. Tools fetched: {[tool.name for tool in tools]}")

        graph_builder = StateGraph(MessagesState)

        chatbot_node = create_chatbot(docs_info)
        graph_builder.add_node("chatbot", chatbot_node)
        
        # Add the CodeAct agent node for code execution queries.
        code_act_node = create_code_act_agent()
        graph_builder.add_node("code_act", code_act_node)
        # Connect the code_act node back to the chatbot node.
        graph_builder.add_edge("code_act", "chatbot")
        
        async def async_tool_executor(state):
            messages = state["messages"]
            last_message = messages[-1]
            print(f"[DEBUG TOOL EXECUTOR] Processing message: '{last_message.content}'")
            
            tool_calls = getattr(last_message, "tool_calls", None) or last_message.additional_kwargs.get("tool_calls", None)
            if not tool_calls:
                print("[DEBUG TOOL EXECUTOR] No tool calls found. Returning messages as is.")
                return {"messages": messages}
            
            new_messages = messages.copy()
            for tool_call in tool_calls:
                tool_name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name
                tool_args = tool_call.get("args", {}) if isinstance(tool_call, dict) else getattr(tool_call, "args", {})
                tool_id = tool_call.get("id", "tool-call-id") if isinstance(tool_call, dict) else getattr(tool_call, "id", "tool-call-id")
                print(f"[DEBUG TOOL EXECUTOR] Invoking tool: '{tool_name}' with arguments: {tool_args}")
                tool = next((t for t in tools if t.name == tool_name), None)
                if not tool:
                    error_msg = f"[DEBUG TOOL EXECUTOR] Tool '{tool_name}' not found. Valid tools: {[t.name for t in tools]}"
                    print(error_msg)
                    new_messages.append(AIMessage(content=error_msg))
                    continue
                try:
                    result = await tool.coroutine(**tool_args) if asyncio.iscoroutinefunction(tool.coroutine) else \
                            tool.func(**tool_args) if hasattr(tool, 'func') else tool(**tool_args)
                    print(f"[DEBUG TOOL EXECUTOR] Tool '{tool_name}' returned: {result}")
                    new_messages.append(ToolMessage(content=str(result), tool_call_id=tool_id, name=tool_name))
                except Exception as e:
                    error_detail = f"[DEBUG TOOL EXECUTOR] Error executing tool '{tool_name}': {e}"
                    print(error_detail)
                    new_messages.append(AIMessage(content=error_detail))
            return {"messages": new_messages}



        graph_builder.add_node("tools", async_tool_executor)

        def router(state):
            last_message = state["messages"][-1]
            text = last_message.content.lower() if hasattr(last_message, "content") else ""
            
            # Log the state of the last message
            print(f"[DEBUG ROUTER] Last message content: '{text}'")
            
            # If the message is an internal <think> block, route to 'tools' to break the cycle.
            if text.strip().startswith("<think>"):
                print("[DEBUG ROUTER] Detected internal thought. Routing decision: 'tools'")
                return "tools"
            
            nba_keywords = ["average points", "ppg", "average ppg", "calculate average", "compute average", "determine average"]
            code_keywords = ["execute code", "code:"]
            
            if any(keyword in text for keyword in nba_keywords + code_keywords):
                print("[DEBUG ROUTER] Keywords detected. Routing decision: 'code_act'")
                return "code_act"
            if "career statistics" in text and "nba" in text:
                print("[DEBUG ROUTER] Detected 'career statistics' with 'nba'. Routing decision: 'tools'")
                return "tools"
            
            has_tool_calls = bool(getattr(last_message, "tool_calls", None) or last_message.additional_kwargs.get("tool_calls"))
            route = "tools" if has_tool_calls else "end"
            print(f"[DEBUG ROUTER] Routing decision based on tool calls: '{route}'")
            return route





        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", router, {
            "tools": "tools",
            "code_act": "code_act",  # explicitly added to fix KeyError
            "end": END
        })
        graph_builder.add_edge("tools", "chatbot")

        graph = graph_builder.compile()
        return graph, client


    def router(state):
        last_message = state["messages"][-1]
        text = last_message.content.lower() if hasattr(last_message, "content") else ""
        
        nba_keywords = ["average points", "ppg", "average ppg", "calculate average"]
        code_keywords = ["execute code", "code:", "calculate", "compute", "determine"]

        # New logic: explicitly route NBA calculation tasks to code_act
        if any(keyword in text for keyword in nba_keywords + code_keywords):
            print("[ROUTER] Detected NBA calculation query. Routing to 'code_act'.")
            return "code_act"
        if "career statistics" in text and "nba" in text:
            return "tools"
        
        has_tool_calls = bool(getattr(last_message, "tool_calls", None) or last_message.additional_kwargs.get("tool_calls"))
        return "tools" if has_tool_calls else "end"




        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", router, {"tools": "tools", "end": END})
        graph_builder.add_edge("tools", "chatbot")

        graph = graph_builder.compile()
        return graph, client


