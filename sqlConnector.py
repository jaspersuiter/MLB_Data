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
        for game_date, game_info in data.items():
            game_id = game_info['game_id']
            pitcher = game_info['pitcher']
            pRC = game_info['pRC']

            # Insert data into the games table
            cur.execute(
                sql.SQL("INSERT INTO games (game_id, game_date, pitcher, pRC) VALUES (%s, %s, %s, %s)"),
                [game_id, game_date, pitcher, pRC]
            )

            # Insert data into the batters table
            for batter_info in game_info['batters']:
                batter = batter_info['batter']
                bRC = batter_info['bRC']
                run_scored = False  # Example value, adjust as needed
                cur.execute(
                    sql.SQL("INSERT INTO batters (game_id, batter, bRC, run_scored, date) VALUES (%s, %s, %s, %s, %s)"),
                    [game_id, batter, bRC, run_scored, game_date]
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
