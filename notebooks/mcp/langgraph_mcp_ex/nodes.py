
# nodes.py
from server import get_tools
from langgraph.graph import MessagesState
# Removed OpenAI dependency; now using ChatOllama for an open-source LLM.
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from datetime import datetime
import os

# Create a dynamic system prompt that includes the current date and tool list.
def get_system_prompt(docs_info=None):
    system_prompt = f"""
    Today is {datetime.now().strftime("%Y-%m-%d")}
    You are a helpful AI Assistant that can use the following tools:
    - data_visualization: Create charts with Python and matplotlib.
    - python_repl: Execute Python code.
    - nba_player_stats: Retrieve NBA player career statistics (overall, last 5 seasons).
    - search_nba_player: Search for NBA players by full name.
    - nba_player_game_logs: Retrieve game logs for an NBA player for a specific season.
    - nba_team_stats: Retrieve team statistics for a given NBA team and season.
    - nba_player_stats_regularseason: Retrieve regular season career totals.
    - nba_player_stats_postseason: Retrieve postseason career totals.
    - nba_player_stats_career_totals: Retrieve an aggregated career totals summary (regular season only).
    - nba_player_stats_best_season: Retrieve the player's best season based on points per game.
    
    IMPORTANT: When a query asks for NBA career statistics, select the most appropriate tool:
      • Use nba_player_stats for overall career stats.
      • Use nba_player_stats_regularseason for regular season only.
      • Use nba_player_stats_postseason for postseason only.
      • Use nba_player_stats_career_totals for a career totals summary.
      • Use nba_player_stats_best_season to find the best season based on key metrics.
    
    Do not output raw tool responses; simply acknowledge execution and summarize the result.
    When using image generation or data visualization tools, only confirm execution without revealing raw details.
    Once a tool has been executed, do not call it again in the same answer.
    """
    if docs_info:
        docs_context = "\n\nYou have access to these documents:\n"
        for doc in docs_info:
            docs_context += f"- {doc['name']}: {doc['type']}\n"
        system_prompt += docs_context
        
    system_prompt += "\nYou should always answer in the same language as the user's query."
    return system_prompt




# Instantiate the LLM using ChatOllama, configured to use Llama3.2.
# Updated for deepseek-r1
llm = ChatOllama(model="deepseek-r1:latest", temperature=0.7, max_tokens=512)


# Create the chatbot node that processes user input and interacts with the LLM.
def create_chatbot(docs_info=None):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(get_system_prompt(docs_info)),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    # Pipe the prompt into the LLM chain.
    chain = prompt | llm
    
    def chatbot(state: MessagesState):
        # Normalize messages to the proper format.
        if isinstance(state["messages"], str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=state["messages"])]
        else:
            messages = state["messages"]
            
        response = chain.invoke(messages)
        return {"messages": messages + [response]}
    
    return chatbot
