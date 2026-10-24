"""Find players available (not selected by any league participant)."""

import csv
from pathlib import Path

import requests

from .paths import DATABASE_DIR
from .fpl_common import BASE_URL, build_players_by_id, fetch_bootstrap


def get_league_players(league_file: str) -> set[str]:
    """Get set of player names selected in the league.
    
    Args:
        league_file: Path to league analysis CSV
        
    Returns:
        Set of player names
    """
    league_players = set()
    
    with open(league_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            league_players.add(row["playerName"])
    
    return league_players


def get_all_players(players_file: str) -> list[dict]:
    """Get all players from players CSV.
    
    Args:
        players_file: Path to all players CSV
        
    Returns:
        List of player dicts
    """
    all_players = []
    
    with open(players_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_players.append(row)
    
    return all_players


def fetch_live_players(gw: int) -> dict:
    """Fetch gameweek-specific live stats: player id -> live player dict."""
    live_data = requests.get(f"{BASE_URL}/event/{gw}/live/").json()
    return {player["id"]: player for player in live_data["elements"]}


def find_available_players(league_file: str, players_file: str, gameweek: int) -> list[dict]:
    """Find players NOT selected by any league participant.
    
    Args:
        league_file: Path to league analysis CSV
        players_file: Path to all players CSV
        gameweek: Gameweek number (for fetching live stats)
        
    Returns:
        List of dicts with playerName, playerTotalPoints, playerPointGw, position, team
        Sorted by playerPointGw descending
    """
    # Get league players
    league_players = get_league_players(league_file)
    
    # Get all players and filter
    all_players = get_all_players(players_file)
    
    # Build player lookup by name from bootstrap
    bootstrap = fetch_bootstrap()
    players_by_id = build_players_by_id(bootstrap)
    
    # Fetch live player data for gameweek
    live_players = fetch_live_players(gameweek)
    
    # Create name -> id mapping
    name_to_id = {}
    for player_id, player in players_by_id.items():
        name_to_id[player["web_name"]] = player_id
    
    # Filter: keep only players NOT in league
    available = []
    for player in all_players:
        if player["playerName"] not in league_players:
            # Get gameweek points from live data if available
            player_id = name_to_id.get(player["playerName"])
            player_gw_points = 0
            if player_id and player_id in live_players:
                player_gw_points = live_players[player_id]["stats"]["total_points"]
            
            available.append({
                "playerName": player["playerName"],
                "playerTotalPoints": int(player["totalPoints"]),
                "playerPointGw": player_gw_points,
                "position": player["position"],
                "team": player["team"],
            })
    
    # Sort by playerPointGw descending
    available.sort(key=lambda x: x["playerPointGw"], reverse=True)
    
    return available


def export_available_players(
    gameweek: int,
    league_file: str = None,
    players_file: str = f"{DATABASE_DIR}/players.csv",
    output_file: str = None,
) -> int:
    """Export available players to CSV.
    
    Args:
        gameweek: Gameweek number
        league_file: Path to league analysis CSV (auto-generated if None)
        players_file: Path to all players CSV
        output_file: Output CSV file path (auto-generated if None)
        
    Returns:
        Number of available players
    """
    # Auto-generate league file if not provided
    if league_file is None:
        league_file = f"{DATABASE_DIR}/league/league_gw_{gameweek}.csv"
    
    # Check files exist
    if not Path(league_file).exists():
        raise FileNotFoundError(f"League file not found: {league_file}")
    if not Path(players_file).exists():
        raise FileNotFoundError(f"Players file not found: {players_file}")
    
    # Auto-generate output file if not provided
    if output_file is None:
        output_file = f"{DATABASE_DIR}/available/available_gw_{gameweek}.csv"
    
    # Create output directory
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Find available players
    available = find_available_players(league_file, players_file, gameweek)
    
    # Write to CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["playerName", "playerTotalPoints", "playerPointGw", "position", "team"],
        )
        writer.writeheader()
        writer.writerows(available)
    
    return len(available)


def main():
    """CLI entry point for available players."""
    gameweek = 1
    count = export_available_players(gameweek)
    print(f"Wrote {count} available players to {DATABASE_DIR}/available/available_gw_{gameweek}.csv")


if __name__ == "__main__":
    main()
