import statsapi
import datetime
import math
from Lineups import get_lineups

# Get today's date
today = datetime.date.today().strftime('%Y-%m-%d')

# Get the schedule for today's date
games = statsapi.schedule(date=today)

# List to store the details of each pitcher
pitchers = []
away_batters, home_batters = get_lineups()
# Loop through the games
print(f"\033[1m\033[34mGames for: {datetime.date.today().strftime('%x')} \033[0m")
for game in games:
    # Get the home team, away team, and their probable pitchers
    home_team = game['home_name']
    away_team = game['away_name']
    home_pitcher_name = game['home_probable_pitcher']
    away_pitcher_name = game['away_probable_pitcher']

    # Get the player ID of the home pitcher
    home_pitcher = statsapi.lookup_player(home_pitcher_name)[0]
    home_pitcher_id = home_pitcher['id']

    # Get the player ID of the away pitcher
    away_pitcher = statsapi.lookup_player(away_pitcher_name)[0]
    away_pitcher_id = away_pitcher['id']

    # Get the ERA of the home pitcher
    home_pitcher_stats = statsapi.player_stat_data(home_pitcher_id, group='[pitching]', type='season', sportId=1)
    home_pitcher_era = home_pitcher_stats['stats'][0]['stats']['era']
    home_pitcher_games = home_pitcher_stats['stats'][0]['stats']['gamesPlayed']

    # Get the ERA of the away pitcher
    away_pitcher_stats = statsapi.player_stat_data(away_pitcher_id, group='[pitching]', type='season', sportId=1)
    away_pitcher_era = away_pitcher_stats['stats'][0]['stats']['era']
    away_pitcher_games = away_pitcher_stats['stats'][0]['stats']['gamesPlayed']

    standings = statsapi.standings_data(season=2024)
    total_games = standings[201]['teams'][0]['w'] + standings[201]['teams'][0]['l']

    # Add the details of the home pitcher to the list
    if home_pitcher_games >= math.floor(.2 * total_games):
      pitchers.append((home_pitcher_name, home_pitcher_era, home_team, away_team))

    # Add the details of the away pitcher to the list
    if away_pitcher_games >= math.floor(.2 * total_games):
      pitchers.append((away_pitcher_name, away_pitcher_era, away_team, home_team))

    # Print the details
    print(f"{away_team} ({away_pitcher_name}, \033[32mERA: {away_pitcher_era}\033[0m) @ {home_team} ({home_pitcher_name}, \033[32mERA: {home_pitcher_era}\033[0m)")

# Sort the list by ERA
pitchers.sort(key=lambda x: x[1])

# Print the pitchers with the lowest 5 ERAs
print("\n\033[1m\033[34mTop 5 Pitchers with the Lowest ERAs:\033[0m")
for i in range(5):
    opposing_team = pitchers[i][3]

    print(f"\033[1m\u001b[4m{i + 1}. {pitchers[i][0]}, {pitchers[i][2]} vs {opposing_team}, \033[32mERA: {pitchers[i][1]}\033[0m")

     # Get the roster of the opposing team
    roster = statsapi.get('team_roster', {'teamId': statsapi.lookup_team(opposing_team)[0]['id']})

    # Initialize a list to store the player's name and OBP
    players_ops = []

    # Loop through the players in the roster
    for player in roster['roster']:
        # Get the player's name and ID
        player_name = player['person']['fullName']
        player_id = player['person']['id']

        # Get the player's stats
        player_stats = statsapi.player_stat_data(player_id, group='[hitting]', type='season', sportId=1)

        # Check if the player has any stats and has at least 15 at-bats and an 'obp' in their stats
        if player_stats['stats'] and player_stats['stats'][0]['stats'].get('atBats', 0) >= (3.1 * player_stats['stats'][0]['stats'].get('gamesPlayed', 0)) and 'ops' in player_stats['stats'][0]['stats']:
            # Get the player's OBP
            player_ops = player_stats['stats'][0]['stats']['ops']

            # Add the player's name and OBP to the list
            players_ops.append((player_name, player_ops))

    # Sort the list by OBP
    players_ops.sort(key=lambda x: x[1])

    # Print the first 5 players with the lowest OBP
    for player_name, player_ops in players_ops[:3]:
        print(f"    {player_name}, \033[0;31mOPS: {player_ops}\033[0m")