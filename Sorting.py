def sort_batters(lineup):
  for i, batter in enumerate(lineup):
        name, personId, ops, xwoba = batter
        run_predictor = 0.75 * xwoba + 0.25 * ops
        lineup[i] = (name, personId, ops, xwoba, run_predictor)

  lineup = sorted(lineup, key=lambda x: x[4], reverse=True)

  return lineup
