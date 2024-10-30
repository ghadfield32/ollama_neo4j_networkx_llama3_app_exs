from utility_functions import load_env_variables, connect_to_neo4j

import pandas as pd
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv



# Function to create constraints only if they don't already exist
def create_constraint_if_not_exists(session, constraint_query, constraint_name):
    check_query = f"SHOW CONSTRAINTS WHERE name = '{constraint_name}'"
    result = session.run(check_query)
    if result.single():
        print(f"Constraint '{constraint_name}' already exists.")
    else:
        session.run(constraint_query)
        print(f"Successfully created constraint: {constraint_name}")



# Function to delete duplicate nodes before creating uniqueness constraints
def delete_duplicate_nodes(session, label, property_name):
    print(f"Deleting duplicate nodes for {label} based on {property_name}...")
    delete_query = f"""
    MATCH (n:{label})
    WITH n.{property_name} AS prop, COLLECT(n) AS nodes
    WHERE SIZE(nodes) > 1
    UNWIND TAIL(nodes) AS duplicateNode
    DETACH DELETE duplicateNode
    """
    session.run(delete_query)
    print(f"Duplicate nodes deleted for {label} based on {property_name}.")

# Setup schema with constraints and cleanup
def setup_schema_with_cleanup(session):
    constraints = [
        {"query": "CREATE CONSTRAINT player_name_unique FOR (p:Player) REQUIRE p.name IS UNIQUE", "name": "player_name_unique"},
        {"query": "CREATE CONSTRAINT team_name_unique FOR (t:Team) REQUIRE t.name IS UNIQUE", "name": "team_name_unique"},
        {"query": "CREATE CONSTRAINT season_name_unique FOR (s:Season) REQUIRE s.name IS UNIQUE", "name": "season_name_unique"},
        {"query": "CREATE CONSTRAINT position_name_unique FOR (pos:Position) REQUIRE pos.name IS UNIQUE", "name": "position_name_unique"},
        {"query": "CREATE CONSTRAINT contract_unique FOR (c:Contract) REQUIRE (c.salary, c.player_name, c.season) IS UNIQUE", "name": "contract_unique"},
    ]

    cleanup_mappings = [
        {"label": "Player", "property": "name"},
        {"label": "Team", "property": "name"},
        {"label": "Season", "property": "name"},
        {"label": "Position", "property": "name"},
        {"label": "Contract", "property": "salary"}
    ]

    for mapping in cleanup_mappings:
        delete_duplicate_nodes(session, mapping["label"], mapping["property"])

    for constraint in constraints:
        create_constraint_if_not_exists(session, constraint["query"], constraint["name"])



def create_player_node(tx, player_data):
    query = """
    MERGE (p:Player {name: $name})
    ON CREATE SET p.age = $age,
                  p.position = $position,
                  p.years_of_service = $years_of_service,
                  p.injury_risk = $injury_risk,
                  p.season_salary = $salary,
                  p.season = $season,
                  p.per = $per,
                  p.ws = $ws,
                  p.bpm = $bpm,
                  p.vorp = $vorp
    """
    tx.run(query,
           name=player_data["Player"],
           age=player_data["Age"],
           position=player_data["Position"],
           years_of_service=player_data["Years of Service"],
           injury_risk=player_data["Injury_Risk"],
           salary=player_data["Salary"],
           season=player_data["Season"],
           per=player_data.get("PER"),
           ws=player_data.get("WS"),
           bpm=player_data.get("BPM"),
           vorp=player_data.get("VORP"))


def create_team_node(tx, team_name, team_id, team_data):
    query = """
    MERGE (t:Team {name: $name})
    ON CREATE SET t.team_id = $team_id,
                  t.needs = $needs,
                  t.strategy = $strategy,
                  t.cap_space = $cap_space
    """
    tx.run(query,
           name=team_name,
           team_id=team_id,
           needs=team_data.get("Needs"),
           strategy=team_data.get("Strategy"),
           cap_space=team_data.get("Cap Space"))


def create_season_node(tx, season):
    query = """
    MERGE (s:Season {name: $season})
    """
    tx.run(query, season=season)


