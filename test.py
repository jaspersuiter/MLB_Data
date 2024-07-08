import statsapi

def get_lineups_if_null(lineup):
    words = lineup[0].split(" ")
    team_name = " ".join(words[:-1])  # This removes the last word, assuming "Batters" is always the last word
    team_id = statsapi.lookup_team(team_name)[0] 

    print(team_id)
    # URL for the last completed game

    print(statsapi.last_game(team_id))

    

get_lineups_if_null("Yankees")