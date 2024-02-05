import json, tweepy, requests
from src.util.RateLimitCounter import RateLimitCounter
from src.util.Configuration import Configuration

# Credits adapted from 
# https://github.com/TIMAN-group/covid19_misinformation/blob/master/data/extract_real_and_fake_tweets_coaid.py

def download_tweet_context(config : Configuration):

    # Parameters
    DB_database = config.DB_database
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    bearer_token = config.search_tweets_v2["bearer_token"]
    rate_sleep_time = config.rate_sleep_time
    rate_counter_limit = config.rate_counter_limit

    # Load Tools
    db = config.get_db()
    rateLimitCounter = RateLimitCounter(rate_sleep_time, rate_counter_limit)
    client = tweepy.Client(
        bearer_token = bearer_token, 
        return_type = requests.Response,
        wait_on_rate_limit=True)

    has_remaining = 1
    while(has_remaining>0):
        # cache
        already_stored = db.fetchall(f"SELECT tweet_id FROM {DB_database}.{DATA_TWEET_TABLE} WHERE status LIKE 'Reload'", dictionary=True)
        tweet_ids = [str(row["tweet_id"]) for row in already_stored]

        chunks = 100 # max 100

        ids = tweet_ids[:chunks]
        if len(ids) <= 0:
            print("Finished early")
            exit()
        tweets = client.get_tweets(ids=ids, 
        tweet_fields=[
            "attachments",
            "author_id",
            #"context_annotations",
            "created_at",
            #"entities",
            "geo",
            "id",
            "in_reply_to_user_id",
            "lang",
            #"possibly_sensitive",
            "public_metrics",
            "referenced_tweets",
            "source",
            "text",
            "withheld"
        ])

        insert_query = f"""
        UPDATE {DB_database}.`{DATA_TWEET_TABLE}`  """ + """
        SET status='{status}', content='{content}'
        WHERE tweet_id={tweet_id}"""

        verbose = False
        tweets_json = tweets.json()
        def clean(text):
            return text.replace("'", "").replace("\\", "").replace('"', '').replace("\n", "")

        if "data" in tweets_json:
            for tweet in tweets_json["data"]:
                tweet["text"] = clean(tweet["text"])
                if "context_annotations" in tweet:
                    for context_annotation in tweet["context_annotations"]:
                        if "description" in context_annotation:
                            context_annotation["description"] = ""
                args = {
                    'tweet_id':tweet["id"], 
                    'status':"True", 
                    'content':json.dumps(tweet).replace("'", "")
                }
                if verbose:print(insert_query.format(**args))
                db.execute(insert_query.format(**args))

        if "errors" in tweets_json:
            for tweet in tweets_json["errors"]:
                tweet_id = tweet["resource_id"]
                args = {
                    'tweet_id':tweet_id, 
                    'status':"False", 
                    'content':json.dumps({})
                }
                if verbose:print(insert_query.format(**args))
                db.execute(insert_query.format(**args))

        has_remaining = len(tweet_ids) - chunks
        print("Remaining", len(tweet_ids) - chunks)
        rateLimitCounter.count()
    db.disconnect()