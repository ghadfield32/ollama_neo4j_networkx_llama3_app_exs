
from graphqa_module import (
    load_environment,
    create_neo4j_driver,
    initialize_llm,
    create_cypher_prompt_template,
    validate_generated_query,
    add_per_game_calculations,
    handle_missing_properties,
    agent_repl_loop,
)
from utility_functions import connect_to_neo4j
from data_cleaning import (
    load_data, 
    data_initial_summary, 
    clean_data, 
    check_for_duplicates, 
    map_team_ids, 
    add_suffixes_to_columns, 
    final_data_check
)
from neo4j_data_preprocess_ingest import (
    clear_database,
    clear_constraints_and_indexes,
    setup_schema_with_cleanup,
    setup_indexes,
    insert_enhanced_data,
    calculate_and_set_trade_value
)
from neo4j_test_functions import get_player_statistics, get_player_contracts
from model_loading import load_llm, test_llm

import os
from dotenv import load_dotenv
import pandas as pd


def check_neo4j_connection():
    """Tests Neo4j connection using utility functions."""
    print("Testing Neo4j connection...")
    try:
        driver = connect_to_neo4j()
        driver.close()
        print("Neo4j connection successful.")
    except Exception as e:
        print(f"Neo4j connection test failed: {e}")


def run_data_cleaning():
    """Executes data cleaning pipeline."""
    load_dotenv('/workspaces/custom_ollama_docker/.env')
    data_file = os.getenv('DATA_FILE', '/workspaces/custom_ollama_docker/data/neo4j/raw/nba_player_data_final_inflated.csv')
    output_file = os.getenv('CLEANED_DATA_FILE', '/workspaces/custom_ollama_docker/data/neo4j/processed/nba_player_data_cleaned.csv')
    
    try:
        dataframe = load_data(data_file)
        print(f"Loaded data with shape: {dataframe.shape}")
        
        data_initial_summary(dataframe, debug=True)
        
        # Data cleaning and validation pipeline
        dataframe_cleaned = clean_data(dataframe, debug=True)
        check_for_duplicates(dataframe_cleaned, debug=True)
        dataframe_mapped = map_team_ids(dataframe_cleaned, debug=True)
        dataframe_final = add_suffixes_to_columns(dataframe_mapped, debug=True)
        final_data_check(dataframe_final, debug=True)
        
        dataframe_final.to_csv(output_file, index=False)
        print(f"Preprocessed data saved to {output_file}")
    except Exception as e:
        print(f"Data cleaning process failed: {e}")


def run_data_ingestion():
    """Executes data ingestion into Neo4j."""
    load_dotenv('/workspaces/custom_ollama_docker/.env')
    data_file = '/workspaces/custom_ollama_docker/data/neo4j/processed/nba_player_data_cleaned.csv'

    try:
        driver = connect_to_neo4j()
        dataframe = pd.read_csv(data_file)
        data_dicts = dataframe.to_dict(orient='records')
        print(f"Loaded {len(data_dicts)} records from {data_file}.")

        with driver.session() as session:
            clear_database(session)
            clear_constraints_and_indexes(session)
            setup_schema_with_cleanup(session)
            setup_indexes(session)
            print("Database schema and indexes set up successfully.")

            for player_data in data_dicts:
                session.execute_write(insert_enhanced_data, player_data)
                session.execute_write(calculate_and_set_trade_value, player_data["Player"])

            print("Data inserted into Neo4j successfully.")
    except Exception as e:
        print(f"Data ingestion process failed: {e}")


def run_neo4j_test_queries(season='2023-24'):
    """Tests Neo4j data retrieval functions."""
    print(f"Running Neo4j test queries for season {season}...")
    try:
        driver = connect_to_neo4j()
        
        print("Retrieving player statistics...")
        player_stats_df = get_player_statistics(driver, season)
        print("Player Statistics:\n", player_stats_df.head())
        
        print("\nRetrieving player contracts...")
        player_contracts_df = get_player_contracts(driver, season)
        print("Player Contracts:\n", player_contracts_df.head())
    except Exception as e:
        print(f"Neo4j test queries failed: {e}")


def run_model_loading(model_name='tomasonjo/llama3-text2cypher-demo'):
    """Loads and tests the specified LLM model."""
    try:
        llm = load_llm(model_name)
        test_prompt = "Why is the sky blue?"
        response = test_llm(llm, test_prompt)
        print(f"Model test response: {response}")
    except Exception as e:
        print(f"Model loading process failed: {e}")


def run_graphqa(question='Who are the top 5 players in the 2023-24 season based on assist total?'):
    """Runs the GraphQA agent for the specified question."""
    load_environment()
    driver = create_neo4j_driver()
    llm = initialize_llm()
    prompt_template = create_cypher_prompt_template()
    
    try:
        agent_repl_loop(
            question=question,
            driver=driver,
            llm=llm,
            schema=schema,
            prompt_template=prompt_template,
            repl_tool=Tool(name="python_repl", description="Python shell for REPL.", func=PythonREPL().run)
        )
    except Exception as e:
        print(f"GraphQA agent execution failed: {e}")


def main():
    """Main function to run the pipeline sequentially."""
    check_neo4j_connection()
    
    # # Data cleaning
    # run_data_cleaning()
    
    # # Data ingestion into Neo4j
    # run_data_ingestion()
    
    # Neo4j test queries
    run_neo4j_test_queries(season='2023-24')
    
    # Model loading and testing
    run_model_loading(model_name='tomasonjo/llama3-text2cypher-demo')
    
    # GraphQA setup and query test
    run_graphqa(question='Who are the top 5 players in the 2023-24 season based on assist total?')

if __name__ == "__main__":
    main()
