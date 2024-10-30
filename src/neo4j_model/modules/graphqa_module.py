
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

# --- SECTION 1: ENVIRONMENT SETUP AND CONNECTIONS ---

def load_environment():
    """Loads environment variables from the .env file."""
    dotenv_path = os.path.join(os.getcwd(), '../../.env')
    load_dotenv(dotenv_path)

def create_neo4j_driver():
    """Initializes the Neo4j driver using credentials from environment variables."""
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(username, password))

def initialize_graph_connection():
    """Initializes the Neo4jGraph connection for LangChain's graph QA chain."""
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    return Neo4jGraph(url=uri, username=username, password=password)


# --- SECTION 2: PROMPT AND LLM INITIALIZATION ---

def initialize_llm():
    """Initializes the ChatOllama model for Cypher query generation."""
    cypher_model = 'tomasonjo/llama3-text2cypher-demo'
    return ChatOllama(model=cypher_model, temperature=0)

def create_cypher_prompt_template():
    """Creates a PromptTemplate for generating Cypher queries based on schema."""
    
    schema = """
    Nodes:
    - Player: Represents an NBA player. Properties: name, age, position, years_of_service, injury_risk, season_salary, season, per, ws, bpm, vorp.
    - Team: Represents an NBA team. Properties: name, team_id, needs, strategy, cap_space.
    - Season: Represents a specific NBA season. Properties: name.
    - Contract: Represents player contracts. Properties: player_name, salary, cap, luxury_tax, duration, player_option, team_option, no_trade_clause.
    - Statistics: Represents player statistics. Properties: player, season, ppg, assists_total, rebounds_total, steals_total, blocks_total, turnovers_total, personal_fouls_total, win_shares_total, offensive_win_shares_total, defensive_win_shares_total, vorp_total, games_played.
    - Injury: Represents player injury details. Properties: player, total_days, injury_periods, risk, injury_history.

    Relationships:
    - Player -[:HAS_PLAYED_FOR]-> Team
    - Player -[:PARTICIPATED_IN]-> Season
    - Player -[:HAS_CONTRACT]-> Contract
    - Player -[:POSSESSES]-> Statistics
    - Player -[:SUFFERED]-> Injury
    - Team -[:HAS_PLAYER]-> Player
    - Team -[:CURRENT_TEAM]-> Player
    """

    return PromptTemplate(
        template=f"""
        You are a Cypher query expert for a Neo4j database with the following schema:
        
        Schema:
        {schema}
        
        Use the schema above to generate a Cypher query that answers the given question.
        Make the query flexible by using case-insensitive matching and partial string matching where appropriate.
        Focus on searching player statistics, contracts, and team details.

        Now, generate a Cypher query for the following question:

        Question: {{question}}
        
        Cypher Query:
        """,
        input_variables=["question"],
    )


# --- SECTION 3: QUERY GENERATION AND MODIFICATION ---

def generate_query(llm, prompt_template, schema, question):
    """Generates a Cypher query from an LLM using a schema and question."""
    prompt_text = prompt_template.format(schema=schema, question=question)
    print(f"Generated Prompt:\n{prompt_text}")
    llm_response = llm([HumanMessage(content=prompt_text)])
    return llm_response.content.strip()

def add_per_game_calculations(query):
    """Adjusts the query for per-game calculations by dividing cumulative stats by games played."""
    print(f"Original Query Before Per-Game Calculations:\n{query}")
    
    total_stat_mappings = {
        "ppg": "stat.ppg / stat.games_played",
        "assists_total": "stat.assists_total / stat.games_played",
        "rebounds_total": "stat.rebounds_total / stat.games_played",
        # Other stat mappings can go here
    }
    
    for total_stat, per_game_stat in total_stat_mappings.items():
        query = re.sub(fr"stat\.{total_stat}", per_game_stat, query, flags=re.IGNORECASE)
    
    print(f"Adjusted Query After Per-Game Calculations:\n{query}")
    return query

def handle_missing_properties(missing_properties, query):
    """Removes references to missing properties from the Cypher query."""
    if not missing_properties:
        return query
    
    for prop in missing_properties:
        query = re.sub(fr"stat\.{prop}\s*", '', query)
    print(f"Adjusted Query After Removing Missing Properties:\n{query}")
    return query


