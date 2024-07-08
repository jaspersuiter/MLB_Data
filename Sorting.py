from pybaseball import statcast_pitcher, statcast_batter
from Lineups import get_lineups 
import statsapi
import os
import sys
import statsapi


def calculate_siera(so, pa, bb, gb, ao):

  strikeout_rate = so / pa
  walk_rate = bb / pa
  ground_ball_diff = gb - ao
  ground_ball_diff_rate = ground_ball_diff / pa

  siera = round(
      6.145  # Constant
      - 16.986 * strikeout_rate
      + 11.434 * walk_rate
      - 1.858 * ground_ball_diff_rate
      + 7.653 * (strikeout_rate**2)
      + 6.664 * (ground_ball_diff_rate**2)  # Ignore for basic calculation
      + 10.130 * strikeout_rate * ground_ball_diff_rate
      - 5.195 * walk_rate * ground_ball_diff_rate, 3
  )

  return siera


def get_lineups_if_null(lineup, opposing_team):
    words = lineup[0][0].split(" ")
    team_name = " ".join(words[:-1]) 
    team_id = statsapi.lookup_team(team_name)[0] 
 
    boxscore = statsapi.boxscore_data(statsapi.last_game(team_id['id']))
    batters = get_lineups(boxscore, opposing_team)

    return batters

def sort_batters(lineup, opposing_team):
    if len(lineup) < 2:
        lineup = get_lineups_if_null(lineup, opposing_team)
    for i, batter in enumerate(lineup):
        name, personId, ops, xwoba = batter
        if personId == 0:
            lineup[i] = (name, personId, ops, xwoba, 1.0)
        else:    
            try:
                ops = float(ops)
            except ValueError:
                ops = 0.0
            try:
                xwoba = float(xwoba)
            except ValueError:
                xwoba = 0.0

            runs = statsapi.player_stat_data(personId, group='[hitting]', type='season', sportId=1)['stats'][0]['stats']['runs']
            at_bats = statsapi.player_stat_data(personId, group='[hitting]', type='season', sportId=1)['stats'][0]['stats']['plateAppearances']
            
            run_coefficient = round((((runs/at_bats) * .60) + (0.75 * xwoba + 0.25 * ops) * .40), 3)
            
            lineup[i] = (name, personId, ops, xwoba, run_coefficient)

    lineup = sorted(lineup, key=lambda x: x[4])

    return lineup

def sort_pitchers(pitchers):
    for i, pitcher in enumerate(pitchers):
        
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        pitcher_stats = statcast_pitcher(start_dt='2024-01-01', end_dt='2024-12-31', player_id=pitcher[6])
        sys.stdout.close()
        sys.stdout = original_stdout

        pitchers_info = statsapi.player_stat_data(pitcher[6], group='pitching', type='season')['stats'][0]['stats']
        woba = pitcher_stats['estimated_woba_using_speedangle']
        average_woba = round(woba.mean(), 3)

        sierra_stats = {
        "so": pitchers_info['strikeOuts'],
        "pa": pitchers_info['atBats'],
        "bb": pitchers_info['baseOnBalls'],
        "gb": pitchers_info['groundOuts'],
        "ao": pitchers_info['airOuts']
        }
        sierra = calculate_siera(**sierra_stats)

        run_coefficient = round((0.40 * float(average_woba) + 0.60 * float(sierra)), 3)
        
        new_pitcher = (pitcher[0], pitcher[1], pitcher[2], pitcher[3], pitcher[4], pitcher[5], pitcher[6], run_coefficient, average_woba, sierra)
        
        # Update the pitchers list with the new tuple
        pitchers[i] = new_pitcher
    
    pitchers = sorted(pitchers, key=lambda x: x[7])
    return pitchers   

def pStat_Sort(pitchers):
    for i, pitcher in enumerate(pitchers):
        
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        pitcher_stats = statcast_pitcher(start_dt='2024-01-01', end_dt='2024-12-31', player_id=pitcher[6])
        sys.stdout.close()
        sys.stdout = original_stdout

        pitchers_info = statsapi.player_stat_data(pitcher[6], group='pitching', type='season')['stats'][0]['stats']
        woba = pitcher_stats['estimated_woba_using_speedangle']
        average_woba = round(woba.mean(), 3)

        sierra_stats = {
        "so": pitchers_info['strikeOuts'],
        "pa": pitchers_info['atBats'],
        "bb": pitchers_info['baseOnBalls'],
        "gb": pitchers_info['groundOuts'],
        "ao": pitchers_info['airOuts']
        }
        sierra = calculate_siera(**sierra_stats)

        run_predictor = round((0.40 * float(average_woba) + 0.60 * float(sierra)), 3)
        
        new_pitcher = (pitcher[0], pitcher[1], pitcher[2], pitcher[3], pitcher[4], pitcher[5], pitcher[6], run_predictor, average_woba, sierra)
      
        # Update the pitchers list with the new tuple
        pitchers[i] = new_pitcher

    return pitchers   
