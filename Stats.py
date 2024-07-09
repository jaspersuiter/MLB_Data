import psycopg2
import statsapi
from psycopg2 import sql
import os
from dotenv import load_dotenv
from collections import defaultdict

date = "2024-07-08" # YYYY-MM-DD

from psycopg2.extensions import adapt, AsIs

def update_run_scored(conn, batter_ids):
    cur = conn.cursor()
    # Before update: Optionally, select and print rows to be updated for verification
    select_query = """
    SELECT batter_id, run_scored FROM batters
    WHERE batter_id = ANY(%s) AND date = %s
    """
    cur.execute(select_query, (batter_ids, date))
    print("Before update:", cur.fetchall())

    # Perform the update
    update_query = """
    UPDATE batters
    SET run_scored = TRUE
    WHERE batter_id = ANY(%s) AND date = %s
    """
    cur.execute(update_query, (batter_ids, date))
    conn.commit()  # Commit the transaction

    # Check the number of rows updated
    if cur.rowcount > 0:
        print(f"{cur.rowcount} rows were updated.")
    else:
        print("No rows were updated.")

    # After update: Optionally, select and print the updated rows for verification
    cur.execute(select_query, (batter_ids, date))
    print("After update:", cur.fetchall())

    cur.close()

def update_runs_init():
  load_dotenv()
  # Database connection parameters
  conn = psycopg2.connect(
    dbname="mlb_data",
    user="postgres",
    password=os.getenv("DB_PASSWORD"),
    host="mlbdata.c9aqq4kw2945.us-east-2.rds.amazonaws.com",
    port="5432"
  )

  print("Connected to the database")

  # Create a cursor
  cur = conn.cursor()

  query = sql.SQL("SELECT id, game_key, batter_id, batter FROM batters WHERE date = %s")
  cur.execute(query, [date])
  batters = cur.fetchall()
  cur.close()

  batters_by_game = defaultdict(list)
  for batter in batters:
    sql_id, game_key, batter_id, batter_info = batter
    batters_by_game[game_key].append((batter_id, batter_info))

  # Process each game
  scorerers = []
  for game_key, game_batters in batters_by_game.items():
      # Select the first 3 batters for the game
      selected_batters = game_batters[:3]
      
      boxscore = statsapi.boxscore_data(game_key[:-1])

      if (game_key[-1] == 'a'):
         for player in boxscore["awayBatters"][1:]:
          if int(player["r"]) > 0:
            scorerers.append(player["personId"])
      else:
        for player in boxscore["homeBatters"][1:]:
          if int(player["r"]) > 0:
            scorerers.append(player["personId"])

  print(scorerers)          

  update_run_scored(conn, scorerers)

update_runs_init()