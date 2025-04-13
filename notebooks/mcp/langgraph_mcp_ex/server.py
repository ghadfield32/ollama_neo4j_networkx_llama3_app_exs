# server.py
from mcp.server.fastmcp import FastMCP
from langchain_experimental.utilities import PythonREPL
import io
import base64
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field
import asyncio
from nba_api.stats.endpoints import playercareerstats, playergamelog, teamyearbyyearstats
import pandas as pd
from nba_api.stats.static import players, teams

# Create an instance of FastMCP – this is crucial!
mcp = FastMCP("My MCP Server")

# Existing tool: nba_player_stats
@mcp.tool()
def nba_player_stats(player_name: str):
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        return f"No player found with name '{player_name}'."
    
    player_id = player_dict[0]['id']
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = stats.get_data_frames()[0]
    summary = df[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'REB', 'AST']].tail(5).to_string(index=False)
    return f"Career stats for {player_name} (last 5 seasons):\n{summary}"

# New Tool: search_nba_player
@mcp.tool()
def search_nba_player(query: str) -> str:
    from nba_api.stats.static import players
    results = players.find_players_by_full_name(query)
    if not results:
        return f"No NBA players found for query '{query}'."
    info = f"Found {len(results)} players for '{query}':\n"
    for p in results:
        info += f"ID: {p['id']} - Name: {p['full_name']} - Team: {p.get('teamName', 'N/A')}\n"
    return info

# New Tool: nba_player_game_logs
@mcp.tool()
async def nba_player_game_logs(player_name: str, season: str) -> str:
    from nba_api.stats.static import players
    from nba_api.stats.endpoints import playergamelog
    results = players.find_players_by_full_name(player_name)
    if not results:
        return f"No player found with name '{player_name}'."
    player_id = results[0]['id']
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = game_logs.get_data_frames()[0]
    summary = df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST']].to_string(index=False)
    return f"Game logs for {player_name} in {season}:\n{summary}"

# New Tool: nba_team_stats
@mcp.tool()
def nba_team_stats(team_abbreviation: str, season: str) -> str:
    from nba_api.stats.static import teams
    from nba_api.stats.endpoints import teamyearbyyearstats
    team_list = teams.find_teams_by_abbreviation(team_abbreviation)
    if not team_list:
        return f"No team found with abbreviation '{team_abbreviation}'."
    team_id = team_list[0]['id']
    stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
    df = stats.get_data_frames()[0]
    df_season = df[df['YEAR'] == season] if season in df['YEAR'].values else df
    summary = df_season.to_string(index=False)
    return f"Team stats for {team_abbreviation} in {season}:\n{summary}"

@mcp.tool()
def nba_player_stats_regularseason(player_name: str) -> str:
    """
    Retrieve the NBA player's career regular season totals.
    Uses the NBA API's PlayerCareerStats endpoint and returns only the Regular Season data.
    """
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        return f"No player found with name '{player_name}'."
    
    player_id = player_dict[0]['id']
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    try:
        df_reg = stats.get_data_frames()[0]
        summary = df_reg[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'REB', 'AST']].tail(5).to_string(index=False)
        return f"Regular Season Stats for {player_name} (last 5 seasons):\n{summary}"
    except Exception as e:
        return f"Error retrieving regular season stats for {player_name}: {str(e)}"

@mcp.tool()
def nba_player_stats_postseason(player_name: str) -> str:
    """
    Retrieve the NBA player's career postseason totals.
    Uses the NBA API's PlayerCareerStats endpoint and returns only the Postseason data.
    """
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        return f"No player found with name '{player_name}'."
    
    player_id = player_dict[0]['id']
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    try:
        # Assuming the postseason totals are in the second DataFrame (index 1)
        df_post = stats.get_data_frames()[1]
        if df_post.empty:
            return f"No postseason stats available for {player_name}."
        summary = df_post[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'REB', 'AST']].tail(5).to_string(index=False)
        return f"Postseason Stats for {player_name} (last 5 seasons):\n{summary}"
    except Exception as e:
        return f"Error retrieving postseason stats for {player_name}: {str(e)}"

@mcp.tool()
def nba_player_stats_career_totals(player_name: str) -> str:
    """
    Retrieve an aggregated summary of the NBA player's career totals (combining regular season data).
    This tool returns overall totals and per-game averages based on regular season data.
    """
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        return f"No player found with name '{player_name}'."
    
    player_id = player_dict[0]['id']
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    try:
        df_reg = stats.get_data_frames()[0]
        if df_reg.empty:
            return f"No regular season data available for {player_name}."
        
        totals = df_reg[['GP', 'PTS', 'REB', 'AST']].sum()
        averages = df_reg[['PTS', 'REB', 'AST']].mean()
        summary = (
            f"Career Totals for {player_name} (Regular Season):\n"
            f"Games Played: {totals['GP']}\n"
            f"Total Points: {totals['PTS']}\n"
            f"Total Rebounds: {totals['REB']}\n"
            f"Total Assists: {totals['AST']}\n\n"
            f"Average Points per Game: {averages['PTS']:.2f}\n"
            f"Average Rebounds per Game: {averages['REB']:.2f}\n"
            f"Average Assists per Game: {averages['AST']:.2f}"
        )
        return summary
    except Exception as e:
        return f"Error retrieving career totals for {player_name}: {str(e)}"
    

# Existing tools for other functions remain unchanged
repl = PythonREPL()


@mcp.tool()
def data_visualization(code: str):
    try:
        repl.run(code)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        return f"Error creating chart: {str(e)}"
        
@mcp.tool()
def nba_player_stats_for_season(player_name: str, season: str) -> str:
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        return f"No player found with name '{player_name}'."
    player_id = player_dict[0]['id']
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = stats.get_data_frames()[0]
    if season not in df['SEASON_ID'].values:
        return f"Data for season {season} is not available."
    df_season = df[df['SEASON_ID'] == season]
    summary = df_season[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'REB', 'AST']].to_string(index=False)
    return f"Stats for {player_name} in {season}:\n{summary}"

@mcp.tool()
def nba_player_avg_ppg_for_season(player_name: str, season: str) -> str:
    # Find the player by full name.
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        return f"No player found with name '{player_name}'."
    
    player_id = player_dict[0]['id']
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = stats.get_data_frames()[0]
    
    # Check if the season is present in the data.
    if season not in df['SEASON_ID'].values:
        return f"Data for season {season} is not available."
    
    # Filter the DataFrame to only include the requested season.
    df_season = df[df['SEASON_ID'] == season]
    
    # Calculate the average points per game.
    try:
        avg_ppg = df_season['PTS'].mean()
        return f"{avg_ppg:.2f}"
    except Exception as e:
        return f"Error computing average points for {player_name} in {season}: {str(e)}"

@mcp.tool()
def python_repl(code: str):
    return repl.run(code)

def get_tools(retriever_tool=None):
    base_tools = [
        python_repl, 
        data_visualization, 
        nba_player_stats, 
        search_nba_player, 
        nba_player_game_logs, 
        nba_team_stats,
        nba_player_stats_for_season,
        nba_player_avg_ppg_for_season
    ]
    if retriever_tool:
        base_tools.append(retriever_tool)
    return base_tools

if __name__ == "__main__":
    mcp.run(transport="sse")
