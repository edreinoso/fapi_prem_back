"""Compare a participant's picks with league-wide player statistics."""

import csv
import math
from pathlib import Path
from collections import Counter

from .paths import DATABASE_DIR
from .config import load_config, get_entry_id_to_name, get_participants
from .fpl_common import POSITION_ORDER


def calculate_selected_percentage(player_name: str, league_data: list[dict]) -> float:
    """Calculate the percentage of league participants who selected a player.
    
    Args:
        player_name: Name of the player
        league_data: List of dicts from league analysis CSV
        
    Returns:
        Percentage (0-100) or 0 if player not in league data
    """
    for row in league_data:
        if row["playerName"] == player_name:
            # Count how many names are in the participantNames field
            names = row["participantNames"].split(";")
            return len(names) * 10.0  # 10% per participant (assuming 10 total)
    return 0.0


def compare_participant_to_league(
    entry_id: int,
    gameweek: int,
    participants_dir: str = f"{DATABASE_DIR}/participants",
    league_dir: str = f"{DATABASE_DIR}/league",
    config_path: str = "config/participants.toml",
) -> list[dict]:
    """Compare a participant's picks with league statistics.
    
    Args:
        entry_id: FPL entry ID of the participant
        gameweek: Gameweek number to compare
        participants_dir: Directory containing participant CSVs
        league_dir: Directory containing league analysis CSVs
        config_path: Path to config file
        
    Returns:
        List of dicts with player comparison data, sorted as specified
        Note: participantNames excludes the evaluated participant
    """
    config = load_config(config_path)
    id_to_name = get_entry_id_to_name(config)
    total_participants = len(get_participants(config))
    
    participant_name = id_to_name.get(entry_id)
    if not participant_name:
        raise ValueError(f"Participant ID {entry_id} not found in config")
    
    # Load league data
    league_file = Path(league_dir) / f"league_gw_{gameweek}.csv"
    if not league_file.exists():
        raise FileNotFoundError(f"League file not found: {league_file}")
    
    league_data = []
    with open(league_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        league_data = list(reader)
    
    # Load participant's picks
    participant_dir = Path(participants_dir) / participant_name
    picks_file = participant_dir / f"{gameweek}.csv"
    if not picks_file.exists():
        raise FileNotFoundError(f"Picks file not found: {picks_file}")
    
    result = []
    with open(picks_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            player_name = row["playerName"]
            points = int(row["totalPoints"])
            position = row["position"]
            is_benched = row["isBenched"].lower() == "true"
            is_captain = row["isCaptain"].lower() == "true"
            
            # Find this player in league data to get their selection percentage
            selected_percentage = 0
            league_participant_names = ""
            for league_row in league_data:
                if league_row["playerName"] == player_name:
                    league_participant_names = league_row["participantNames"]
                    # Remove the evaluated participant from the list
                    names = [n.strip() for n in league_participant_names.split(";")]
                    other_names = [n for n in names if n != participant_name]
                    league_participant_names = ";".join(other_names)
                    # Calculate percentage: number of OTHER participants who selected / (total - 1)
                    selected_percentage = math.ceil((len(other_names) / (total_participants - 1)) * 100) if total_participants > 1 else 0
                    break
            
            result.append({
                "playerName": player_name,
                "playerPointGw": points,
                "position": position,
                "isCaptain": is_captain,
                "isBenched": is_benched,
                "selectedPercentage": selected_percentage,
                "participantNames": league_participant_names,
                "_position_order": POSITION_ORDER.get(position, 99),  # For sorting
            })
    
    # Sort by: isBenched (True first) > position order > points descending
    result.sort(
        key=lambda x: (
            x["isBenched"],  # True (benched) comes first
            x["_position_order"],  # Then by position order
            -x["playerPointGw"],  # Then by points descending
        )
    )
    
    # Remove internal sorting field
    for row in result:
        del row["_position_order"]
    
    return result


def export_participant_comparison(
    entry_id: int,
    gameweek: int,
    output_file: str = None,
    participants_dir: str = f"{DATABASE_DIR}/participants",
    league_dir: str = f"{DATABASE_DIR}/league",
    config_path: str = "config/participants.toml",
) -> int:
    """Export participant comparison to CSV.
    
    Args:
        entry_id: FPL entry ID of the participant
        gameweek: Gameweek number to compare
        output_file: Output CSV file path (auto-generated if None)
        participants_dir: Directory containing participant CSVs
        league_dir: Directory containing league analysis CSVs
        config_path: Path to config file
        
    Returns:
        Number of players in comparison
    """
    config = load_config(config_path)
    id_to_name = get_entry_id_to_name(config)
    
    if output_file is None:
        participant_name = id_to_name.get(entry_id)
        output_file = f"{DATABASE_DIR}/comparisons/{participant_name}_gw_{gameweek}.csv"
    
    # Create output directory
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get comparison data
    comparison_data = compare_participant_to_league(
        entry_id, gameweek, participants_dir, league_dir, config_path
    )
    
    # Write to CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["playerName", "playerPointGw", "position", "isCaptain", "isBenched", "selectedPercentage", "participantNames"],
        )
        writer.writeheader()
        writer.writerows(comparison_data)
    
    return len(comparison_data)


def main():
    """CLI entry point for participant comparison."""
    entry_id = 7571821  # Bryan
    gameweek = 1
    count = export_participant_comparison(entry_id, gameweek)
    
    config = load_config("config/participants.toml")
    id_to_name = get_entry_id_to_name(config)
    participant_name = id_to_name.get(entry_id)
    
    print(f"Wrote {count} players to {DATABASE_DIR}/comparisons/{participant_name}_gw_{gameweek}.csv")


if __name__ == "__main__":
    main()
