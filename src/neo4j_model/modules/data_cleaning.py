

import pandas as pd
import os
from dotenv import load_dotenv

def load_data(file_path):
    """Loads data from the specified CSV file path."""
    dataframe = pd.read_csv(file_path)
    return dataframe

def initial_data_check(dataframe, debug=False):
    """Performs initial data checks, including missing values, data types, and unique counts."""
    if debug:
        print("Initial data shape:", dataframe.shape)
        
        # Check for missing values
        missing_values_summary = dataframe.isnull().sum()
        print("Missing Values Summary:\n", missing_values_summary[missing_values_summary > 0])
        
        # Data types of each column
        print("Data Types:\n", dataframe.dtypes)
        
        # Count unique values in key columns
        unique_counts = dataframe.nunique()
        print("Unique Values in Key Columns:\n", unique_counts[['Player', 'Season', 'Team', 'Salary']])
        
        # Check if key columns have unexpected unique values
        print(f"Unique Players: {dataframe['Player'].nunique()}")
        print(f"Unique Seasons: {dataframe['Season'].nunique()}")
        print(f"Unique Teams: {dataframe['Team'].nunique()}")
        print(f"Unique Salary values: {dataframe['Salary'].nunique()}")
        
def clean_data(dataframe, debug=False):
    """Cleans and prepares data for Neo4j ingestion, displaying nulls before and after cleaning."""
    if debug:
        print("Cleaning data...")
    
    # Step 1: Display total nulls before any cleaning
    total_nulls_before = dataframe.isnull().sum().sum()
    if debug:
        print("Total null values before cleaning:", total_nulls_before)
        print("Null values by column before cleaning:\n", dataframe.isnull().sum())

    # Remove '2nd Apron' column if it exists
    if '2nd Apron' in dataframe.columns:
        dataframe = dataframe.drop(columns=['2nd Apron'])
        if debug:
            print("Dropped '2nd Apron' column.")

    # Fill missing values in 'Injury_Periods' with 'Not_injured'
    dataframe['Injury_Periods'] = dataframe['Injury_Periods'].fillna("Not_injured")
    if debug:
        print("Filled missing 'Injury_Periods' with 'Not_injured'.")

    # Step 2: Drop rows with any remaining missing values
    dataframe_cleaned = dataframe.dropna()
    
    # Step 3: Display total nulls after cleaning
    total_nulls_after = dataframe_cleaned.isnull().sum().sum()
    if debug:
        print("Total null values after cleaning:", total_nulls_after)
        print("Null values by column after cleaning:\n", dataframe_cleaned.isnull().sum())
        print("Data shape after dropping remaining NaNs:", dataframe_cleaned.shape)
    
    return dataframe_cleaned


def check_for_duplicates(dataframe, debug=False):
    """Checks and logs duplicate entries in the dataframe."""
    duplicates = dataframe.duplicated(subset=["Player", "Season", "Salary"])
    num_duplicates = duplicates.sum()
    if debug:
        print("Number of duplicate rows:", num_duplicates)
    if num_duplicates > 0:
        print("Duplicate rows based on [Player, Season, Salary]:\n", dataframe[duplicates])

def map_team_ids(dataframe, debug=False):
    """Maps team abbreviations to TeamID."""
    team_id_mapping = {
        "ATL": 1610612737, "BOS": 1610612738, "BKN": 1610612751, "CHA": 1610612766,
        "CHI": 1610612741, "CLE": 1610612739, "DAL": 1610612742, "DEN": 1610612743,
        "DET": 1610612765, "GSW": 1610612744, "HOU": 1610612745, "IND": 1610612754,
        "LAC": 1610612746, "LAL": 1610612747, "MEM": 1610612763, "MIA": 1610612748,
        "MIL": 1610612749, "MIN": 1610612750, "NOP": 1610612740, "NYK": 1610612752,
        "OKC": 1610612760, "ORL": 1610612753, "PHI": 1610612755, "PHX": 1610612756,
        "POR": 1610612757, "SAC": 1610612758, "SAS": 1610612759, "TOR": 1610612761,
        "UTA": 1610612762, "WAS": 1610612764
    }
    dataframe['TeamID'] = dataframe['Team'].map(team_id_mapping)
    if debug:
        unmapped_teams = dataframe['TeamID'].isnull().sum()
        if unmapped_teams > 0:
            print(f"{unmapped_teams} teams were not mapped to TeamIDs. Check team abbreviations.")
    return dataframe

