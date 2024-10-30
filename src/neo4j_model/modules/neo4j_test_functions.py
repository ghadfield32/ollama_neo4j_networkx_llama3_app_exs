from utility_functions import load_env_variables, connect_to_neo4j
from neo4j import GraphDatabase
import pandas as pd
import os
from dotenv import load_dotenv

def query_to_dataframe(driver, query, parameters=None):
    """Runs a Cypher query and returns a pandas DataFrame."""
    print(f"Running query: {query}")
    print(f"With parameters: {parameters}")
    
    with driver.session() as session:
        result = session.run(query, parameters)
        columns = result.keys()
        data = [record.values() for record in result]
        
        print(f"Query returned {len(data)} records.")
        return pd.DataFrame(data, columns=columns)

def get_player_statistics(driver, season):
    """Retrieves player statistics for a given season."""
    print(f"Fetching player statistics for season: {season}")
    query = """
    MATCH (p:Player)-[:POSSESSES]->(stat:Statistics {season: $season})
    RETURN p.name AS player, stat.ppg AS points_per_game, stat.assists_total AS assists, stat.rebounds_total AS rebounds
    ORDER BY stat.ppg DESC
    LIMIT 10
    """
    parameters = {"season": season}
    return query_to_dataframe(driver, query, parameters)

def get_player_contracts(driver, season):
    """Retrieves player contracts for a given season."""
    print(f"Fetching player contracts for season: {season}")
    query = """
    MATCH (p:Player)-[:HAS_CONTRACT]->(c:Contract {season: $season})
    RETURN p.name AS player, c.salary AS salary, c.duration AS contract_duration
    ORDER BY c.salary DESC
    LIMIT 10
    """
    parameters = {"season": season}
    return query_to_dataframe(driver, query, parameters)

def get_top_teams_by_salary(driver, season):
    """Retrieves teams ranked by total salary for a given season."""
    print(f"Fetching top teams by salary for season: {season}")
    query = """
    MATCH (t:Team)<-[:HAS_PLAYED_FOR]-(p:Player)-[:HAS_CONTRACT]->(c:Contract {season: $season})
    RETURN t.name AS team, SUM(c.salary) AS total_salary
    ORDER BY total_salary DESC
    LIMIT 10
    """
    parameters = {"season": season}
    return query_to_dataframe(driver, query, parameters)

def get_players_with_high_injury_risk(driver):
    """Retrieves players with a high injury risk."""
    print("Fetching players with high injury risk...")
    query = """
    MATCH (p:Player)-[:SUFFERED]->(i:Injury)
    WHERE i.risk >= 0.8
    RETURN p.name AS player, i.total_days AS total_days_injured, i.risk AS injury_risk
    ORDER BY i.risk DESC
    LIMIT 10
    """
    return query_to_dataframe(driver, query)

def get_team_strategies(driver):
    """Retrieves team strategies and associated needs."""
    print("Fetching team strategies and needs...")
    query = """
    MATCH (t:Team)
    RETURN t.name AS team, t.strategy AS strategy, t.needs AS needs
    """
    return query_to_dataframe(driver, query)

def get_top_players_by_vorp(driver, season):
    """Retrieves top players by VORP for a given season."""
    print(f"Fetching top players by VORP for season: {season}")
    query = """
    MATCH (p:Player)-[:POSSESSES]->(stat:Statistics {season: $season})
    RETURN p.name AS player, stat.vorp_total AS vorp
    ORDER BY stat.vorp_total DESC
    LIMIT 10
    """
    parameters = {"season": season}
    return query_to_dataframe(driver, query, parameters)

def main(season='2023-24'):
    """Main function to connect to Neo4j, retrieve data, and print the results."""
    print("Starting Neo4j test function execution...")
    
    try:
        driver = connect_to_neo4j()
        
        print("Retrieving player statistics...")
        player_stats_df = get_player_statistics(driver, season)
        print("Player Statistics:\n", player_stats_df)
        
        print("\nRetrieving player contracts...")
        player_contracts_df = get_player_contracts(driver, season)
        print("Player Contracts:\n", player_contracts_df)
        
        print("\nRetrieving top teams by salary...")
        team_salary_df = get_top_teams_by_salary(driver, season)
        print("Top Teams by Salary:\n", team_salary_df)
        
        print("\nRetrieving players with high injury risk...")
        injury_risk_df = get_players_with_high_injury_risk(driver)
        print("Players with High Injury Risk:\n", injury_risk_df)
        
        print("\nRetrieving team strategies and needs...")
        team_strategy_df = get_team_strategies(driver)
        print("Team Strategies:\n", team_strategy_df)
        
        print("\nRetrieving top players by VORP...")
        top_vorp_df = get_top_players_by_vorp(driver, season)
        print("Top Players by VORP:\n", top_vorp_df)
    
    except Exception as e:
        print(f"An error occurred during Neo4j data testing: {e}")

if __name__ == '__main__':
    main()
