import json
from src.util.Configuration import Configuration

def hard_etract_value(row, key):
    split = row["content"].split('": "')
    extract = False
    for val in split:
        if extract:
            extract = False
            split2 = val.split('", "')
            return split2[0].replace("\"}", " ")
        if key in val:
            extract = True
    return None

def load_created_at_from_tweet(config: Configuration):
    DB_database = config.DB_database
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    db = config.get_db()
    db2 = config.get_db()

    statement_insert = "UPDATE {DB_database}.{DATA_TWEET_TABLE} SET created_at = '{created_at}', text = '{text}', author_id = '{author_id}' WHERE tweet_id = '{tweet_id}'"

    cursor = db.get_cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {DB_database}.{DATA_TWEET_TABLE}")
    for row in cursor:
        row["content"] = row["content"]
        # Try loading json
        try:
            tweet = json.loads(row["content"])
            created_at = tweet["created_at"]
            author_id = tweet["author_id"]
            text = tweet["text"]
        except:
            # Fallback to hard extraction
            created_at = hard_etract_value(row, "\"created_at")
            if created_at is None:
                created_at = hard_etract_value(row, "created_at")
            author_id = hard_etract_value(row, "\"author_id")
            if author_id is None:
                author_id = hard_etract_value(row, "author_id")
            text = hard_etract_value(row, "\"text")
            if text is None:
                text = hard_etract_value(row, "text")
            if text is None or created_at is None or author_id is None:
                print("Failed:",row["tweet_id"],created_at, author_id, text)
                continue

        db2.execute(statement_insert.format(
            DB_database=DB_database,
            DATA_TWEET_TABLE=DATA_TWEET_TABLE,
            created_at=created_at,
            author_id=author_id,
            text=text,
            tweet_id=row["tweet_id"]
        ))
    db.disconnect()
    db2.disconnect()