# --- SECTION 4: VALIDATION AND EXECUTION ---

def validate_generated_query(query, driver, schema):
    """Validates the generated Cypher query against the actual schema to identify potential issues."""
    schema_properties = [
        re.sub(r'\.\n-.*$', '', prop.strip().lower())
        for prop in schema.split("Properties: ")[1].split(",")
    ]
    
    with driver.session() as session:
        result = session.run("CALL db.schema.nodeTypeProperties()")
        db_properties = {record["propertyName"].lower() for record in result}
    
    missing_properties = [prop for prop in schema_properties if prop not in db_properties]
    print(f"Missing Properties: {missing_properties}")
    
    return missing_properties

def run_cypher_query(query, driver):
    """Executes the given Cypher query on the Neo4j database and returns the results."""
    print(f"Executing Query:\n{query}")
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]


# --- SECTION 5: MAIN LOOP AND EXECUTION ---

def agent_repl_loop(question, driver, llm, schema, prompt_template, repl_tool):
    """Runs the REPL loop to handle query generation and debugging autonomously."""
    results = {
        "prompt_text": None,
        "generated_query": None,
        "adjusted_query": None,
        "query_result": None,
    }
    
    try:
        # Generate initial query
        results["prompt_text"] = prompt_template.format(schema=schema, question=question)
        raw_query = generate_query(llm, prompt_template, schema, question)
        print(f"Generated Raw Query:\n{raw_query}")
        
        results["generated_query"] = raw_query

        # Validate and adjust query
        missing_properties = validate_generated_query(raw_query, driver, schema)
        adjusted_query = handle_missing_properties(missing_properties, raw_query)
        final_query = add_per_game_calculations(adjusted_query)
        
        results["adjusted_query"] = final_query

        # Execute query
        query_results = run_cypher_query(final_query, driver)
        print("Query Results:")
        for record in query_results:
            print(record)
        
        results["query_result"] = query_results

    except Exception as e:
        print(f"Error occurred: {e}")
        if repl_tool:
            repl_tool.func(f"print('{str(e)}')")
    
    return results  # Return the results dictionary


# Define the schema for the graph, fixing VORP issue and capitalized properties
schema = """
Nodes:
- Player: Represents an NBA player. Properties: name, age, position, years_of_service, injury_risk, season_salary, season, per, ws, bpm, vorp.
- Team: Represents an NBA team. Properties: name, team_id, needs, strategy, cap_space.
- Season: Represents a specific NBA season. Properties: name.
- Contract: Represents player contracts. Properties: player_name, salary, cap, luxury_tax, duration, player_option, team_option, no_trade_clause.
- Statistics: Represents player statistics. Properties: player, season, ppg, assists_total, rebounds_total, steals_total, blocks_total, turnovers_total, personal_fouls_total, win_shares_total, offensive_win_shares_total, defensive_win_shares_total, vorp_total, games_played.
- Injury: Represents player injury details. Properties: player, total_days, injury_periods, risk, injury_history.

Relationships:
- Player -[:HAS_PLAYED_FOR]-> Team
- Player -[:PARTICIPATED_IN]-> Season
- Player -[:HAS_CONTRACT]-> Contract
- Player -[:POSSESSES]-> Statistics
- Player -[:SUFFERED]-> Injury
- Team -[:HAS_PLAYER]-> Player
- Team -[:CURRENT_TEAM]-> Player
"""

def main():
    """Main function to set up connections, load schema, and run REPL loop."""
    load_environment()
    driver = create_neo4j_driver()
    llm = initialize_llm()
    graph = initialize_graph_connection()
    repl_tool = Tool(name="python_repl", description="Python shell for REPL.", func=PythonREPL().run)
    
    # Sample question
    sample_question = "Who are the top 5 players in the 2023-24 season based on assist total?"
    
    # Prompt setup
    prompt_template = create_cypher_prompt_template()
    agent_repl_loop(sample_question, driver, llm, schema, prompt_template, repl_tool)


if __name__ == "__main__":
    main()
