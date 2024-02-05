import wayback
from src.util.Configuration import Configuration

def collect_article_date_from_wayback(config: Configuration):
    db = config.get_db()
    db_insert = config.get_db()

    DB_database = config.DB_database
    DATA_ARTICLE_TABLE = config.DATA_ARTICLE_TABLE

    cursor = db.get_cursor(dictionary=True)

    cursor.execute("""
    SELECT id, news_url FROM {DB_database}.{DATA_ARTICLE_TABLE} WHERE published_date_cleaned IS NULL OR published_date_cleaned = ''
    """.format(DB_database=DB_database,DATA_ARTICLE_TABLE=DATA_ARTICLE_TABLE))

    client = wayback.WaybackClient()
    for row in cursor:
        results = client.search(row["news_url"])
        try:
            record = next(results)
            ts = record.timestamp
            id = row["id"]
            statement = """
                UPDATE {DB_database}.{DATA_ARTICLE_TABLE} SET published_date2 = '{ts}' WHERE id = {id}
            """.format(DB_database=DB_database,DATA_ARTICLE_TABLE=DATA_ARTICLE_TABLE, ts=ts, id=id)
            db_insert.execute(statement)
        except Exception as e:
            print("Failed", row["id"],row["news_url"])
            pass

    cursor.close()
    db.disconnect()
    db_insert.disconnect()
