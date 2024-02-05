import os, tweepy
import numpy as np
from src.util.Configuration import Configuration

# Credits adapted from 
# https://github.com/TIMAN-group/covid19_misinformation/blob/master/data/extract_real_and_fake_tweets_coaid.py

def download_followers(config: Configuration):
    DB_database = config.DB_database
    DATA_USER_TABLE = config.DATA_USER_TABLE
    DATA_USER_RELATIONS = config.DATA_USER_RELATIONS
    twitter_v1_credential_file_path = config.twitter_v1_credential_file_path

    follower_limit = config.follower_limit

    with open(twitter_v1_credential_file_path, "r") as twitter_key_file:
        twitter_key = twitter_key_file.readline().split(",")

    db = config.get_db()
    auth = tweepy.OAuthHandler(twitter_key[0], twitter_key[1],twitter_key[2],twitter_key[3])
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Cache userIDs
    userIDs = db.fetchall(f"SELECT userID FROM {DB_database}.{DATA_USER_TABLE} WHERE status_followers = 0", dictionary=True)
    userIDs = [str(row["userID"]) for row in userIDs]

    remaining = len(userIDs)
    index = 0
    while(remaining>0):
        user_id = userIDs[index]

        try:
            follower_ids =[]
            for user in tweepy.Cursor(api.get_follower_ids, user_id=user_id, count=5000).items(follower_limit):
                follower_ids.append(user)


            userID = user_id
            chunk_insertion = 500
            checksum = 0
            for i in range(0,int((len(follower_ids)+chunk_insertion)/chunk_insertion)):
                follower_ids_chunk = follower_ids[i*chunk_insertion:(i+1)*chunk_insertion]
                values = np.full((len(follower_ids_chunk)), userID)
                values = ",".join(["(" + str(value[0]) + "," + str(value[1]) + ")" for value in np.stack((values, follower_ids_chunk)).transpose()])
                insert_query = f"INSERT IGNORE INTO {DB_database}.{DATA_USER_RELATIONS} (`userID`, `followerID`) VALUES {values};"
                if values != "" and values is not None:
                    print(insert_query)
                    db.execute(insert_query)
                checksum += len(follower_ids_chunk)
            db.execute(f"UPDATE {DB_database}.{DATA_USER_TABLE} SET status_followers=10 WHERE userID = {user_id} ")
        except Exception as e:
            print(e)
            db.execute(f"UPDATE {DB_database}.{DATA_USER_TABLE} SET status_followers=2 WHERE userID = {user_id} ")

        index+=1
        remaining = len(userIDs) - index
        print("Remaining", len(userIDs) - index)
    db.disconnect()