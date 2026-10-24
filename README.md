# fapi_prem_back

## Project Overview
Backend for the Premier Fantasy League tools. A set of Python scripts fetch FPL data and arrange it into CSV files. The Streamlit dashboard that visualizes these files lives in the frontend repository (`../front`).

## Database Location
The CSV files are not part of this repository. They live in a separate directory shared with the frontend:

```
premier/
├── backend/   <- this repository
├── front/     <- Streamlit dashboard
└── database/  <- generated CSV files (not tracked by git)
```

By default the scripts read and write `../database`. To use another location, set `PREMIER_DATABASE_DIR`:

```bash
PREMIER_DATABASE_DIR=/path/to/database uv run premier league-analysis 5
```

Run the commands from the `backend/` directory so the default relative path (and `config/participants.toml`) resolve correctly.

## Setup and Requirements
Make sure you have uv installed, then install the project:
```bash
uv sync
```

## Scripts and Usage

### 1. League Analysis
```bash
uv run premier league-analysis <gameweek>
```
- Analyzes league data for a specific gameweek
- Generates CSV files in the database/league directory
- **Maps to Requirements: FRQ4 (Build a league-wide player summary)**
- **Maps to Requirements: FRQ6 (League player elimination based on participation)**

### 2. Participant Analysis
```bash
uv run premier participants <participant>
```
- Process participant data and generate player statistics
- Creates participant-specific output files
- **Maps to Requirements: FRQ1 (GET all players)**
- **Maps to Requirements: FRQ2 (GET all players from a participant)**
- **Maps to Requirements: FRQ3 (GET all players from all participants)**

### 3. Available Players
```bash
uv run premier available-players <gameweek>
```
- Generates a list of available players for selection
- Compiles data about player availability and attributes

### 4. Position Overview
```bash
uv run premier position-overview            # every participant in the config
uv run premier position-overview <entry_id> # a single participant
```
- Creates an overview of player positions across participants
- Shows distribution of goalkeepers, defenders, midfielders, and attackers
- **Maps to Requirements: FRQ7 (Participant position distribution overview)**

### 5. Participant Comparison
```bash
uv run premier participant-comparison <entry_id> <gameweek>
```
- Compares a specific participant's picks against the league
- Analyzes performance and selection patterns
- **Maps to Requirements: FRQ5 (Compare participants players with the other league players)**

### 6. Formation Overview
```bash
uv run premier formation-overview <entry_id>
uv run premier formation-overview --all
```
- For each gameweek, derives the participant's formation (e.g. `4-3-3`) from the starting XI and sums the starting XI points
- Benched players are excluded; captain points are doubled, consistent with Position Overview
- **Maps to Requirements: FRQ8 (Formation and points per round)**

### 7. Rank Per Round
```bash
uv run premier rank-per-round <rounds>                  # rounds 1..<rounds>, every participant
uv run premier rank-per-round 6 --start 6               # a single round
uv run premier rank-per-round 6 --participants <id> ... # only some participants
```
- For each round, reads the round total from `database/positions/<name>_positions.csv` and ranks participants by points (descending; ties share a rank)
- A participant's positions file is regenerated automatically if it is missing or does not contain the round yet
- **Maps to Requirements: FRQ9 (Rank participants per round)**

### 8. Captain Points
```bash
uv run premier captain-points                                # every participant, every gameweek
uv run premier captain-points --gameweeks 3 5                # only some gameweeks
uv run premier captain-points --participants <id> ...        # only some participants
```
- For each participant and gameweek, reports the captain, their base points, the multiplier and the points the captain generated
- If the captain did not play, the vice-captain who received the armband is used; a triple captain gameweek shows a multiplier of 3
- Output: `database/captains/captain_points.csv` (`captain_points_gw<N>.csv` when gameweeks are selected)
- **Maps to Requirements: FRQ10 (Captain points per participant)**

### 9. Player Analysis
```bash
uv run premier players
```
- Generates comprehensive player statistics and insights
- Provides data about individual player performance

### Refresh everything for a gameweek
```bash
./run.sh <gameweek>
```

## Requirements Mapping

### FRQ1: GET all players
- **Mapped to**: `participants` script (processes individual participant data)

### FRQ2: GET all players from a participant
- **Mapped to**: `participants` script (processes individual participant data)

### FRQ3: GET all players from all participants
- **Mapped to**: `participants` script (processes all participant data)

### FRQ4: Build a league-wide player summary
- **Mapped to**: `league-analysis` script (aggregates player data across all participants)
- **Output**: `database/league/league_gw_N.csv`

### FRQ5: Compare participant players with league players
- **Mapped to**: `participant-comparison` script (compares one participant against league data)
- **Output**: `database/comparisons/participant_name_gw_N.csv`

### FRQ6: League player elimination based on participation
- **Mapped to**: `available-players` script (league players removed from `players.csv`)
- **Output**: `database/available/available_gw_N.csv`

### FRQ7: Participant position distribution overview
- **Mapped to**: `position-overview` script (aggregates participant positions across gameweeks)
- **Output**: `database/positions/participant_name_positions.csv`

### FRQ8: Formation and points per round
- **Mapped to**: `formation-overview` script (counts starting XI players per position and sums points per gameweek)
- **Output**: `database/formations/participant_name_formations.csv` (`round,formation,totalPoints`)

### FRQ9: Rank participants per round
- **Mapped to**: `rank-per-round` script (ranks participants by their starting XI total per round)
- **Output**: `database/rank/gwN.csv` (`rank,participant,totalPoints`)

### FRQ10: Captain points per participant
- **Mapped to**: `captain-points` script (captain, base points, multiplier and resulting points per gameweek)
- **Output**: `database/captains/captain_points.csv` (`gameweek,participant,captain,captainBasePoints,multiplier,captainPoints`)

## Directory Structure
- `src/premier/` - Source code directory containing all Python scripts
- `config/` - Configuration files (`participants.toml`)
- `specs/` - Requirement descriptions
- `docs_requirements.md` - Functional requirements
- `../database/` - Generated CSV files (outside this repository):
  - `league/` - League analysis per gameweek
  - `participants/` - Participant-specific picks
  - `comparisons/` - Comparison result files
  - `available/` - Players not picked by anyone
  - `positions/` - Position distribution files
  - `formations/` - Formation and points per gameweek
  - `rank/` - Participant ranking per round (`gwN.csv`)
  - `captains/` - Captain points per participant and gameweek
