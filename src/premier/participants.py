import csv
from pathlib import Path

import requests

from .paths import DATABASE_DIR
from .fpl_common import (
    BASE_URL,
    POSITION_ORDER,
    STAT_FIELDS,
    build_players_by_id,
    build_positions,
    fetch_bootstrap,
)


def fetch_live_players(gw: int) -> dict:
    """Fetch gameweek-specific live stats: player id -> live player dict."""
    live_data = requests.get(f"{BASE_URL}/event/{gw}/live/").json()
    return {player["id"]: player for player in live_data["elements"]}


HEADER = ["playerName", "totalPoints", "position", "multiplier", "isCaptain", "isBenched"]


def write_to_csv(
    rows: list,
    entry_id: int,
    gw: int,
    output_dir: str,
    participant_name: str = None,
) -> Path:
    """Write rows to output_dir/participant_name/gw.csv and return the path.
    
    Args:
        rows: Player data rows
        entry_id: FPL entry ID (used in fallback if no name provided)
        gw: Gameweek number
        output_dir: Base output directory
        participant_name: Participant name for directory structure
        
    Returns:
        Path to the written CSV file
    """
    # Use participant name if provided, otherwise fall back to entry_id
    dir_name = participant_name or str(entry_id)
    db_dir = Path(output_dir) / dir_name
    db_dir.mkdir(parents=True, exist_ok=True)
    output_filename = db_dir / f"{gw}.csv"

    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER + STAT_FIELDS)
        writer.writerows(rows)

    return output_filename


def export_picks(
    entry_id: int,
    gw: int,
    output_dir: str = f"{DATABASE_DIR}/participants",
    participant_name: str = None,
) -> int:
    """Fetch picks for a given FPL entry and gameweek and export to CSV.
    
    Args:
        entry_id: FPL entry ID
        gw: Gameweek number
        output_dir: Base output directory (default: ../database/participants)
        participant_name: Optional participant name for directory structure
        
    Returns:
        Number of picks exported
    """
    bootstrap = fetch_bootstrap()
    players = build_players_by_id(bootstrap)
    positions = build_positions(bootstrap)
    live_players = fetch_live_players(gw)

    picks = requests.get(
        f"{BASE_URL}/entry/{entry_id}/event/{gw}/picks/"
    ).json()

    rows = []

    for pick in picks["picks"]:
        player = players[pick["element"]]
        live_player = live_players[pick["element"]]

        rows.append(
            [
                player["web_name"],
                live_player["stats"]["total_points"],
                positions[player["element_type"]],
                pick["multiplier"],
                pick["is_captain"],
                pick["position"] > 11,
            ]
            + [player.get(field) for field in STAT_FIELDS]
        )

    # Starting XI first, then GK/DEF/MID/FWD, then highest GW points
    rows.sort(key=lambda row: (row[5], POSITION_ORDER.get(row[2], 99), -row[1]))

    write_to_csv(rows, entry_id, gw, output_dir, participant_name)

    return len(rows)


def export_picks_range(
    entry_id: int,
    gw_start: int = None,
    gw_end: int = None,
    output_dir: str = f"{DATABASE_DIR}/participants",
    participant_name: str = None,
) -> int:
    """Export picks for a range of gameweeks.
    
    Args:
        entry_id: FPL entry ID
        gw_start: Starting gameweek (None uses code default of 1)
        gw_end: Ending gameweek inclusive (None uses code default of 5)
        output_dir: Base output directory
        participant_name: Optional participant name for directory structure
        
    Returns:
        Total number of picks exported across all gameweeks
    """
    # Use defaults if not provided
    if gw_start is None:
        gw_start = 1
    if gw_end is None:
        gw_end = 5
    
    dir_name = participant_name or entry_id
    total_picks = 0
    for gw in range(gw_start, gw_end + 1):
        count = export_picks(entry_id, gw, output_dir, participant_name)
        print(f"  Wrote {count} picks to {output_dir}/{dir_name}/{gw}.csv")
        total_picks += count
    
    return total_picks


def main():
    """CLI entry point for exporting picks."""
    ENTRY_ID = 8388589
    GW_START = 1
    GW_END = 5  # inclusive

    total = export_picks_range(ENTRY_ID, GW_START, GW_END)
    print(f"Total picks exported: {total}")


if __name__ == "__main__":
    main()
