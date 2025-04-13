import builtins
import contextlib
import io
import math
from typing import Any

from langchain.chat_models import init_chat_model
from langgraph_codeact import create_codeact
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama

def eval_code(code: str, _locals: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    # Store original keys before execution
    original_keys = set(_locals.keys())
    try:
        with contextlib.redirect_stdout(io.StringIO()) as f:
            exec(code, builtins.__dict__, _locals)
        result = f.getvalue()
        if not result:
            result = "<code ran, no output printed to stdout>"
    except Exception as e:
        result = f"Error during execution: {repr(e)}"
    # Determine new variables created during execution
    new_keys = set(_locals.keys()) - original_keys
    new_vars = {key: _locals[key] for key in new_keys}
    return result, new_vars

# Sample math operation tools
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide one number by another."""
    return a / b

def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first."""
    return a - b

def sin(a: float) -> float:
    """Return the sine of a number (in radians)."""
    return math.sin(a)

def cos(a: float) -> float:
    """Return the cosine of a number (in radians)."""
    return math.cos(a)

def radians(a: float) -> float:
    """Convert degrees to radians."""
    return math.radians(a)

def exponentiation(a: float, b: float) -> float:
    """Raise a number to the power of another."""
    return a ** b

def sqrt(a: float) -> float:
    """Return the square root of a number."""
    return math.sqrt(a)

def ceil(a: float) -> float:
    """Round a number up to the nearest integer."""
    return math.ceil(a)

# List of tools available for code execution.
tools = [
    add,
    multiply,
    divide,
    subtract,
    sin,
    cos,
    radians,
    exponentiation,
    sqrt,
    ceil,
]

# Initialize the chat model using Ollama and deepseek.
model = ChatOllama(model="deepseek-r1:latest", temperature=0.7, max_tokens=512)

# Create the CodeAct agent.
code_act = create_codeact(model, tools, eval_code)

def create_code_act_agent():
    """
    Returns a compiled CodeAct agent with a MemorySaver checkpoint.
    """
    return code_act.compile(checkpointer=MemorySaver())


from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import asyncio

def get_recent_seasons(player_name: str, count: int = None) -> list:
    """
    Retrieve the most recent seasons for a given player by querying the NBA API.
    
    Args:
        player_name (str): The full name of the NBA player.
        count (int, optional): The number of most recent seasons to return.
            If None, returns all available seasons.
    
    Returns:
        list: A sorted list (ascending order) of season IDs. The most recent seasons
              are at the end of the list.
    """
    player_list = players.find_players_by_full_name(player_name)
    if not player_list:
        return []
    player_id = player_list[0]['id']
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = stats.get_data_frames()[0]
    seasons = df['SEASON_ID'].unique().tolist()
    seasons.sort()
    if count is not None and count < len(seasons):
        return seasons[-count:]
    return seasons

async def compute_avg_ppg_last_seasons(player_name: str, count: int = None) -> float:
    """
    Compute the average points per game (PPG) for a player over the last 'count' seasons.
    If count is None, all available seasons will be used.
    
    Args:
        player_name (str): The full name of the NBA player.
        count (int, optional): Number of recent seasons to consider.
    
    Returns:
        float: The computed average PPG.
    """
    seasons = get_recent_seasons(player_name, count)
    total_points = 0.0
    total_games = 0
    for season in seasons:
        logs = await nba_player_game_logs(player_name, season)
        lines = logs.splitlines()
        if len(lines) < 2:
            continue
        header = lines[0].split()
        try:
            pts_index = header.index("PTS")
        except ValueError:
            continue
        season_points = 0.0
        season_games = 0
        for line in lines[1:]:
            cols = line.split()
            if len(cols) <= pts_index:
                continue
            try:
                pts = float(cols[pts_index])
                season_points += pts
                season_games += 1
            except Exception:
                continue
        total_points += season_points
        total_games += season_games
    if total_games == 0:
        return 0.0
    return total_points / total_games

def compute_avg_ppg_last_seasons_sync(player_name: str, count: int = None) -> str:
    """
    Synchronous wrapper for computing average PPG over the last 'count' seasons.
    
    Args:
        player_name (str): The full name of the NBA player.
        count (int, optional): Number of recent seasons to consider.
    
    Returns:
        str: The average PPG formatted to two decimal places.
    """
    avg_ppg = asyncio.run(compute_avg_ppg_last_seasons(player_name, count))
    return f"{avg_ppg:.2f}"

# Append the new synchronous wrapper to the tools list.
tools.append(compute_avg_ppg_last_seasons_sync)
