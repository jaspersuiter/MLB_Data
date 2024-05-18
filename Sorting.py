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
