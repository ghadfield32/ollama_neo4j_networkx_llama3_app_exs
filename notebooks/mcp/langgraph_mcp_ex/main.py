
# main.py
import streamlit as st
import asyncio
from agent import create_agent
from langchain_core.messages import HumanMessage

async def main():
    # Create the agent and keep the MCP client alive.
    agent, client = await create_agent()
    
    # Get user input (using input() for a console example)
    user_input = input("What would you like to ask? ")
    initial_message = HumanMessage(content=user_input)
    
    try:
        print("Processing your request...")
        config = {"recursion_limit": 50}  # Increase the recursion limit for debugging
        result = await agent.ainvoke({"messages": [initial_message]}, config=config)

        
        # Iterate over returned messages and print them.
        for message in result["messages"]:
            if hasattr(message, "type") and message.type == "human":
                print(f"User: {message.content}")
            elif hasattr(message, "type") and message.type == "tool":
                print(f"Tool Result: {message.content}")
                if "image" in message.content.lower() and "url" in message.content.lower():
                    print("Image Generated Successfully!")
            else:
                print(f"AI: {message.content}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # In a real application, the client would remain active as long as needed.

if __name__ == "__main__":
    asyncio.run(main())
