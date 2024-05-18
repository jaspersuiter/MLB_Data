import statsapi
import datetime
from pybaseball import statcast_batter
import os
import sys

def get_lineups(boxscore, opposing_team):
    if opposing_team == "away":
        lineup = [(batter['namefield'], batter['personId'], batter['ops']) for batter in boxscore['awayBatters']]
    else:
        lineup = [(batter['namefield'], batter['personId'], batter['ops']) for batter in boxscore['homeBatters']]

    for i, batter in enumerate(lineup[1:]):
        # Redirect standard output to a null device
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

        # Call statcast_batter with standard output redirected
        woba = statcast_batter(start_dt='2024-01-01', end_dt='2024-12-31', player_id=batter[1])['estimated_woba_using_speedangle']

        # Restore standard output
        sys.stdout.close()
        sys.stdout = original_stdout

        average_woba = round(woba.mean(), 3)
        lineup[i+1] = batter + (average_woba,)

    # Set the xwOBA for the first batter to always be 1.0
    first_batter = lineup[0]
    lineup[0] = first_batter + (100,)

    return lineup