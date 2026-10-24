"""Overview of a participant's starting XI points aggregated by position."""

import csv
from pathlib import Path

from .paths import DATABASE_DIR
from .config import load_config, get_entry_id_to_name

# Position name (as stored in participant CSVs) -> output column
POSITION_COLUMNS = {
    "Goalkeeper": "goalkeepers",
    "Defender": "defenders",
    "Midfielder": "midfielders",
    "Forward": "attackers",
}

FIELDNAMES = ["gameweek", *POSITION_COLUMNS.values(), "total"]


def build_position_overview(
    entry_id: int,
    participants_dir: str = f"{DATABASE_DIR}/participants",
    config_path: str = "config/participants.toml",
) -> list[dict]:
    """Aggregate starting XI points per position for every gameweek of a participant.

    Benched players are excluded. Points are totalPoints * multiplier, so the
    captain's points are doubled (matching the FPL app's gameweek total).

    Args:
        entry_id: FPL entry ID of the participant
        participants_dir: Directory containing participant CSVs
        config_path: Path to config file

    Returns:
        List of dicts (one per gameweek, ordered by gameweek) with keys
        gameweek, goalkeepers, defenders, midfielders, attackers, total,
        followed by a final "total" row summing each column
    """
    config = load_config(config_path)
    participant_name = get_entry_id_to_name(config).get(entry_id)
    if not participant_name:
        raise ValueError(f"Participant ID {entry_id} not found in config")

    participant_dir = Path(participants_dir) / participant_name
    if not participant_dir.is_dir():
        raise FileNotFoundError(f"Participant directory not found: {participant_dir}")

    gameweek_files = sorted(
        (p for p in participant_dir.glob("*.csv") if p.stem.isdigit()),
        key=lambda p: int(p.stem),
    )
    if not gameweek_files:
        raise FileNotFoundError(f"No gameweek files found in: {participant_dir}")

    result = []
    for picks_file in gameweek_files:
        row_totals = {column: 0 for column in POSITION_COLUMNS.values()}
        with open(picks_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["isBenched"].lower() == "true":
                    continue
                column = POSITION_COLUMNS.get(row["position"])
                if column:
                    # multiplier accounts for captain (x2) / triple captain (x3)
                    row_totals[column] += int(row["totalPoints"]) * int(row["multiplier"])
        result.append({
            "gameweek": int(picks_file.stem),
            **row_totals,
            "total": sum(row_totals.values()),
        })

    # Final row: sum of each column across all gameweeks
    result.append({
        "gameweek": "total",
        **{key: sum(r[key] for r in result) for key in [*POSITION_COLUMNS.values(), "total"]},
    })

    return result


def export_position_overview(
    entry_id: int,
    output_file: str = None,
    participants_dir: str = f"{DATABASE_DIR}/participants",
    config_path: str = "config/participants.toml",
) -> int:
    """Export a participant's per-gameweek position overview to CSV.

    Args:
        entry_id: FPL entry ID of the participant
        output_file: Output CSV file path (auto-generated if None)
        participants_dir: Directory containing participant CSVs
        config_path: Path to config file

    Returns:
        Number of gameweeks written
    """
    data = build_position_overview(entry_id, participants_dir, config_path)

    if output_file is None:
        participant_name = get_entry_id_to_name(load_config(config_path)).get(entry_id)
        output_file = f"{DATABASE_DIR}/positions/{participant_name}_positions.csv"

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(data)

    return len(data) - 1  # exclude the totals row
