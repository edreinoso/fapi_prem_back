import csv
from pathlib import Path

from .paths import DATABASE_DIR
from .fpl_common import STAT_FIELDS, fetch_bootstrap, get_all_players


def export_players(output_file: str = f"{DATABASE_DIR}/players.csv") -> int:
    """Fetch all players from FPL API and export to CSV.
    
    Args:
        output_file: Output CSV file path (default: ../database/players.csv)
        
    Returns:
        Number of players exported
    """
    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    bootstrap = fetch_bootstrap()
    players = get_all_players(bootstrap)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write header with base fields plus stat fields
        writer.writerow(
            ["playerName", "totalPoints", "position", "team", "currentPrice"] + STAT_FIELDS
        )

        # Write player data rows
        for player in players:
            writer.writerow([
                player["playerName"],
                player["totalPoints"],
                player["position"],
                player["team"],
                player["currentPrice"],
            ] + [player.get(field) for field in STAT_FIELDS])

    return len(players)


def main():
    """CLI entry point for exporting players."""
    count = export_players()
    print(f"Wrote {count} players to players.csv")


if __name__ == "__main__":
    main()