def create_position_node(tx, position):
    query = """
    MERGE (pos:Position {name: $position})
    """
    tx.run(query, position=position)


def create_contract_node(tx, contract_data):
    query = """
    MERGE (c:Contract {player_name: $player_name, season: $season})
    ON CREATE SET c.salary = $salary,
                  c.cap = $cap,
                  c.luxury_tax = $luxury_tax,
                  c.duration = $duration,
                  c.player_option = $player_option,
                  c.team_option = $team_option,
                  c.no_trade_clause = $no_trade_clause
    """
    tx.run(query,
           player_name=contract_data["Player"],
           season=contract_data["Season"],
           salary=contract_data["Salary"],
           cap=contract_data["Salary Cap"],
           luxury_tax=contract_data["Luxury Tax"],
           duration=contract_data.get("Contract Duration"),
           player_option=contract_data.get("Player Option"),
           team_option=contract_data.get("Team Option"),
           no_trade_clause=contract_data.get("No Trade Clause"))


def delete_duplicate_contract_nodes(session):
    delete_query = """
    MATCH (c:Contract)
    WITH c.salary AS salary, c.player_name AS player_name, c.season AS season, COLLECT(c) AS contracts
    WHERE SIZE(contracts) > 1
    UNWIND TAIL(contracts) AS duplicateContract
    DETACH DELETE duplicateContract
    """
    session.run(delete_query)
    print("Duplicate Contract nodes deleted based on salary, player_name, and season.")


def create_statistics_node(tx, player_name, stats_data):
    query = """
    MERGE (stat:Statistics {player: $player, season: $season})
    ON CREATE SET 
        stat.ppg = $pts_total,               // Use total fields
        stat.assists_total = $ast_total,
        stat.rebounds_total = $trb_total,
        stat.steals_total = $stl_total,
        stat.blocks_total = $blk_total,
        stat.turnovers_total = $tov_total,
        stat.personal_fouls_total = $pf_total,
        stat.win_shares_total = $ws_total,
        stat.offensive_win_shares_total = $ows_total,
        stat.defensive_win_shares_total = $dws_total,
        stat.vorp_total = $vorp_total,
        stat.games_played = $games_played  // Retain games played without "total" as it isn't cumulative
    """
    tx.run(query, 
           player=player_name, 
           season=stats_data["Season"], 
           pts_total=stats_data["PTS_total"], 
           ast_total=stats_data["AST_total"], 
           trb_total=stats_data["TRB_total"], 
           stl_total=stats_data["STL_total"],
           blk_total=stats_data["BLK_total"],
           tov_total=stats_data["TOV_total"],
           pf_total=stats_data["PF_total"],
           ws_total=stats_data["WS_total"],
           ows_total=stats_data["OWS_total"],
           dws_total=stats_data["DWS_total"],
           vorp_total=stats_data["VORP_total"],
           games_played=stats_data["GP"])




def create_injury_node(tx, player_name, injury_data):
    if pd.isna(injury_data["Total_Days_Injured"]) or pd.isna(injury_data["Injury_Periods"]) or pd.isna(injury_data["Injury_Risk"]):
        return
    query = """
    MERGE (i:Injury {player: $player})
    ON CREATE SET i.total_days = $total_days,
                  i.injury_periods = $injury_periods,
                  i.risk = $risk,
                  i.injury_history = $injury_history
    """
    tx.run(query,
           player=player_name,
           total_days=injury_data["Total_Days_Injured"],
           injury_periods=injury_data["Injury_Periods"],
           risk=injury_data["Injury_Risk"],
           injury_history=injury_data.get("Injury_History"))


