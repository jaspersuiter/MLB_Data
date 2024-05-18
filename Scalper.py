import statsapi
import datetime
from datetime import timedelta
import math
from Lineups import get_lineups
from Sorting import sort_batters
from pybaseball import statcast_batter
from pybaseball import playerid_lookup

# Get today's date
today = datetime.date.today().strftime('%Y-%m-%d')
now = datetime.datetime.now()

# Get the schedule for today's date
games = statsapi.schedule(date=today)

# List to store the details of each pitcher
pitchers = []

# Loop through the games
print(f"\033[1m\033[34mGames for: {datetime.date.today().strftime('%x')} starting after {now.strftime('%I:%M %p')}  \033[0m")
for game in games:
    
    game_datetime = datetime.datetime.fromisoformat(game['game_datetime'].rstrip('Z'))
    game_datetime -= timedelta(hours=4)
    formatted_game_datetime = game_datetime.strftime('%Y%m%d_%H%M%S')

    if formatted_game_datetime < now.strftime('%Y%m%d_%H%M%S'):
        continue
    
    
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
    if home_pitcher_games >= math.floor(.15 * total_games):
      pitchers.append((home_pitcher_name, home_pitcher_era, home_team, away_team, "away", game['game_id']))

    # Add the details of the away pitcher to the list
    if away_pitcher_games >= math.floor(.15 * total_games):
      pitchers.append((away_pitcher_name, away_pitcher_era, away_team, home_team, "home", game['game_id']))

    # Print the details
    print(f"{away_team} ({away_pitcher_name}, \033[32mERA: {away_pitcher_era}\033[0m) @ {home_team} ({home_pitcher_name}, \033[32mERA: {home_pitcher_era}\033[0m)")

# Sort the list by ERA
pitchers.sort(key=lambda x: x[1])

# Print the pitchers with the lowest 5 ERAs
print("\n\033[1m\033[34mTop 5 Pitchers with the Lowest ERAs:\033[0m")
for i in range(5):
    try:
        opposing_team = pitchers[i][3]

        print(f"\033[1m\u001b[4m{i + 1}. {pitchers[i][0]}, {pitchers[i][2]} vs {opposing_team}, \033[32mERA: {pitchers[i][1]}\033[0m")

        # Get the lineup of the opposing team
        now = datetime.datetime.now()

        # Format the date and time as a string in the format YYYYMMDD_HHMMSS
        formatted_now = now.strftime('%Y%m%d_%H%M%S')
        boxscore = statsapi.boxscore_data(pitchers[i][5], now)
        batters = get_lineups(boxscore, pitchers[i][4])

        batters = sort_batters(batters)

        # Print the first 5 players with the lowest OPS
        for name, id, ops, xwOBA, run_coefficient in batters[:4]:
            print(f"    {name}, Run coefficient: \033[0;32m{run_coefficient}\033[0m, xwOBA: \033[0;31m{xwOBA}\033[0m, OPS: \033[1;31m{ops}\033[0m")
    except IndexError:
        break