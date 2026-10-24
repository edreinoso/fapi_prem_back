"""Rank participants by their total starting XI points for each round."""

import csv
from pathlib import Path

from .paths import DATABASE_DIR
from .config import load_config, get_entry_id_to_name
from .position_overview import export_position_overview

FIELDNAMES = ["rank", "participant", "totalPoints"]


def _read_round_total(positions_file: Path, round_number: int) -> int | None:
    """Return the `total` column of a round's row, or None if the round is absent."""
    with open(positions_file, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # The final summary row has gameweek "total" and never matches
            if row["gameweek"] == str(round_number):
                return int(row["total"])
    return None


def _get_round_total(
    entry_id: int,
    name: str,
    round_number: int,
    positions_dir: str,
    participants_dir: str,
    config_path: str,
) -> int | None:
    """Get a participant's total for a round from the positions directory.

    If the positions file is missing or does not contain the round yet, it is
    (re)generated from the participant picks with the position-overview logic.
    Returns None when the round is still unavailable (no picks exported).
    """
    positions_file = Path(positions_dir) / f"{name}_positions.csv"

    if positions_file.exists():
        total = _read_round_total(positions_file, round_number)
        if total is not None:
            return total

    try:
        export_position_overview(
            entry_id,
            output_file=str(positions_file),
            participants_dir=participants_dir,
            config_path=config_path,
        )
    except FileNotFoundError:
        return None

    return _read_round_total(positions_file, round_number)


def build_rank_per_round(
    round_number: int,
    entry_ids: list[int] | None = None,
    positions_dir: str = f"{DATABASE_DIR}/positions",
    participants_dir: str = f"{DATABASE_DIR}/participants",
    config_path: str = "config/participants.toml",
) -> tuple[list[dict], list[str]]:
    """Rank participants for a single round by their starting XI total.

    Ranking is descending by points; participants with equal points share the
    same rank (1, 2, 2, 4, ...).

    Args:
        round_number: Round (gameweek) to rank
        entry_ids: Participants to include (all participants in the config if None)
        positions_dir: Directory containing <name>_positions.csv files
        participants_dir: Directory containing participant picks
        config_path: Path to config file

    Returns:
        Tuple of (rows with keys rank, participant, totalPoints; names of
        participants skipped because they have no data for the round)
    """
    id_to_name = get_entry_id_to_name(load_config(config_path))
    if entry_ids is None:
        entry_ids = list(id_to_name)

    scores: list[tuple[str, int]] = []
    skipped: list[str] = []
    for entry_id in entry_ids:
        name = id_to_name.get(entry_id)
        if not name:
            raise ValueError(f"Participant ID {entry_id} not found in config")
        total = _get_round_total(
            entry_id, name, round_number, positions_dir, participants_dir, config_path
        )
        if total is None:
            skipped.append(name)
        else:
            scores.append((name, total))

    scores.sort(key=lambda item: (-item[1], item[0]))

    rows = []
    previous_points = None
    rank = 0
    for position, (name, points) in enumerate(scores, start=1):
        if points != previous_points:
            rank = position
            previous_points = points
        rows.append({"rank": rank, "participant": name, "totalPoints": points})

    return rows, skipped


def export_rank_per_round(
    round_number: int,
    entry_ids: list[int] | None = None,
    output_dir: str = f"{DATABASE_DIR}/rank",
    positions_dir: str = f"{DATABASE_DIR}/positions",
    participants_dir: str = f"{DATABASE_DIR}/participants",
    config_path: str = "config/participants.toml",
) -> tuple[Path, int, list[str]]:
    """Export the ranking of a round to <output_dir>/gw<round>.csv.

    Returns:
        Tuple of (output path, number of participants ranked, skipped names)
    """
    rows, skipped = build_rank_per_round(
        round_number, entry_ids, positions_dir, participants_dir, config_path
    )
    if not rows:
        raise FileNotFoundError(f"No participant data found for round {round_number}")

    output_path = Path(output_dir) / f"gw{round_number}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return output_path, len(rows), skipped
