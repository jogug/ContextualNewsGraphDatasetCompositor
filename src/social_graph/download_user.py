import json, tweepy, requests
from src.util.Configuration import Configuration
from src.util.RateLimitCounter import RateLimitCounter
from src.util.StringCleanUtil import clean_text_name

# Credits adapted from 
# https://github.com/TIMAN-group/covid19_misinformation/blob/master/data/extract_real_and_fake_tweets_coaid.py

def download_users (config : Configuration):
    Db_database = config.Db_database
    bearer_token = config.search_tweets_v2["bearer_token"]
    DATA_USER_TABLE = config.DATA_USER_TABLE
    rate_sleep_time = config.rate_sleep_time
    rate_counter_limit = config.rate_counter_limit

    db = config.get_db()
    rateLimitCounter = RateLimitCounter(rate_sleep_time, rate_counter_limit)
    client = tweepy.Client(
        bearer_token=bearer_token, 
        return_type = requests.Response,
        wait_on_rate_limit=True)

    remaining = 1
    while(remaining>0):
        # cache
        userIDs = db.fetchall(f"SELECT userID FROM {Db_database}.{DATA_USER_TABLE} WHERE status LIKE 'Reload'", dictionary=True)
        userIDs = [str(row["userID"]) for row in userIDs]

        chunks = 100 # max 100

        ids = userIDs[:chunks]
        if len(ids) <= 0:
            print("Finished early")
            exit()

        # ?client.get_users_followers
        users = client.get_users(
            ids=ids,
            user_fields=[
                "id",
                "created_at",
                "description",
                "entities",
                "location",
                "name",
                "pinned_tweet_id",
                "profile_image_url",
                "protected",
                "public_metrics",
                "url",
                "username",
                "verified",
                "withheld"
            ]
        )

        insert_query = """
            INSERT INTO {Db_database}.`{DATA_USER_TABLE}` (`userID`, `status`, `content`) VALUES ('{user_id}', '{status}', '{content}')
            ON DUPLICATE KEY UPDATE status=VALUE(status), content=VALUE(content);
        """

        verbose = True
        users_json = users.json()


        if "data" in users_json:
            for user in users_json["data"]:
                user["username"] = clean_text_name(user["username"])
                user["description"] = clean_text_name(user["description"])

                args = {
                    'DATA_USER_TABLE' : DATA_USER_TABLE,
                    'user_id':user["id"], 
                    'status':"True", 
                    'content':json.dumps(user).replace("'", "")
                }
                if verbose:print(insert_query.format(**args))
                db.execute(insert_query.format(**args))

        if "errors" in users_json:
            for tweet in users_json["errors"]:
                user_id = tweet["resource_id"]
                args = {
                    'Db_database' : Db_database,
                    'DATA_USER_TABLE' : DATA_USER_TABLE,
                    'user_id':user_id, 
                    'status':"False", 
                    'content':json.dumps({})
                }
                if verbose:print(insert_query.format(**args))
                db.execute(insert_query.format(**args))

        remaining = len(userIDs) - chunks
        print("Remaining", len(userIDs) - chunks)
        rateLimitCounter.count()