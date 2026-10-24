# Feature: Data Insights From Premier Fantasy Leagues

## ✅ FRQ1
**GET all players**
- Retrieve a list of all players in the league

## ✅ FRQ2
**GET all players from a participant**
- Retrieve a list of all players selected by a specific participant

## ✅ FRQ3
**GET all players from all participants**
- Retrieve a comprehensive list of all players selected across all participants

## ✅ FRQ4
**Build a league-wide player summary**

### Input
- Specific gameweek number

### Output
- List of all players in the league for the specified gameweek
- CSV output format:
  ```
  playerName, playerPointGw, participantNames
  ```

### Processing
- Iterate through each participant
- Apply initial sorting by `playerPointGw`
- Consider creating a separate output file for better organization

## ✅ FRQ5
**Compare participant players with league players**

### Input
- Username or user ID
- Gameweek number to compare

### Output
- CSV table with the following format:
  ```
  playerName, playerPointGw, position, isCaptain, isBenched, selectedPercentage, participantsNames
  ```

### Sorting Criteria
1. `isBenched` (ascending - benched players appear last)
2. `position` 
3. `playerPointGw` (descending)

### Processing Notes
- Calculate `selectedPercentage`: percentage of participants who selected this player
- Exclude the participant being evaluated from the comparison
- Include all other participants in the analysis

## ✅ FRQ6
**League player elimination based on participation**

### Input
- Two CSV files:
  - `./database/league/league_gw_N.csv` (players in the league)
  - `players.csv` (all available players)

### Processing
- Remove players who participated in the league from `players.csv`
- Calculate total points for remaining players

### Output
- New CSV file with format:
  ```
  playerName, playerPointGw, position, team
  ```

### Sorting Criteria
- `playerPointGw` (descending)

### Notes
- The scoring should consider matchday-specific points (`playerPointGw`) rather than total points
- The original `players.csv` file provides total points, while we want to focus on gameweek-specific scores

## ✅ FRQ7
**Participant position distribution overview**

### Input
- Participant ID

### Processing
- For each gameweek:
  - Aggregate positions for players in the starting XI (excluding bench players)
  - Count occurrences of each position type

### Output
- CSV file with format:
  ```
  gameweek,goalkeepers,defenders,midfielders,attackers
  ```

### Processing Details
- Use existing participant data from database
- Focus only on starting XI players (not benched players)

### Example Output
```
gameweek,goalkeepers,defenders,midfielders,attackers
1,1,4,4,1
2,1,5,3,1
...
```
## ✅ FRQ8
**Participant formation and points per round**

### Input
- Participant ID (or all participants)

### Processing
- For each gameweek (round) of the participant:
  - Take only the starting XI players (`isBenched` is false)
  - Count the number of players per outfield position (defenders, midfielders, forwards)
  - Build the formation as `defenders-midfielders-forwards` (e.g. `4-3-3`); the goalkeeper is not part of the formation
  - Sum the points of the starting XI players for that round (`totalPoints * multiplier`, so the captain's points are doubled)
- Implemented as its own module, separate from the position overview

### Output
- One CSV file per participant: `database/formations/{participant}_formations.csv`
- CSV output format:
  ```
  round,formation,totalPoints
  ```

### Example Output
```
round,formation,totalPoints
1,4-3-3,54
2,4-4-2,74
3,3-4-3,79
...
```

### Usage
```
uv run premier formation-overview <entry_id>
uv run premier formation-overview --all
```

### Notes
- Participants without exported picks are skipped when using `--all`

## ✅ FRQ9
**Participant ranking per round**

### Input
- Round number: every round from `--start` (default 1) up to the given round is processed
- List of participants (optional, defaults to all participants in the config)

### Processing
- Use the `database/positions/{participant}_positions.csv` files (FRQ7) as the data source
- For each round:
  - Go through each participant
  - Read the `total` column from the row for that round
  - Rank the participants by that total
- If a participant's positions file is missing or does not contain the round yet, regenerate it from the participant picks

### Output
- One CSV file per round: `database/rank/gw{N}.csv`
- CSV output format:
  ```
  rank,participant,totalPoints
  ```

### Sorting Criteria
1. `totalPoints` (descending)
2. `participant` (alphabetical, to break ties in the ordering)

### Example Output
```
rank,participant,totalPoints
1,Gian,63
2,Kirby,62
3,Luifer,60
...
```

### Usage
```
uv run premier rank-per-round 3
uv run premier rank-per-round 5 --start 5
uv run premier rank-per-round 3 --participants <entry_id> <entry_id>
```

### Notes
- Participants with equal points share the same rank (1, 2, 2, 4, ...)
- Participants with no data for a round are left out of that round's file and reported in the console
- Rounds with no data for any participant are skipped
