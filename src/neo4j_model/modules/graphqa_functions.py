from utility_functions import load_env_variables, connect_to_neo4j

from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import Tool
import os
from dotenv import load_dotenv
import re

# Step 2: Setup the GraphCypherQAChain
def setup_graphqa_chain(llm, graph, cypher_prompt):
    """Sets up the GraphCypherQAChain with schema, cypher_prompt, and configurations."""
    
    return GraphCypherQAChain.from_llm(
        cypher_llm=llm,
        qa_llm=llm,
        validate_cypher=True,
        graph=graph,
        verbose=True,
        return_intermediate_steps=True,
        return_direct=True,
        cypher_prompt=cypher_prompt,
        allow_dangerous_requests=True,
    )

# Step 3: Validate the generated Cypher query against the schema
def validate_generated_query(query, driver, schema):
    """Validates the generated Cypher query against the actual schema to identify potential issues."""
    schema_properties = [re.sub(r'\.\n-.*$', '', prop.strip().lower()) for prop in schema.split("Properties: ")[1].split(",")]
    
    with driver.session() as session:
        result = session.run("CALL db.schema.nodeTypeProperties()")
        db_properties = {record["propertyName"].lower() for record in result}
    
    missing_properties = [prop for prop in schema_properties if prop not in db_properties]
    print(f"Missing Properties: {missing_properties}")
    
    return missing_properties

# Step 4: Handle missing properties in the generated query
def handle_missing_properties(missing_properties, query):
    """Removes references to missing properties from the Cypher query."""
    if not missing_properties:
        return query
    
    for prop in missing_properties:
        query = re.sub(fr"stat\.{prop}\s*", '', query)
    
    print(f"Adjusted Query After Removing Missing Properties:\n{query}")
    return query

# Step 5: Add per-game calculations to the query if necessary
def add_per_game_calculations(query):
    """Adjusts the query for per-game calculations by dividing cumulative stats by games played."""
    print(f"Original Query Before Per-Game Calculations:\n{query}")
    
    total_stat_mappings = {
        "ppg": "stat.ppg / stat.games_played",
        "assists_total": "stat.assists_total / stat.games_played",
        "rebounds_total": "stat.rebounds_total / stat.games_played",
        "steals_total": "stat.steals_total / stat.games_played",
        "blocks_total": "stat.blocks_total / stat.games_played",
        "turnovers_total": "stat.turnovers_total / stat.games_played",
        "personal_fouls_total": "stat.personal_fouls_total / stat.games_played",
        "win_shares_total": "stat.win_shares_total / stat.games_played",
        "offensive_win_shares_total": "stat.offensive_win_shares_total / stat.games_played",
        "defensive_win_shares_total": "stat.defensive_win_shares_total / stat.games_played",
        "vorp_total": "stat.vorp_total / stat.games_played",
    }
    
    for total_stat, per_game_stat in total_stat_mappings.items():
        query = re.sub(fr"stat\.{total_stat}", per_game_stat, query, flags=re.IGNORECASE)
    
    print(f"Adjusted Query After Per-Game Calculations:\n{query}")
    return query

# Step 6: Run the Cypher query
def run_cypher_query(query, driver):
    """Executes the Cypher query on the Neo4j database and returns the results."""
    print(f"Executing Query:\n{query}")
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]


# Step 7: Agent REPL loop for error handling and query debugging
def agent_repl_loop(sample_question, schema, driver, llm, repl_tool, cypher_prompt):
    """Runs the REPL loop to handle query generation and errors, and returns intermediate steps for debugging."""
    # Initialize variables to return intermediate steps
    prompt_text = cypher_prompt.format(schema=schema, question=sample_question)
    llm_response_content = ""
    adjusted_query = ""
    query_result = []

    try:
        # Step 1: Generate the initial Cypher query using the language model
        llm_response = llm([HumanMessage(content=prompt_text)])
        llm_response_content = llm_response.content.strip()
        
        # Display generated query
        print(f"Generated Query:\n{llm_response_content}")

        # Step 2: Add per-game calculations if needed
        adjusted_query = add_per_game_calculations(llm_response_content)
        
        # Step 3: Execute the adjusted Cypher query on Neo4j
        query_result = run_cypher_query(adjusted_query, driver)
        
        # Display query results
        print("Query Results:")
        for record in query_result:
            print(record)

    except Exception as e:
        # Capture error information and use the REPL tool to debug
        print(f"Error occurred: {e}")
        repl_output = repl_tool.func(f"print('{str(e)}')")
        print(f"Python REPL Output for Debugging:\n{repl_output}")
    
    # Return all relevant data for display in the Streamlit app
    return {
        "prompt_text": prompt_text,
        "generated_query": llm_response_content,
        "adjusted_query": adjusted_query,
        "query_result": query_result,
    }


# Step 8: Main function to initialize and run the agent with a test question
def main(question='Who are the top 5 players in the 2023-24 season based on assist total?'):
    try:
        driver = connect_to_neo4j()
        graph = Neo4jGraph(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"), password=os.getenv("NEO4J_PASSWORD"))
        llm = ChatOllama(model='tomasonjo/llama3-text2cypher-demo', temperature=0)
        python_repl = PythonREPL()
        repl_tool = Tool(
            name="python_repl",
            description="A Python shell for executing commands.",
            func=python_repl.run,
        )
        
        # Define schema and cypher_prompt
        schema = """
        Nodes:
        - Player: Represents an NBA player. Properties: name, age, position, years_of_service, injury_risk, season_salary, season, per, ws, bpm, vorp.
        - Team: Represents an NBA team. Properties: name, team_id, needs, strategy, cap_space.
        - Season: Represents a specific NBA season. Properties: name.
        - Contract: Represents player contracts. Properties: player_name, salary, cap, luxury_tax, duration, player_option, team_option, no_trade_clause.
        - Statistics: Represents player statistics. Properties: player, season, ppg, assists_total, rebounds_total, steals_total, blocks_total, turnovers_total, personal_fouls_total, win_shares_total, offensive_win_shares_total, defensive_win_shares_total, vorp_total, games_played.
        - Injury: Represents player injury details. Properties: player, total_days, injury_periods, risk, injury_history.
        """
        
        cypher_prompt = PromptTemplate(
            template="""
            You are a Cypher query expert for a Neo4j database with the following schema:
            
            Schema:
            Nodes:
            - Player: Represents an NBA player with properties like name, assists_total, and other statistics.
            - Team: Represents an NBA team with a property 'season' (e.g., '2023-24').
            
            Relationships:
            - :PARTICIPATED_IN (Player)-[:PARTICIPATED_IN]->(Team): Links players to the teams for a given season.

            Use the schema above to generate a Cypher query that answers the given question.
            Make the query flexible by using case-insensitive matching and partial string matching where appropriate.
            
            Question: {question}
            
            Cypher Query:
            """,
            input_variables=["schema", "question"]
        )

        
        agent_repl_loop(question, schema, driver, llm, repl_tool, cypher_prompt)
    
    except Exception as e:
        print(f"An error occurred during GraphQA operations: {e}")

if __name__ == '__main__':
    main()
