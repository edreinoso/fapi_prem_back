# FRQ4: Build League-wide Player List


## Problem Statement
Create a league-wide view of all players selected across all participants for a given gameweek, showing which participants selected each player and their gameweek points.

## Current State
* Individual participant picks are exported to `database/participants/[entry_id]/[gw].csv`
* Each file contains playerName, totalPoints (GW points), position, multiplier, isCaptain, isBenched, and stat fields
* We have a config file listing all 9 participants

## Proposed Solution

### New Module: `league_analysis.py`
Create a new module with the following functions:

**`analyze_gameweek(gameweek, participants_dir, config_path)`**
* Load all participants from config
* For each participant, read their picks CSV for the given gameweek
* Aggregate all players, tracking which participants selected them and their points
* Return aggregated data sorted by playerPointGw descending

**`export_league_players(gameweek, output_file, participants_dir, config_path)`**
* Call analyze_gameweek()
* Write CSV with columns: playerName, playerPointGw, participantIds
* participantIds should be comma-separated list of entry IDs who picked this player

### Output File Structure
* Location: `database/league/league_gw_[N].csv`
* Columns: playerName, playerPointGw, participantIds
* Sorted by playerPointGw descending

### CLI Integration
Add new subcommand:
```warp-runnable-command
premier league-analysis <gameweek> [--config CONFIG] [-d DIRECTORY]

```
### Example Output
```csv
playerName,playerPointGw,participantIds
Haaland,15,7571821;6385584;5253078
Rodri,12,7571821;6385584;5253078;5185269
Van Dijk,8,7571821;5253078

```
## Implementation Steps
1. Create league_analysis.py module
2. Implement analyze_gameweek() function
3. Implement export_league_players() function
4. Update **init**.py to add league-analysis subcommand
5. Test with sample gameweek
6. Commit changes

## Dependencies
* Existing: config module, participants CSV files
* New: pandas optional (for aggregation) or use dict-based approach

## Success Criteria
* ✓ Can analyze any gameweek
* ✓ Output includes all players from all participants
* ✓ Players sorted by points descending
* ✓ Shows which participants selected each player
* ✓ Works with config file for participant list
* ✓ CLI integration with proper error handling
