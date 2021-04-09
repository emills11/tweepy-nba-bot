import tweepy
import pandas as pd
from games import retrieve_games
from config import create_api
from datetime import datetime
import pytz
import time

def tweet_game_scores(api, date, last_games):
    # Retrieve DataFrame containing today's completed games
    games_today = retrieve_games(date)

    # Condition is true if the list of retrieved games is longer than last retrieved games, i.e. when new games have completed
    if len(games_today.index) > len(last_games.index):
        # Filter out games that have already had their scores tweeted
        new_games = games_today[~games_today.GAME_ID.isin(last_games.GAME_ID)]
        new_games.reset_index(inplace=True)
        # Iterate through new games starting with first one completed
        for index in reversed(new_games.index):
            current = new_games.iloc[index]
            # Format the message to be tweeted out
            # Example: "FINAL: The Charlotte Hornets (25-20) defeat the Miami Heat (23-22), 115-104"
            tweet = (f"FINAL: The {current['TEAM_NAME_A']} ({current['RECORD_A']}) defeat the {current['TEAM_NAME_B']} ({current['RECORD_B']}), "
                    f"{current['PTS_A']}-{current['PTS_B']}")
            # Use tweepy to tweet message
            api.update_status(tweet)
            print(tweet)
            time.sleep(5)

        # Update csv file with new games
        games_today.to_csv('games_today.csv', index=False)


def get_time_minutes(time):
    return int(time.hour) * 60 + int(time.minute)


def main():
    # Create Twitter api
    api = create_api()

    EST = pytz.timezone('US/Eastern')
    last_time = get_time_minutes(datetime.now(EST))
    date = datetime.today().strftime("%Y-%m-%d")

    # Main loop
    while True:
        current_time = get_time_minutes(datetime.now(EST))
        # If the time has changed past 4 AM, assume there are no more games today and reset csv/date
        if last_time < 240 <= current_time:
            print("Resetting daily games...")
            new = pd.DataFrame(columns=['GAME_ID', 'TEAM_ID_A', 'TEAM_NAME_A', 'RECORD_A', 'PTS_A', 'TEAM_ID_B', 'TEAM_NAME_B', 'RECORD_B', 'PTS_B'])
            new.to_csv('games_today.csv', index=False)
            date = datetime.today().strftime("%Y-%m-%d")

        last_games = pd.read_csv('games_today.csv', dtype=str)
        tweet_game_scores(api, date, last_games)
        print(f"{current_time}: Checking again in 5 minutes")
        last_time = current_time
        # Wait five minutes between checking games
        # NBA stats api only updates data ~30 minutes after game is done, still figuring out exact delay amount
        time.sleep(300)


if __name__ == "__main__":
    main()
