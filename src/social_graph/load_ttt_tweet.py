import json, datetime
from src.util.Configuration import Configuration


def load_tweets(config: Configuration):
    DB_database = config.DB_database
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    statement_tweets = """
        SELECT * FROM {DB_database}.{DATA_TWEET_TABLE}
    """
    tweets = {}
    try:
        db = config.get_db()
        cursor = db.get_cursor(dictionary=True)
        cursor.execute(statement_tweets.format(DB_database=DB_database,DATA_TWEET_TABLE=DATA_TWEET_TABLE))
        for row in cursor:
            if row["created_at"] is None:
                try:
                    content = json.loads(row["content"])
                    if "created_at" not in content:
                        print("no created at date", row)
                        continue
                    tweets[row["tweet_id"]] = row
                except:
                    print("no created at date", row)
                    continue
            tweets[row["tweet_id"]] = row
    finally:
        cursor.close()
        db.disconnect()
    return tweets

def load_articles(config: Configuration):
    DB_database = config.DB_database
    DATA_ARTICLE_TABLE = config.DATA_ARTICLE_TABLE
    statement_articles = """
        SELECT * FROM {DB_database}.{DATA_ARTICLE_TABLE}
    """
    articles = {}
    try:
        db = config.get_db()
        cursor = db.get_cursor(dictionary=True)
        cursor.execute(statement_articles.format(DB_database=DB_database, DATA_ARTICLE_TABLE=DATA_ARTICLE_TABLE))
        for row in cursor:
            # Get cleaned date
            if row["published_date_cleaned"] is None: continue
            if type(row["published_date_cleaned"]) != datetime.datetime:
                try:
                    # Parse this format 2024-01-24 00:00:00
                    date = datetime.datetime.strptime(row["published_date_cleaned"], '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        date = datetime.datetime.strptime(row["published_date_cleaned"], '%Y-%m-%dT%H:%M:%S.%fZ')
                    except Exception as e:
                        article_id = row["id"]
                        print(f"Article {article_id} has no date", row)
                        pass
            else:
                date = row["date"]
            row["date_obj"] = date

            # Fallback Date on Article
            if row["date"] is not None and row["date"] != "":
                # Pares February 1, 2024
                row["date_obj2"] = datetime.datetime.strptime(row["date"].strip(), '%B %d, %Y')
            articles[row["id"]] = row
    finally:
        cursor.close()
        db.disconnect()
    return articles

def load_ttt_tweet(config: Configuration):
    DB_database = config.DB_database
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    db = config.get_db()
    articles = load_articles(config)
    tweets = load_tweets(config)

    statement_insert = "UPDATE {DB_database}.{DATA_TWEET_TABLE} SET ttt = '{ttt}' WHERE tweet_id = '{tweet_id}'"

    for tweet_id, tweet in tweets.items():
        article_id = int(tweet["article_id"])
        source_tweet_id = tweet["source_tweet_id"]
        # check if type of created at is datetime
        if type(tweet["created_at"]) != datetime.datetime:
            tweet_date = datetime.datetime.strptime(tweet['created_at'].strip(),'%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            tweet_date = tweet["created_at"]

        if source_tweet_id == 0:
            # main tweet
            ttt = 0
        elif article_id == 0:
            # reply tweet
            if source_tweet_id not in tweets: continue
            other_tweet = tweets[source_tweet_id]
            if type(other_tweet['created_at']) != datetime.datetime:
                other_created_at = datetime.datetime.strptime(other_tweet['created_at'].strip(),'%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                other_created_at = other_tweet["created_at"]
            ttt = (tweet_date - other_created_at).total_seconds()
        else:
            # normal article case
            if article_id not in articles: continue
            article = articles[article_id]
            other_created_at = article["date_obj"] # Fallback Date on Article
            ttt = (tweet_date - other_created_at).total_seconds()
            if ttt < 0 and "date_obj2" in article: # Fallback Date on Article
                other_created_at = article["date_obj2"]
                ttt = (tweet_date - other_created_at).total_seconds()

        db.execute(statement_insert.format(
            DB_database=DB_database,
            DATA_TWEET_TABLE=DATA_TWEET_TABLE,
            ttt=ttt,
            tweet_id=tweet_id
        ))
