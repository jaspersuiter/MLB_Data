import statsapi
import datetime

def get_lineups():

  def get_lineups_and_player_info(data, game_pk):
    away_batters = [(batter['namefield'], batter['personId'], batter['ops']) for batter in data['awayBatters']]
    home_batters = [(batter['namefield'], batter['personId'], batter['ops']) for batter in data['homeBatters']]

    return away_batters, home_batters
  
  # Get today's date
  today = datetime.date.today().strftime('%Y-%m-%d')

  now = datetime.datetime.now()

  # Format the date and time as a string in the format YYYYMMDD_HHMMSS
  formatted_now = now.strftime('%Y%m%d_%H%M%S')
  # Get the schedule for today's date
  games = statsapi.schedule(date=today)

  for game in games:
    boxscore = statsapi.boxscore_data(game['game_id'], formatted_now)
    away_batters, home_batters = get_lineups_and_player_info(boxscore, game['game_id'])

    print("\n\033[1m\033[34mAway Batters:\033[0m")
    for name, id, ops in away_batters:
        print(f"{id}, {name}, {ops}")

    print("\033[1m\033[34m\nHome Batters:\033[0m")
    for name, id, ops in home_batters:
        print(f"{id}, {name}, {ops}")

  return away_batters, home_batters