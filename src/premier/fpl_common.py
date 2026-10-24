import requests

BASE_URL = "https://fantasy.premierleague.com/api"

# Extra stat columns pulled straight from the API, same name in and out
STAT_FIELDS = [
    "minutes",
    "goals_scored",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "bonus",
    "form",
    "selected_by_percent",
    "expected_goals",
    "expected_assists",
    "expected_goal_involvements",
    "expected_goals_conceded",
]

# Position ordering for squad display: GK -> DEF -> MID -> FWD
POSITION_ORDER = {"Goalkeeper": 0, "Defender": 1, "Midfielder": 2, "Forward": 3}


def fetch_bootstrap():
    """Fetch the FPL bootstrap-static payload (players, teams, positions, etc.)."""
    return requests.get(f"{BASE_URL}/bootstrap-static/").json()


def build_teams(bootstrap):
    """team id -> team name (1 = Arsenal, ... 20 = Wolves, alphabetical)."""
    return {team["id"]: team["name"] for team in bootstrap["teams"]}


def build_positions(bootstrap):
    """element_type id -> position (1 = Goalkeeper, 2 = Defender, 3 = Midfielder, 4 = Forward)."""
    return {
        element_type["id"]: element_type["singular_name"]
        for element_type in bootstrap["element_types"]
    }


def build_players_by_id(bootstrap):
    """player id -> raw player dict, keyed for quick lookups (e.g. from picks)."""
    return {player["id"]: player for player in bootstrap["elements"]}


def get_all_players(bootstrap):
    """Get all players with formatted data (name, points, position, team, price, stats).
    
    Returns a list of dictionaries with player information ready for export.
    """
    teams = build_teams(bootstrap)
    positions = build_positions(bootstrap)
    players = bootstrap["elements"]
    
    formatted_players = []
    for player in players:
        formatted_players.append({
            "playerName": player["web_name"],
            "totalPoints": player["total_points"],
            "position": positions[player["element_type"]],
            "team": teams[player["team"]],
            "currentPrice": player["now_cost"] / 10,
            **{field: player.get(field) for field in STAT_FIELDS}
        })
    
    return formatted_players
