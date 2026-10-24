# FRQ6: Available Players (Not Selected by League)


## Problem Statement
Identify and list all FPL players who were NOT selected by any participant in the league for a given gameweek, showing their availability and potential value.

## Current State
* All players list: `database/players.csv` (created by FRQ1)
* League selections: `database/league/league_gw_[N].csv` (created by FRQ4)
* Both files have player data with points, position, and other stats

## Proposed Solution

### New Module: `available_players.py`
Create functions to:

**`get_league_players(league_file)`**
* Read league CSV and extract set of player names who were selected
* Return set of player names

**`get_all_players(players_file)`**
* Read players CSV and extract all player data
* Return list of player dicts

**`find_available_players(league_file, players_file)`**
* Get league players set
* Get all players list
* Filter: return players NOT in league set
* Include: playerName, playerPointGw, position, team

**`export_available_players(gameweek, league_file, players_file, output_file)`**
* Call find_available_players()
* Write CSV with columns: playerName, playerPointGw, position, team
* Sort by playerPointGw descending

### Output File Structure
* Location: `database/available/available_gw_[N].csv`
* Columns: playerName, playerPointGw, position, team
* Sorted by playerPointGw descending

### CLI Integration
Add new subcommand:
```warp-runnable-command
premier available-players <gameweek> [-d LEAGUE_DIR] [-p PLAYERS_FILE]

```
### Example Output
```csv
playerName,playerPointGw,position,team
Unpopular Player A,15,Midfielder,Arsenal
Niche Pick B,13,Defender,Chelsea
Available Gem,12,Forward,Liverpool

```
## Implementation Steps
1. Create available_players.py module
2. Implement get_league_players() function
3. Implement find_available_players() function
4. Implement export_available_players() function
5. Update **init**.py to add available-players subcommand
6. Test with sample gameweek
7. Commit changes

## Dependencies
* Existing: players.csv, league_gw_N.csv
* Uses: pathlib, csv, set operations

## Success Criteria
* ✓ Correctly identifies players NOT in league
* ✓ Includes all required fields (playerName, playerPointGw, position, team)
* ✓ Sorts by playerPointGw descending
* ✓ Works for any gameweek
* ✓ CLI integration with proper error handling
* ✓ Output in expected CSV format
