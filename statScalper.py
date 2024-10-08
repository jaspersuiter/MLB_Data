import statsapi
import datetime
from datetime import timedelta
import math
from Lineups import get_lineups
from Sorting import sort_batters, sort_pitchers
from sqlConnector import insert_data
from Stats import update_runs_init

# Get today's date
today = "2024-06-29" # YYYY-MM-DD
now = datetime.datetime.now()

# Get the schedule for today's date
games = statsapi.schedule(date=today)

# List to store the details of each pitcher
pitchers = []

games_data = {today: {}}

# Loop through the games
print(f"\033[1m\033[34mGames for: {today}\033[0m")
for game in games:
    
    game_datetime = datetime.datetime.fromisoformat(game['game_datetime'].rstrip('Z'))
    game_datetime -= timedelta(hours=4)
    formatted_game_datetime = game_datetime.strftime('%Y%m%d_%H%M%S')
    
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
    if home_pitcher_stats['stats']:
      home_pitcher_era = home_pitcher_stats['stats'][0]['stats']['era']
      home_pitcher_games = home_pitcher_stats['stats'][0]['stats']['gamesPlayed']
    else:
      continue

    # Get the ERA of the away pitcher
    away_pitcher_stats = statsapi.player_stat_data(away_pitcher_id, group='[pitching]', type='season', sportId=1)
    away_pitcher_era = away_pitcher_stats['stats'][0]['stats']['era']
    away_pitcher_games = away_pitcher_stats['stats'][0]['stats']['gamesPlayed']

    standings = statsapi.standings_data(season=2024)
    total_games = standings[201]['teams'][0]['w'] + standings[201]['teams'][0]['l']

    # Add the details of the home pitcher to the list
    if home_pitcher_games >= math.floor(.15 * total_games):
      pitchers.append((home_pitcher_name, home_pitcher_era, home_team, away_team, "away", game['game_id'], home_pitcher_id))

    # Add the details of the away pitcher to the list
    if away_pitcher_games >= math.floor(.15 * total_games):
      pitchers.append((away_pitcher_name, away_pitcher_era, away_team, home_team, "home", game['game_id'], away_pitcher_id))

    # Print the details
    print(f"{away_team} ({away_pitcher_name}, \033[32mERA: {away_pitcher_era}\033[0m) @ {home_team} ({home_pitcher_name}, \033[32mERA: {home_pitcher_era}\033[0m) \033[1m\033[34m{game_datetime.strftime('%I:%M %p')}\033[0m")

# Sort the pitchers
pitchers = sort_pitchers(pitchers)

# Print the pitchers with the lowest 5 ERAs
print(f"\n\033[1m\033[34mAll matchups for the day: ({len(pitchers)})\033[0m")
for i in range(len(pitchers)):
    try:
        opposing_team = pitchers[i][3]

        print(f"\033[1m\u001b[4m{i + 1}. {pitchers[i][0]}, {pitchers[i][2]} vs {opposing_team}, \033[32mRC: {pitchers[i][7]}, ERA: {pitchers[i][1]}, xwOBA: {pitchers[i][8]}, SIERRA: {pitchers[i][9]}\033[0m")
        # Get the lineup of the opposing team
        now = datetime.datetime.now()

        # Format the date and time as a string in the format YYYYMMDD_HHMMSS
        formatted_now = now.strftime('%Y%m%d_%H%M%S')
        boxscore = statsapi.boxscore_data(pitchers[i][5], now)
        batters = get_lineups(boxscore, pitchers[i][4])
        batters = sort_batters(batters, pitchers[i][4])
        game_key = str(pitchers[i][5]) + pitchers[i][4][0]
        
        games_data[today][game_key] = {
           'game_id': pitchers[i][5],
           'pitcher': pitchers[i][0],
           'pRC': pitchers[i][7],
           'ranking': i + 1,
           'batters': []}

        # Print the first 3 players with the lowest run coefficients
        j = 1
        for name, id, ops, xwOBA, run_coefficient in batters[:3]:
            print(f"    {name}, Run coefficient: \033[0;32m{run_coefficient}\033[0m, xwOBA: \033[0;31m{xwOBA}\033[0m, OPS: \033[1;31m{ops}\033[0m")
            games_data[today][game_key]['batters'].append({
               'batter_id': id,
               'batter': name,
               'bRC': run_coefficient,
               'ranking': j,
            })
            j += 1   

    except IndexError:
        print("No more games today.")
        break
    
insert_data(games_data)
update_runs_init(today)