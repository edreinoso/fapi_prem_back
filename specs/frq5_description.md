# FRQ5: Compare Participant with League Players


## Problem Statement
Create a comparison view showing a participant's selected players alongside league-wide statistics, helping identify which players are unique picks vs. popular/unpopular selections.

## Current State
* Individual participant picks: `database/participants/[Name]/[gw].csv`
* League analysis: `database/league/league_gw_[N].csv` with aggregated player data
* Config file with participant name mappings

## Proposed Solution

### New Module: `participant_comparison.py`
Create functions to:

**`calculate_selected_percentage(player_name, total_participants, league_picks_file)`**
* Count occurrences of player in league
* Calculate percentage: (occurrences / total_participants) * 100

**`compare_participant_to_league(entry_id, gameweek, participants_dir, league_dir, config_path)`**
* Load participant's picks CSV
* Load league analysis CSV
* Merge data to include league stats
* Calculate selected percentage for each player
* Return formatted data

**`export_participant_comparison(entry_id, gameweek, output_file, participants_dir, league_dir, config_path)`**
* Call compare_participant_to_league()
* Write CSV with columns: playerName, playerPointGw, position, selectedPercentage, participantNames
* Sort by: isBenched (benched first) > position order > points descending

### Output File Structure
* Location: `database/comparisons/[Participant Name]_gw_[N].csv`
* Columns: playerName, playerPointGw, position, selectedPercentage, participantNames
* Sorted as specified

### CLI Integration
Add new subcommand:
```warp-runnable-command
premier participant-comparison <entry_id> <gameweek> [--config CONFIG] [-d DIRECTORY]

```
### Example Output
```csv
playerName,playerPointGw,position,selectedPercentage,participantNames
João Pedro,11,Midfielder,90.0,Edgardo;El Mono;Gian;Gordo Juan;Kirby;Luifer;Miguel;Sebastian;Zavarce
White,11,Defender,20.0,Bryan;Luifer
Mason,5,Defender,0.0,Edgardo
Unique Pick,8,Forward,10.0,Edgardo

```
## Implementation Steps
1. Create participant_comparison.py module
2. Implement calculate_selected_percentage() function
3. Implement compare_participant_to_league() function
4. Implement export_participant_comparison() function
5. Update **init**.py to add participant-comparison subcommand
6. Test with sample participant and gameweek
7. Commit changes

## Dependencies
* Existing: config module, participants CSV files, league analysis CSV
* Uses: pathlib, csv, collections

## Success Criteria
* ✓ Can compare any participant to league
* ✓ Shows all participant's picks with league stats
* ✓ Calculates selection percentage correctly
* ✓ Sorts by isBenched, then position, then points
* ✓ Works with config file for participant name lookup
* ✓ CLI integration with proper error handling
* ✓ Output in expected CSV format
