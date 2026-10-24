#!/usr/bin/env bash
# Refresh all data for a gameweek.
# Usage: ./run.sh <gameweek>

if [[ $# -ne 1 || ! "$1" =~ ^[1-9][0-9]*$ ]]; then
    echo "Usage: $0 <gameweek>   (a positive integer, e.g. $0 7)" >&2
    exit 1
fi

GAMEWEEK="$1"

# Run from the repository root regardless of where the script is called from
cd "$(dirname "$0")" || exit 1

# Print a header, run the command, and report how long it took
run_step() {
    local title="$1"; shift
    echo
    echo "=== $title ==="
    local start=$SECONDS
    "$@" || exit 1
    echo "⏱  $title finished in $((SECONDS - start))s"
}

TOTAL_START=$SECONDS

# players.csv feeds the team and price columns and the available players, so refresh it first
run_step "players" uv run premier players
run_step "participants" uv run premier participants --config config/participants.toml --gameweek "$GAMEWEEK"
run_step "league-analysis" uv run premier league-analysis "$GAMEWEEK"
run_step "available-players" uv run premier available-players "$GAMEWEEK"
run_step "position-overview" uv run premier position-overview --all
run_step "rank-per-round" uv run premier rank-per-round "$GAMEWEEK"
run_step "formation-overview" uv run premier formation-overview --all

echo
echo "=== Total execution time: $((SECONDS - TOTAL_START))s ==="
