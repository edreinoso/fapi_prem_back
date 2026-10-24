"""League-wide analysis of FPL participants."""

import csv
from collections import defaultdict
from pathlib import Path

from .paths import DATABASE_DIR
from .config import load_config, get_participants, get_entry_id_to_name

FIELDNAMES = [
    "playerName",
    "totalPoints",
    "position",
    "team",
    "currentPrice",
    "participantNames",
    "participantCount",
]


def load_team_lookup(players_file: str) -> dict[tuple[str, str], str]:
    """Build (playerName, position) -> team from the all-players CSV.
    
    If several players share the same name and position, their teams are
    joined with "/" so the ambiguity stays visible.
    Returns an empty lookup if the file does not exist.
    """
    path = Path(players_file)
    if not path.exists():
        print(f"  ⚠ Players file not found: {players_file} (team column will be empty)")
        return {}
    
    teams = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["playerName"], row["position"])
            if row["team"] not in teams[key]:
                teams[key].append(row["team"])
    
    return {key: "/".join(value) for key, value in teams.items()}


def load_price_lookup(players_file: str) -> dict[tuple[str, str], str]:
    """Build (playerName, position) -> currentPrice from the all-players CSV.

    If several players share the same name and position but have different
    prices, the price is left out (empty) rather than guessing which one is meant.
    Returns an empty lookup if the file or column does not exist; the missing-file
    warning is already printed by load_team_lookup.
    """
    path = Path(players_file)
    if not path.exists():
        return {}

    prices = defaultdict(set)
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("currentPrice"):
                prices[(row["playerName"], row["position"])].add(row["currentPrice"])

    return {key: next(iter(value)) for key, value in prices.items() if len(value) == 1}


def analyze_gameweek(
    gameweek: int,
    participants_dir: str = f"{DATABASE_DIR}/participants",
    config_path: str = "config/participants.toml",
    players_file: str = f"{DATABASE_DIR}/players.csv",
) -> list[dict]:
    """Analyze all participants' picks for a given gameweek.
    
    Aggregates player data across all participants, tracking:
    - Which participants selected each player
    - How many participants selected each player
    - The gameweek points for that player
    
    Args:
        gameweek: Gameweek number to analyze
        participants_dir: Base directory containing participant CSVs
        config_path: Path to participants config file
        players_file: Path to all players CSV (used to look up each player's team and price)
        
           List of dicts with keys: playerName, totalPoints, position, team,
        currentPrice, participantNames, participantCount
        Sorted by totalPoints descending
    """
    team_lookup = load_team_lookup(players_file)
    price_lookup = load_price_lookup(players_file)
    config = load_config(config_path)
    participants = get_participants(config)
    id_to_name = get_entry_id_to_name(config)
    
    # Aggregate player data: playerName -> {points, set of participant names}
    player_data = defaultdict(
        lambda: {"points": 0, "position": "", "participant_names": set()}
    )
    
    for entry_id in participants.keys():
        # Try participant name directory first, then fall back to ID
        participant_name = id_to_name.get(entry_id)
        dir_name = participant_name or str(entry_id)
        picks_file = Path(participants_dir) / dir_name / f"{gameweek}.csv"
        
        if not picks_file.exists():
            print(f"  ⚠ Skipped {participant_name or entry_id}: picks file not found")
            continue
        
        # Read this participant's picks
        with open(picks_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                player_name = row["playerName"]
                points = int(row["totalPoints"])
                
                # Track points (use highest if player appears multiple times, shouldn't happen)
                if points > player_data[player_name]["points"]:
                    player_data[player_name]["points"] = points
                player_data[player_name]["position"] = row["position"]
                
                # Track which participant selected this player (use name if available)
                player_data[player_name]["participant_names"].add(
                    participant_name or str(entry_id)
                )
    
    # Convert to list and sort by points descending
    result = [
        {
            "playerName": name,
            "totalPoints": data["points"],
            "position": data["position"],
            "team": team_lookup.get((name, data["position"]), ""),
            "currentPrice": price_lookup.get((name, data["position"]), ""),
            "participantNames": ";".join(sorted(data["participant_names"])),
            "participantCount": len(data["participant_names"]),
        }
        for name, data in player_data.items()
    ]
    
    result.sort(key=lambda x: x["totalPoints"], reverse=True)
    
    return result


def export_league_players(
    gameweek: int,
    output_file: str = None,
    participants_dir: str = f"{DATABASE_DIR}/participants",
    config_path: str = "config/participants.toml",
    players_file: str = f"{DATABASE_DIR}/players.csv",
) -> int:
    """Export league-wide player analysis to CSV.
    
    Args:
        gameweek: Gameweek number to analyze
        output_file: Output CSV file path (auto-generated if None)
        participants_dir: Base directory containing participant CSVs
        config_path: Path to participants config file
        players_file: Path to all players CSV (used to look up each player's team)
        
    Returns:
        Number of unique players exported
    """
    if output_file is None:
        output_file = f"{DATABASE_DIR}/league/league_gw_{gameweek}.csv"
    
    # Create output directory
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Analyze gameweek
    players = analyze_gameweek(gameweek, participants_dir, config_path, players_file)
    
    # Write to CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(players)
    
    return len(players)


def main():
    """CLI entry point for league analysis."""
    # Example: analyze gameweek 1
    GAMEWEEK = 1
    count = export_league_players(GAMEWEEK)
    print(f"Wrote {count} players to {DATABASE_DIR}/league/league_gw_{GAMEWEEK}.csv")


if __name__ == "__main__":
    main()