def create_relationships(tx, player_data):
    """Create relationships between Player, Team, Season, Contract, and other nodes in the database."""
    relationships = [
        {
            "query": """
                MATCH (p:Player {name: $player}), (t:Team {name: $team}), (s:Season {name: $season})
                MERGE (p)-[:HAS_PLAYED_FOR {season: $season}]->(t)
                MERGE (p)-[:PARTICIPATED_IN]->(s)
            """,
            "params": {"player": player_data["Player"], "team": player_data["Team"], "season": player_data["Season"]}
        },
        {
            "query": """
                MATCH (p:Player {name: $player}), (c:Contract {salary: $salary, season: $season})
                MERGE (p)-[:HAS_CONTRACT {season: $season}]->(c)
            """,
            "params": {"player": player_data["Player"], "salary": player_data["Salary"], "season": player_data["Season"]}
        },
        {
            "query": """
                MATCH (p:Player {name: $player}), (stat:Statistics {player: $player, season: $season})
                MERGE (p)-[:POSSESSES {season: $season}]->(stat)
            """,
            "params": {"player": player_data["Player"], "season": player_data["Season"]}
        },
        # Additional relationships for injury and current team
    ]
    for rel in relationships:
        tx.run(rel["query"], **rel["params"])
    print(f"Relationships created for Player: {player_data['Player']} for season: {player_data['Season']}.")


def calculate_and_set_trade_value(tx, player_name):
    # Placeholder for actual calculation logic
    trade_value = 0  # Replace with real calculation if needed
    query = """
    MATCH (p:Player {name: $player})
    SET p.trade_value = $trade_value
    """
    tx.run(query, player=player_name, trade_value=trade_value)


# Example query to check indexes
def check_indexes(session):
    result = session.run("CALL db.indexes")
    for record in result:
        print(record)


def clear_database(session):
    delete_query = "MATCH (n) DETACH DELETE n"
    session.run(delete_query)
    print("All nodes and relationships deleted from the database.")


# Function to clear all constraints and indexes
def clear_constraints_and_indexes(session):
    # Delete all constraints
    print("Clearing all constraints...")
    constraints_result = session.run("SHOW CONSTRAINTS")
    for record in constraints_result:
        constraint_name = record['name']
        session.run(f"DROP CONSTRAINT {constraint_name}")
        print(f"Constraint '{constraint_name}' has been deleted.")
    
    # Delete all indexes
    print("Clearing all indexes...")
    indexes_result = session.run("SHOW INDEXES")
    for record in indexes_result:
        index_name = record['name']
        session.run(f"DROP INDEX {index_name}")
        print(f"Index '{index_name}' has been deleted.")


# Function to create indexes if they don't already exist
def create_index_if_not_exists(session, index_query, index_name):
    try:
        check_query = f"SHOW INDEXES WHERE name = '{index_name}'"
        result = session.run(check_query)
        if result.single():
            print(f"Index '{index_name}' already exists.")
        else:
            session.run(index_query)
            print(f"Successfully created index: {index_name}")
    except Exception as e:
        print(f"Failed to create index: {index_name}. Error: {e}")


# Function to set up indexes
def setup_indexes(session):
    indexes = [
        {"query": "CREATE INDEX player_name_index IF NOT EXISTS FOR (p:Player) ON (p.name)", "name": "player_name_index"},
        {"query": "CREATE INDEX team_name_index IF NOT EXISTS FOR (t:Team) ON (t.name)", "name": "team_name_index"},
        {"query": "CREATE INDEX contract_season_index IF NOT EXISTS FOR (c:Contract) ON (c.season)", "name": "contract_season_index"}
    ]

    for index in indexes:
        create_index_if_not_exists(session, index["query"], index["name"])


# Function to insert data into Neo4j
def insert_enhanced_data(tx, player_data):
    create_player_node(tx, player_data)
    create_team_node(tx, player_data["Team"], player_data["TeamID"], player_data)
    create_season_node(tx, player_data["Season"])
    create_contract_node(tx, player_data)
    create_statistics_node(tx, player_data["Player"], player_data)
    create_injury_node(tx, player_data["Player"], player_data)
    create_relationships(tx, player_data)


# Main function to insert data
def main():
    load_dotenv('../../.env')
    data_file = '../../data/neo4j/processed/nba_player_data_cleaned.csv'

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
        print("An error occurred during Neo4j data ingestion:", e)


if __name__ == '__main__':
    main()
