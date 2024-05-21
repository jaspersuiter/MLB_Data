from pybaseball import statcast_pitcher
import statsapi

def sort_batters(lineup):
    for i, batter in enumerate(lineup):
        name, personId, ops, xwoba = batter
        try:
            ops = float(ops)
        except ValueError:
            ops = 0.0
        try:
            xwoba = float(xwoba)
        except ValueError:
            xwoba = 0.0
        run_predictor = round(0.75 * xwoba + 0.25 * ops, 3)
        lineup[i] = (name, personId, ops, xwoba, run_predictor)

    lineup = sorted(lineup, key=lambda x: x[4])

    return lineup

def sort_pitchers(pitchers):
    for pitcher in enumerate(pitchers):
        woba = statcast_pitcher(start_dt='2024-01-01', end_dt='2024-12-31', player_id=pitcher[1][6])['estimated_woba_using_speedangle']
        average_woba = round(woba.mean(), 3)
        print(average_woba)


        print(statsapi.player_stat_data(pitcher[1][6], group="[pitching]", type="season", sportId=1))

       # calculate SIERA here 6.145 - 16.986(SO/PA) + 11.434(BB/PA) - 1.858((GB-FB-PU)/PA) + 7.653((SO/PA)^2) +/- 6.664(((GB-FB-PU)/PA)^2) + 10.130(SO/PA)((GB-FB-PU)/PA) - 5.195(BB/PA)*((GB-FB-PU)/PA)