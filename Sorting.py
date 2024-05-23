from pybaseball import statcast_pitcher, statcast_batter
import statsapi
import os
import sys

def sort_batters(lineup):
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
            
            run_predictor = round((((runs/at_bats) * .60) + (0.75 * xwoba + 0.25 * ops) * .40), 3)
            
            lineup[i] = (name, personId, ops, xwoba, run_predictor)

    lineup = sorted(lineup, key=lambda x: x[4])

    return lineup

def sort_pitchers(pitchers):
    for i, pitcher in enumerate(pitchers):
        
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        woba = statcast_pitcher(start_dt='2024-01-01', end_dt='2024-12-31', player_id=pitcher[6])['estimated_woba_using_speedangle']
        sys.stdout.close()
        sys.stdout = original_stdout

        average_woba = round(woba.mean(), 3)

        run_predictor = round((0.60 * float(average_woba) + 0.40 * float(pitcher[1])), 3)
        
        new_pitcher = (pitcher[0], pitcher[1], pitcher[2], pitcher[3], pitcher[4], pitcher[5], pitcher[6], run_predictor)

        # Update the pitchers list with the new tuple
        pitchers[i] = new_pitcher

    pitchers = sorted(pitchers, key=lambda x: x[-1])
       # calculate SIERA here 6.145 - 16.986(SO/PA) + 11.434(BB/PA) - 1.858((GB-FB-PU)/PA) + 7.653((SO/PA)^2) +/- 6.664(((GB-FB-PU)/PA)^2) + 10.130(SO/PA)((GB-FB-PU)/PA) - 5.195(BB/PA)*((GB-FB-PU)/PA)
    return pitchers   