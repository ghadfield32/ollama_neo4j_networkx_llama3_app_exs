
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from modules.graphqa_module import (
    load_environment,
    create_neo4j_driver,
    initialize_llm,
    create_cypher_prompt_template,
    agent_repl_loop,
)
from modules.utility_functions import connect_to_neo4j
from modules.data_cleaning import (
    load_data,
    data_initial_summary,
    clean_data,
    check_for_duplicates,
    map_team_ids,
    add_suffixes_to_columns,
    final_data_check
)
from modules.neo4j_data_preprocess_ingest import (
    clear_database,
    clear_constraints_and_indexes,
    setup_schema_with_cleanup,
    setup_indexes,
    insert_enhanced_data,
    calculate_and_set_trade_value
)
from modules.neo4j_test_functions import (
    get_player_statistics,
    get_player_contracts,
    get_top_teams_by_salary,
    get_players_with_high_injury_risk,
    get_team_strategies,
    get_top_players_by_vorp
)


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

# App setup
st.title("NBA Player Data Analysis with Neo4j and Llama3")
st.sidebar.title("Workflow Steps")

# --- Step 1: Load and Clean Data ---
if st.sidebar.checkbox("Step 1: Load and Clean Data"):
    st.subheader("Data Loading and Cleaning")
    load_dotenv('/workspaces/custom_ollama_docker/.env')
    data_file = st.text_input("Enter path to raw data file:", "/workspaces/custom_ollama_docker/data/neo4j/raw/nba_player_data_final_inflated.csv")
    output_file = "/workspaces/custom_ollama_docker/data/neo4j/processed/nba_player_data_cleaned.csv"
    
    if st.button("Load and Clean Data"):
        try:
            dataframe = load_data(data_file)
            st.write("Initial Data Loaded:", dataframe.head())
            
            # Data cleaning steps
            data_initial_summary(dataframe, debug=True)
            dataframe_cleaned = clean_data(dataframe, debug=True)
            check_for_duplicates(dataframe_cleaned, debug=True)
            dataframe_mapped = map_team_ids(dataframe_cleaned, debug=True)
            dataframe_final = add_suffixes_to_columns(dataframe_mapped, debug=True)
            final_data_check(dataframe_final, debug=True)
            
            dataframe_final.to_csv(output_file, index=False)
            st.success(f"Preprocessed data saved to {output_file}")
            st.write("Cleaned Data:", dataframe_final.head())
        except Exception as e:
            st.error(f"Data cleaning process failed: {e}")

# --- Step 2: Ingest Data into Neo4j ---
if st.sidebar.checkbox("Step 2: Ingest Data into Neo4j"):
    st.subheader("Data Ingestion into Neo4j")
    load_dotenv('/workspaces/custom_ollama_docker/.env')
    data_file = "/workspaces/custom_ollama_docker/data/neo4j/processed/nba_player_data_cleaned.csv"
    
    if st.button("Ingest Data"):
        try:
            driver = connect_to_neo4j()
            dataframe = pd.read_csv(data_file)
            data_dicts = dataframe.to_dict(orient='records')
            st.write(f"Loaded {len(data_dicts)} records for ingestion.")
            
            with driver.session() as session:
                clear_database(session)
                clear_constraints_and_indexes(session)
                setup_schema_with_cleanup(session)
                setup_indexes(session)
                st.write("Database schema and indexes set up successfully.")
                
                for player_data in data_dicts:
                    session.execute_write(insert_enhanced_data, player_data)
                    session.execute_write(calculate_and_set_trade_value, player_data["Player"])

                st.success("Data inserted into Neo4j successfully.")
        except Exception as e:
            st.error(f"Data ingestion process failed: {e}")

# --- Step 3: Test Neo4j Queries ---
if st.sidebar.checkbox("Step 3: Test Neo4j Queries"):
    st.subheader("Test Data Retrieval from Neo4j")
    season = st.text_input("Enter season (e.g., '2023-24'):", "2023-24")
    query_type = st.selectbox("Select a query to run:", [
        "Player Statistics",
        "Top Teams by Salary",
        "Top Players by VORP"
    ])

    if st.button("Run Test Query"):
        try:
            driver = connect_to_neo4j()
            
            if query_type == "Player Statistics":
                st.write("Retrieving player statistics...")
                query = """
                MATCH (p:Player)-[:POSSESSES]->(stat:Statistics {season: $season})
                RETURN p.name AS player, stat.ppg AS points_per_game, stat.assists_total AS assists
                """
                st.code(query, language="cypher")
                player_stats_df = get_player_statistics(driver, season)
                st.write("Player Statistics:", player_stats_df.head())
            
                
            elif query_type == "Top Teams by Salary":
                st.write("Retrieving top teams by salary...")
                query = """
                MATCH (t:Team)<-[:HAS_PLAYED_FOR]-(p:Player)-[:HAS_CONTRACT]->(c:Contract {season: $season})
                RETURN t.name AS team, SUM(c.salary) AS total_salary
                ORDER BY total_salary DESC
                LIMIT 5
                """
                st.code(query, language="cypher")
                team_salary_df = get_top_teams_by_salary(driver, season)
                st.write("Top Teams by Salary:", team_salary_df.head())
                
                
            elif query_type == "Top Players by VORP":
                st.write("Retrieving top players by VORP...")
                query = """
                MATCH (p:Player)-[:POSSESSES]->(stat:Statistics {season: $season})
                RETURN p.name AS player, stat.vorp_total AS vorp
                ORDER BY stat.vorp_total DESC
                LIMIT 5
                """
                st.code(query, language="cypher")
                top_vorp_df = get_top_players_by_vorp(driver, season)
                st.write("Top Players by VORP:", top_vorp_df.head())
                
        except Exception as e:
            st.error(f"Neo4j test queries failed: {e}")



# --- Step 4: GraphQA with Llama3 ---
if st.sidebar.checkbox("Step 4 : GraphQA with Llama3"):
    st.subheader("GraphQA - Ask Questions on NBA Data")
    load_environment()
    driver = create_neo4j_driver()
    llm = initialize_llm()
    prompt_template = create_cypher_prompt_template()
    
    question = st.text_input("Enter your question about NBA data:", "Who are the top 5 players in the 2023-24 season based on assist total?")
    
    if st.button("Run GraphQA"):
        try:
            # Run the agent REPL loop and capture all intermediate outputs
            results = agent_repl_loop(
                question=question,  # Pass `question` instead of `sample_question`
                schema=schema,
                driver=driver,
                llm=llm,
                repl_tool=None,  # Optional: Python REPL for interactive debugging
                prompt_template=prompt_template
            )
            
            # Display the generated prompt
            st.write("Generated Prompt:")
            st.code(results["prompt_text"], language="plaintext")

            # Display the initial generated query
            st.write("Generated Query:")
            st.code(results["generated_query"], language="cypher")

            # Display the adjusted query if it was modified
            if results["adjusted_query"] != results["generated_query"]:
                st.write("Adjusted Query After Per-Game Calculations:")
                st.code(results["adjusted_query"], language="cypher")

            # Show the query results
            if results["query_result"]:
                st.write("Query Results:")
                st.write(pd.DataFrame(results["query_result"]))  # Display results as a DataFrame
            else:
                st.write("No results returned from the query.")

        except Exception as e:
            st.error(f"GraphQA agent execution failed: {e}")


