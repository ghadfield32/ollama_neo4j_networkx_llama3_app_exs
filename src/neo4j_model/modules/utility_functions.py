
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

def load_env_variables():
    """Loads environment variables from .env file and returns as dictionary."""
    load_dotenv('../../.env')
    return {
        'NEO4J_URI': os.getenv("NEO4J_URI"),
        'NEO4J_USERNAME': os.getenv("NEO4J_USERNAME"),
        'NEO4J_PASSWORD': os.getenv("NEO4J_PASSWORD")
    }

def connect_to_neo4j():
    """Connects to the Neo4j database using credentials from environment variables."""
    env_vars = load_env_variables()
    uri = env_vars['NEO4J_URI']
    username = env_vars['NEO4J_USERNAME']
    password = env_vars['NEO4J_PASSWORD']
    
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        print("Connected to Neo4j successfully.")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        raise
    return driver

def main():
    """Main function to test Neo4j connection."""
    print("Testing Neo4j connection...")
    try:
        driver = connect_to_neo4j()
        driver.close()  # Close the connection after testing
        print("Neo4j connection test completed successfully.")
    except Exception as e:
        print("Neo4j connection test failed.")

if __name__ == "__main__":
    main()
