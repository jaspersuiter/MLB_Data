import psycopg2
import statsapi
from psycopg2 import sql
import os
from dotenv import load_dotenv
from collections import defaultdict

def connect_to_db():
    conn = psycopg2.connect(
    dbname="mlb_data",
    user="postgres",
    password=os.getenv("DB_PASSWORD"),
    host="mlbdata.c9aqq4kw2945.us-east-2.rds.amazonaws.com",
    port="5432" 
  )
    return conn

def update_all_time_averages(conn):
    cur = conn.cursor()

    try:
        # Calculate all-time averages
        cur.execute("""
           SELECT ROUND(AVG(first_5)::numeric, 2) AS all_time_first_5_avg,
            ROUND(AVG(second_5)::numeric, 2) AS all_time_second_5_avg,
            ROUND(AVG(third_5)::numeric, 2) AS all_time_third_5_avg,
            ROUND(AVG("First")::numeric, 2) AS all_time_first,
            ROUND(AVG("Second")::numeric, 2) AS all_time_second,
            ROUND(AVG(third)::numeric, 2) AS all_time_third,
            ROUND(AVG("Primary")::numeric, 2) AS all_time_primary,
            ROUND(AVG(overall)::numeric, 2) AS all_time_overall
           FROM stats
          """)
        all_time_averages = cur.fetchone()

        print(all_time_averages)

        # Update all-time averages in the stats table
        cur.execute("""
            UPDATE stats
            SET first_5 = %s,
                second_5 = %s,
                third_5 = %s,
                "First" = %s,
                "Second" = %s,
                third = %s,
                "Primary" = %s,
                overall = %s
            WHERE date = 'All Time'
        """, all_time_averages)
        
        conn.commit()
        print("All-time averages updated successfully!")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error: {e}")

    finally:
        cur.close()

def fetch_game_and_batters_data(conn, date):
    cur = conn.cursor()

    # SQL query to fetch game_key, pitcher, ranking from games table
    # and game_key, run_scored, ranking from batters table
    query = """
    SELECT g.game_key, g.pitcher, g.ranking, b.run_scored, b.ranking
    FROM games g
    JOIN batters b ON g.game_key = b.game_key
    WHERE b.date = %s
    """
    cur.execute(query, (date,))
    rows = cur.fetchall()
    cur.close()
    return rows

def update_run_scored(conn, batter_ids, date):
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

    update_stats(date)

def update_runs_init(date):
  load_dotenv()
  # Database connection parameters
  conn = connect_to_db()

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

  update_run_scored(conn, scorerers, date)

  conn.close()

def insert_averages(conn, averages, date):
    cur = conn.cursor()

     # Define the INSERT statement with placeholders for values including date
    insert_query = """
    INSERT INTO stats (date, first_5, second_5, third_5, "First", "Second", third, "Primary", overall)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Execute the INSERT statement with the provided data
    cur.execute(insert_query, (date,) + tuple(averages))
    conn.commit()
    conn.commit()

    cur.close()

def update_stats(date):
  conn = connect_to_db()

  averages = []
  first = 0
  second = 0
  third = 0
  first_5 = 0
  second_5 = 0
  third_5 = 0
  game_counter = set()
  
  # Fetch game and batters data for the specified date
  data = fetch_game_and_batters_data(conn, date)
  
  # Print or process the fetched data
  for row in data:
      game_key, pitcher, game_ranking, run_scored, batter_ranking = row
      print(f"Game Key: {game_key}, Pitcher: {pitcher}, Game Ranking: {game_ranking}")
      print(f"Run Scored: {run_scored}, Batter Ranking: {batter_ranking}")
      print("---")

       # Apply conditions and increment counters
      if game_ranking <= 5:
          if batter_ranking == 1 and not run_scored:
              first_5 += 1
          elif batter_ranking == 2 and not run_scored:
              second_5 += 1
          elif batter_ranking == 3 and not run_scored:
              third_5 += 1

      if batter_ranking == 1 and not run_scored:
          first += 1
      elif batter_ranking == 2 and not run_scored:
          second += 1
      elif batter_ranking == 3 and not run_scored:
          third += 1      

      game_counter.add(game_key)
  
  averages.append(round(first_5/5 * 100, 2))
  averages.append(round(second_5/5 * 100, 2))
  averages.append(round(third_5/5 * 100, 2))
  averages.append(round(first/len(game_counter) * 100, 2))
  averages.append(round(second/len(game_counter) * 100, 2))
  averages.append(round(third/len(game_counter) * 100, 2))
  averages.append(round((averages[0] + averages[1] + averages[2]) / 3, 2))
  averages.append(round((averages[3] + averages[4] + averages[5]) / 3, 2))

  insert_averages(conn, averages, date)
  update_all_time_averages(conn)

  conn.close()