def add_suffixes_to_columns(dataframe, debug=False):
    """Renames statistical columns to include '_total' suffix where needed."""
    suffix_mapping = {
        'PTS': 'PTS_total', 'AST': 'AST_total', 'TRB': 'TRB_total', 'STL': 'STL_total',
        'BLK': 'BLK_total', 'TOV': 'TOV_total', 'PF': 'PF_total', 'WS': 'WS_total',
        'OWS': 'OWS_total', 'DWS': 'DWS_total', 'VORP': 'VORP_total'
    }
    dataframe = dataframe.rename(columns=suffix_mapping)
    if debug:
        print("Applied suffixes to cumulative columns.")
    return dataframe

def final_data_check(dataframe, debug=False):
    """Final data checks before saving for Neo4j ingestion."""
    if debug:
        # Verify all necessary columns exist
        required_columns = ['Player', 'Season', 'TeamID', 'Salary'] + list(dataframe.filter(regex='_total').columns)
        missing_columns = [col for col in required_columns if col not in dataframe.columns]
        if missing_columns:
            print(f"Missing expected columns: {missing_columns}")
        
        # Re-check for missing values
        null_summary = dataframe.isnull().sum()
        if null_summary.any():
            print("Columns with remaining null values:\n", null_summary[null_summary > 0])
        
        # Check if data types are compatible for Neo4j
        print("Final Data Types:\n", dataframe.dtypes)

        # Preview the first few rows of the final dataframe
        print("Preview of cleaned data:\n", dataframe.head())

def check_data_statistics(dataframe, debug=False):
    """Generates descriptive statistics and checks for unique counts to spot anomalies."""
    if debug:
        print("Descriptive Statistics of the Dataset:\n", dataframe.describe(include='all'))
        print("\nUnique Value Counts for Key Columns:")
        unique_counts = dataframe.nunique()
        print(unique_counts[['Player', 'Season', 'Team', 'Salary']])
        print(f"\nUnique Players: {dataframe['Player'].nunique()}")
        print(f"Unique Seasons: {dataframe['Season'].nunique()}")
        print(f"Unique Teams: {dataframe['Team'].nunique()}")
        print(f"Unique Contracts (based on Salary): {dataframe['Salary'].nunique()}")

def identify_conflicting_contracts(dataframe, debug=False):
    """Identifies conflicting contracts and displays detailed entries for conflicts."""
    conflicting_contracts = dataframe.groupby(['Player', 'Season', 'Salary']).size().reset_index(name='count')
    conflicting_contracts = conflicting_contracts[conflicting_contracts['count'] > 1]
    
    if not conflicting_contracts.empty:
        print("Potential Conflicting Contracts Found:")
        print(conflicting_contracts)
        for _, row in conflicting_contracts.iterrows():
            player, season, salary = row['Player'], row['Season'], row['Salary']
            print(f"\nDetails of Conflicting Contracts for Player: {player}, Season: {season}, Salary: {salary}")
            print(dataframe[(dataframe['Player'] == player) & 
                            (dataframe['Season'] == season) & 
                            (dataframe['Salary'] == salary)])

def data_initial_summary(dataframe, debug=False):
    """Performs initial checks and calls the detailed statistics and conflict identification functions."""
    initial_data_check(dataframe, debug)
    check_data_statistics(dataframe, debug)
    identify_conflicting_contracts(dataframe, debug)


def main(debug=True):
    load_dotenv('/workspaces/custom_ollama_docker/.env')
    data_file = os.getenv('DATA_FILE', '/workspaces/custom_ollama_docker/data/neo4j/raw/nba_player_data_final_inflated.csv')
    output_file = os.getenv('CLEANED_DATA_FILE', '/workspaces/custom_ollama_docker/data/neo4j/processed/nba_player_data_cleaned.csv')
    
    try:
        dataframe = load_data(data_file)
        print(f"Loaded data with shape: {dataframe.shape}")
        
        # Step 2: Initial checks, data statistics, and conflict identification
        data_initial_summary(dataframe, debug)
        
        # Clean data, check duplicates, map IDs, add suffixes, and run final checks
        dataframe_cleaned = clean_data(dataframe, debug)
        check_for_duplicates(dataframe_cleaned, debug)
        dataframe_mapped = map_team_ids(dataframe_cleaned, debug)
        dataframe_final = add_suffixes_to_columns(dataframe_mapped, debug)
        final_data_check(dataframe_final, debug)
        
        dataframe_final.to_csv(output_file, index=False)
        print(f"Preprocessed data saved to {output_file}")
    
    except Exception as e:
        print("An error occurred during data preprocessing:", e)


if __name__ == "__main__":
    main(debug=True)
