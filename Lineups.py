import statsapi
import datetime

def get_lineups(boxscore, opposing_team):

  if opposing_team == "away":
    lineup = [(batter['namefield'], batter['personId'], batter['ops']) for batter in boxscore['awayBatters']]
  else:
    lineup = [(batter['namefield'], batter['personId'], batter['ops']) for batter in boxscore['homeBatters']]

  return lineup