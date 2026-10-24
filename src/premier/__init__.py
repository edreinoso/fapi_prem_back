"""Premier Fantasy League tools for fetching and analyzing FPL data."""

import argparse
import sys

from .paths import DATABASE_DIR
from .players import export_players
from .participants import export_picks, export_picks_range
from .league_analysis import export_league_players
from .participant_comparison import export_participant_comparison
from .available_players import export_available_players as export_available
from .position_overview import export_position_overview
from .captain_points import export_captain_points
from .formation_overview import export_formation_overview
from .rank_per_round import export_rank_per_round
from .config import load_config, get_participants, get_export_defaults, get_entry_id_to_name

__version__ = "0.1.0"


def main() -> None:
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Premier Fantasy League data export tools",
        prog="premier"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Players command
    players_parser = subparsers.add_parser(
        "players",
        help="Export all FPL players to CSV"
    )
    players_parser.add_argument(
        "-o", "--output",
        default=f"{DATABASE_DIR}/players.csv",
        help="Output CSV file path (default: ../database/players.csv)"
    )
    
    # Participants command
    participants_parser = subparsers.add_parser(
        "participants",
        help="Export team picks for given gameweek(s) to CSV"
    )
    participants_parser.add_argument(
        "entry_id",
        type=int,
        nargs="*",
        help="FPL entry ID(s) - can specify multiple or use --config"
    )
    participants_parser.add_argument(
        "--gameweek",
        type=int,
        default=None,
        help="Single gameweek number (optional; if not provided, uses range)"
    )
    participants_parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to TOML config file with participant list"
    )
    participants_parser.add_argument(
        "--gw-start",
        type=int,
        default=None,
        help="Starting gameweek for range (overrides config/code default)"
    )
    participants_parser.add_argument(
        "--gw-end",
        type=int,
        default=None,
        help="Ending gameweek for range (overrides config/code default)"
    )
    participants_parser.add_argument(
        "-d", "--directory",
        default=f"{DATABASE_DIR}/participants",
        help="Output directory (default: ../database/participants)"
    )
    
    # League analysis command
    league_parser = subparsers.add_parser(
        "league-analysis",
        help="Analyze league-wide player data for a gameweek"
    )
    league_parser.add_argument(
        "gameweek",
        type=int,
        help="Gameweek number to analyze"
    )
    league_parser.add_argument(
        "--config",
        type=str,
        default="config/participants.toml",
        help="Path to participants config file (default: config/participants.toml)"
    )
    league_parser.add_argument(
        "--participants-dir",
        default=f"{DATABASE_DIR}/participants",
        help="Directory containing participant picks (default: ../database/participants)"
    )
    league_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output CSV file path (auto-generated if not specified)"
    )
    
    # Participant comparison command
    comparison_parser = subparsers.add_parser(
        "participant-comparison",
        help="Compare a participant's picks with league-wide statistics"
    )
    comparison_parser.add_argument(
        "entry_id",
        type=int,
        help="FPL entry ID of participant to compare"
    )
    comparison_parser.add_argument(
        "gameweek",
        type=int,
        help="Gameweek number to compare"
    )
    comparison_parser.add_argument(
        "--config",
        type=str,
        default="config/participants.toml",
        help="Path to participants config file (default: config/participants.toml)"
    )
    comparison_parser.add_argument(
        "--participants-dir",
        default=f"{DATABASE_DIR}/participants",
        help="Directory containing participant picks (default: ../database/participants)"
    )
    comparison_parser.add_argument(
        "--league-dir",
        default=f"{DATABASE_DIR}/league",
        help="Directory containing league analysis (default: ../database/league)"
    )
    comparison_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output CSV file path (auto-generated if not specified)"
    )
    
    # Available players command
    available_parser = subparsers.add_parser(
        "available-players",
        help="Find players NOT selected by any league participant"
    )
    available_parser.add_argument(
        "gameweek",
        type=int,
        help="Gameweek number to analyze"
    )
    available_parser.add_argument(
        "--league-file",
        default=None,
        help="Path to league analysis CSV (auto-generated if not specified)"
    )
    available_parser.add_argument(
        "--players-file",
        default=f"{DATABASE_DIR}/players.csv",
        help="Path to all players CSV (default: ../database/players.csv)"
    )
    available_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output CSV file path (auto-generated if not specified)"
    )
    
    # Position overview command
    positions_parser = subparsers.add_parser(
        "position-overview",
        help="Aggregate starting XI points by position per gameweek (all participants by default)"
    )
    positions_parser.add_argument(
        "entry_id",
        type=int,
        nargs="?",
        default=None,
        help="FPL entry ID of a single participant (omit to process every participant in the config)"
    )
    positions_parser.add_argument(
        "--all",
        action="store_true",
        help="Process every participant in the config (default when no entry_id is given)"
    )
    positions_parser.add_argument(
        "--config",
        type=str,
        default="config/participants.toml",
        help="Path to participants config file (default: config/participants.toml)"
    )
    positions_parser.add_argument(
        "--participants-dir",
        default=f"{DATABASE_DIR}/participants",
        help="Directory containing participant picks (default: ../database/participants)"
    )
    positions_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output CSV file path (auto-generated if not specified; only valid with an entry_id)"
    )
    
    # Formation overview command
    formations_parser = subparsers.add_parser(
        "formation-overview",
        help="Formation (e.g. 4-3-3) and starting XI points of a participant per gameweek"
    )
    formations_parser.add_argument(
        "entry_id",
        type=int,
        nargs="?",
        default=None,
        help="FPL entry ID of participant (omit when using --all)"
    )
    formations_parser.add_argument(
        "--all",
        action="store_true",
        help="Generate the overview for every participant in the config"
    )
    formations_parser.add_argument(
        "--config",
        type=str,
        default="config/participants.toml",
        help="Path to participants config file (default: config/participants.toml)"
    )
    formations_parser.add_argument(
        "--participants-dir",
        default=f"{DATABASE_DIR}/participants",
        help="Directory containing participant picks (default: ../database/participants)"
    )
    formations_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output CSV file path (auto-generated if not specified; not valid with --all)"
    )
    
    # Rank per round command
    rank_parser = subparsers.add_parser(
        "rank-per-round",
        help="Rank participants by starting XI points for each round (rounds 1..N)"
    )
    rank_parser.add_argument(
        "rounds",
        type=int,
        help="Last round to process; every round from --start up to this one is ranked"
    )
    rank_parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="First round to process (default: 1; use the same value as rounds for a single round)"
    )
    rank_parser.add_argument(
        "--participants",
        type=int,
        nargs="+",
        default=None,
        metavar="ENTRY_ID",
        help="FPL entry ID(s) to include (default: every participant in the config)"
    )
    rank_parser.add_argument(
        "--config",
        type=str,
        default="config/participants.toml",
        help="Path to participants config file (default: config/participants.toml)"
    )
    rank_parser.add_argument(
        "--positions-dir",
        default=f"{DATABASE_DIR}/positions",
        help="Directory containing position overview CSVs (default: ../database/positions)"
    )
    rank_parser.add_argument(
        "--participants-dir",
        default=f"{DATABASE_DIR}/participants",
        help="Directory containing participant picks (default: ../database/participants)"
    )
    rank_parser.add_argument(
        "-d", "--directory",
        default=f"{DATABASE_DIR}/rank",
        help="Output directory (default: ../database/rank)"
    )
    
    # Captain points command
    captain_parser = subparsers.add_parser(
        "captain-points",
        help="Points generated by each participant's captain per gameweek"
    )
    captain_parser.add_argument(
        "--gameweeks",
        type=int,
        nargs="+",
        default=None,
        metavar="GW",
        help="Gameweek(s) to include (default: every gameweek with picks)"
    )
    captain_parser.add_argument(
        "--participants",
        type=int,
        nargs="+",
        default=None,
        metavar="ENTRY_ID",
        help="FPL entry ID(s) to include (default: every participant in the config)"
    )
    captain_parser.add_argument(
        "--config",
        type=str,
        default="config/participants.toml",
        help="Path to participants config file (default: config/participants.toml)"
    )
    captain_parser.add_argument(
        "--participants-dir",
        default=f"{DATABASE_DIR}/participants",
        help="Directory containing participant picks (default: ../database/participants)"
    )
    captain_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output CSV file path (default: ../database/captains/captain_points[_gwN].csv)"
    )
    
    args = parser.parse_args()
    
    if args.command == "players":
        count = export_players(args.output)
        print(f"✓ Wrote {count} players to {args.output}")
    elif args.command == "participants":
        # Determine entry IDs to process
        entry_ids = []
        id_to_name = {}  # entry_id -> participant_name mapping
        gw_start = args.gw_start
        gw_end = args.gw_end
        config = None
        
        if args.config:
            # Load from config file
            try:
                config = load_config(args.config)
                entry_ids = list(get_participants(config).keys())
                id_to_name = get_entry_id_to_name(config)
                # Use config defaults if CLI flags not provided
                if gw_start is None or gw_end is None:
                    defaults = get_export_defaults(config)
                    if gw_start is None:
                        gw_start = defaults["gw_start"]
                    if gw_end is None:
                        gw_end = defaults["gw_end"]
            except Exception as e:
                print(f"✗ Error loading config: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.entry_id:
            # Use CLI-provided entry IDs
            entry_ids = args.entry_id
        else:
            # No entry IDs provided
            print("✗ Either specify entry_id(s) or use --config", file=sys.stderr)
            participants_parser.print_help()
            sys.exit(1)
        
        # Process each entry
        total_picks = 0
        for entry_id in entry_ids:
            participant_name = id_to_name.get(entry_id) if id_to_name else None
            if args.gameweek is not None:
                # Single gameweek specified
                count = export_picks(entry_id, args.gameweek, args.directory, participant_name)
                dir_name = participant_name or entry_id
                print(f"  Wrote {count} picks to {args.directory}/{dir_name}/{args.gameweek}.csv")
                total_picks += count
            else:
                # Range mode (no output in loop since export_picks_range prints its own)
                count = export_picks_range(entry_id, gw_start, gw_end, args.directory, participant_name)
                total_picks += count
        
        print(f"\n✓ Total picks exported: {total_picks}")
    elif args.command == "league-analysis":
        try:
            count = export_league_players(
                args.gameweek,
                output_file=args.output,
                participants_dir=args.participants_dir,
                config_path=args.config,
            )
            output_path = args.output or f"{DATABASE_DIR}/league/league_gw_{args.gameweek}.csv"
            print(f"✓ Wrote {count} unique players to {output_path}")
        except Exception as e:
            print(f"✗ Error analyzing league: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "participant-comparison":
        try:
            count = export_participant_comparison(
                args.entry_id,
                args.gameweek,
                output_file=args.output,
                participants_dir=args.participants_dir,
                league_dir=args.league_dir,
                config_path=args.config,
            )
            output_path = args.output or f"{DATABASE_DIR}/comparisons/{get_entry_id_to_name(load_config(args.config)).get(args.entry_id)}_gw_{args.gameweek}.csv"
            print(f"✓ Wrote {count} players to {output_path}")
        except Exception as e:
            print(f"✗ Error comparing participant: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "available-players":
        try:
            league_file = args.league_file or f"{DATABASE_DIR}/league/league_gw_{args.gameweek}.csv"
            count = export_available(
                args.gameweek,
                league_file=league_file,
                players_file=args.players_file,
                output_file=args.output,
            )
            output_path = args.output or f"{DATABASE_DIR}/available/available_gw_{args.gameweek}.csv"
            print(f"✓ Wrote {count} available players to {output_path}")
        except Exception as e:
            print(f"✗ Error finding available players: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "position-overview":
        if args.all and args.entry_id is not None:
            print("✗ Specify either an entry_id or --all, not both", file=sys.stderr)
            sys.exit(1)
        run_all = args.entry_id is None
        if run_all and args.output:
            print("✗ --output can only be used together with an entry_id", file=sys.stderr)
            sys.exit(1)
        try:
            id_to_name = get_entry_id_to_name(load_config(args.config))
            entry_ids = list(id_to_name) if run_all else [args.entry_id]
            for entry_id in entry_ids:
                name = id_to_name.get(entry_id)
                output_path = args.output or f"{DATABASE_DIR}/positions/{name}_positions.csv"
                try:
                    count = export_position_overview(
                        entry_id,
                        output_file=output_path,
                        participants_dir=args.participants_dir,
                        config_path=args.config,
                    )
                except FileNotFoundError as e:
                    # When processing everyone, skip participants without exported picks
                    if not run_all:
                        raise
                    print(f"  Skipped {name}: {e}", file=sys.stderr)
                    continue
                print(f"✓ Wrote {count} gameweeks to {output_path}")
        except Exception as e:
            print(f"✗ Error building position overview: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "formation-overview":
        if args.all == (args.entry_id is not None):
            print("✗ Specify either an entry_id or --all", file=sys.stderr)
            sys.exit(1)
        if args.all and args.output:
            print("✗ --output cannot be used with --all", file=sys.stderr)
            sys.exit(1)
        try:
            id_to_name = get_entry_id_to_name(load_config(args.config))
            entry_ids = list(id_to_name) if args.all else [args.entry_id]
            for entry_id in entry_ids:
                name = id_to_name.get(entry_id)
                output_path = args.output or f"{DATABASE_DIR}/formations/{name}_formations.csv"
                try:
                    count = export_formation_overview(
                        entry_id,
                        output_file=output_path,
                        participants_dir=args.participants_dir,
                        config_path=args.config,
                    )
                except FileNotFoundError as e:
                    # With --all, skip participants without exported picks
                    if not args.all:
                        raise
                    print(f"  Skipped {name}: {e}", file=sys.stderr)
                    continue
                print(f"✓ Wrote {count} gameweeks to {output_path}")
        except Exception as e:
            print(f"✗ Error building formation overview: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "rank-per-round":
        if args.start < 1 or args.rounds < args.start:
            print("✗ rounds must be >= --start, and --start must be >= 1", file=sys.stderr)
            sys.exit(1)
        try:
            for round_number in range(args.start, args.rounds + 1):
                try:
                    output_path, count, skipped = export_rank_per_round(
                        round_number,
                        entry_ids=args.participants,
                        output_dir=args.directory,
                        positions_dir=args.positions_dir,
                        participants_dir=args.participants_dir,
                        config_path=args.config,
                    )
                except FileNotFoundError as e:
                    print(f"  Skipped round {round_number}: {e}", file=sys.stderr)
                    continue
                print(f"✓ Ranked {count} participants for round {round_number} -> {output_path}")
                if skipped:
                    print(f"  No data for round {round_number}: {', '.join(skipped)}", file=sys.stderr)
        except Exception as e:
            print(f"✗ Error ranking rounds: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "captain-points":
        try:
            output_path, count, skipped = export_captain_points(
                entry_ids=args.participants,
                gameweeks=args.gameweeks,
                output_file=args.output,
                participants_dir=args.participants_dir,
                config_path=args.config,
            )
            print(f"✓ Wrote {count} captain rows to {output_path}")
            for note in skipped:
                print(f"  Skipped {note}", file=sys.stderr)
        except Exception as e:
            print(f"✗ Error building captain points: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Show help if no command specified
        parser.print_help()
        sys.exit(0)
