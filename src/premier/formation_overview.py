"""Per-gameweek formation (e.g. 4-3-3) and starting XI points of a participant."""

import csv
from pathlib import Path

from .paths import DATABASE_DIR
from .config import load_config, get_entry_id_to_name

FIELDNAMES = ["round", "formation", "totalPoints"]

# Outfield positions as stored in participant CSVs, in formation order.
# The goalkeeper is always exactly one player and is not part of the formation.
FORMATION_POSITIONS = ["Defender", "Midfielder", "Forward"]


def build_formation_overview(
    entry_id: int,
    participants_dir: str = f"{DATABASE_DIR}/participants",
    config_path: str = "config/participants.toml",
) -> list[dict]:
    """Build the formation and starting XI points for every gameweek of a participant.

    The formation is the number of starting XI players (isBenched is false) per
    outfield position, written as defenders-midfielders-forwards (e.g. "4-3-3").
    Points are totalPoints * multiplier summed over the starting XI, so the
    captain's points are doubled (consistent with position-overview and the FPL
    app's gameweek total).

    Args:
        entry_id: FPL entry ID of the participant
        participants_dir: Directory containing participant CSVs
        config_path: Path to config file

    Returns:
        List of dicts (one per gameweek, ordered by gameweek) with keys
        round, formation, totalPoints
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
        counts = {position: 0 for position in FORMATION_POSITIONS}
        total_points = 0
        with open(picks_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["isBenched"].lower() == "true":
                    continue
                total_points += int(row["totalPoints"]) * int(row["multiplier"])
                if row["position"] in counts:
                    counts[row["position"]] += 1
        result.append({
            "round": int(picks_file.stem),
            "formation": "-".join(str(counts[p]) for p in FORMATION_POSITIONS),
            "totalPoints": total_points,
        })

    return result


def export_formation_overview(
    entry_id: int,
    output_file: str = None,
    participants_dir: str = f"{DATABASE_DIR}/participants",
    config_path: str = "config/participants.toml",
) -> int:
    """Export a participant's per-gameweek formation overview to CSV.

    Args:
        entry_id: FPL entry ID of the participant
        output_file: Output CSV file path (auto-generated if None)
        participants_dir: Directory containing participant CSVs
        config_path: Path to config file

    Returns:
        Number of gameweeks written
    """
    data = build_formation_overview(entry_id, participants_dir, config_path)

    if output_file is None:
        participant_name = get_entry_id_to_name(load_config(config_path)).get(entry_id)
        output_file = f"{DATABASE_DIR}/formations/{participant_name}_formations.csv"

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(data)

    return len(data)
