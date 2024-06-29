import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def insert_data(data):
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

    try:
        for game_date, games_info in data.items():
            for game_key, game_info in games_info.items():
                game_id = game_info['game_id']
                pitcher = game_info['pitcher']
                pRC = game_info['pRC']
                pitcher_ranking = game_info['ranking']

                # Insert data into the games table with the new ranking field
                cur.execute(
                    sql.SQL("INSERT INTO games (game_id, game_date, pitcher, pRC, ranking) VALUES (%s, %s, %s, %s, %s, %s)"),
                    [game_key, game_id, game_date, pitcher, pRC, pitcher_ranking]
                )

                # Insert data into the batters table with batter_id and ranking
                for batter_info in game_info['batters']:
                    batter_id = batter_info['batter_id']
                    batter = batter_info['batter']
                    bRC = batter_info['bRC']
                    batter_ranking = batter_info['ranking']
                    run_scored = False  # Example value, adjust as needed
                    cur.execute(
                        sql.SQL("INSERT INTO batters (game_id, batter_id, batter, bRC, run_scored, date, ranking) VALUES (%s, %s, %s, %s, %s, %s, %s)"),
                        [game_key, batter_id, batter, bRC, run_scored, game_date, batter_ranking]
                    )

        # Commit the changes
        conn.commit()
        print("Data inserted successfully")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()
